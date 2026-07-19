import requests
import json
import subprocess
import os
import sys
import time
import signal
import threading

from pathlib import Path
from requests_toolbelt.adapters.host_header_ssl import HostHeaderSSLAdapter

import config
from key import gen_wg_keys

TOKEN_FILE = Path(config.TOKEN_CACHE_FILE)
servers = []
shutdown_event = threading.Event()

def get_wg_regions():
    print("retrieving pia region info")
    regions = {}
    serverlist_url = "https://serverlist.piaservers.net/vpninfo/servers/v6"

    r = requests.get(serverlist_url)
    r_no_cert = r.text.partition("\n")[0]
    server_list = json.loads(r_no_cert)

    for region in server_list["regions"]:
        if region["country"] not in regions:
            regions[region["country"]] = []

        if not region["offline"] and "wg" in region["servers"]:
            for ip in region["servers"]["wg"]:
                r = {
                    "ip": ip["ip"],
                    "cn": ip["cn"],
                    "dns": region["dns"]
                }
                regions[region["country"]].append(r)

    return regions

def get_wg_json(region, token, pk):
    baseurl = "https://" + region["ip"] + ":1337"
    endpoint = "/addKey"

    params = {
        "pt": token,
        "pubkey": pk
    }

    headers = {
        "Host": region["cn"]
    }

    # for proper certificate validation
    s = requests.Session()
    s.mount("https://", HostHeaderSSLAdapter())

    r = s.get(baseurl + endpoint, headers=headers, params=params, verify=config.CA_FILE)
    return r.json()

def get_wg_config(region, token, socks_port, http_port):
    sk, pk = gen_wg_keys()

    j = get_wg_json(region, token, pk)

    wg_file_str = f"""
[Interface]
Address = {j["peer_ip"]}/32
PrivateKey = {sk}
CheckAlive = {config.HEALTH_IP}
CheckAliveInterval = 25
DNS = 1.1.1.1

[Peer]
PersistentKeepalive = 25
PublicKey = {j["server_key"]}
AllowedIPs = 0.0.0.0/0
Endpoint = {j["server_ip"]}:{j["server_port"]}

[Socks5]
BindAddress = 0.0.0.0:{socks_port}
Username = {config.PROXY_USER}
Password = {config.PROXY_PASS}

[http]
BindAddress = 0.0.0.0:{http_port}
Username = {config.PROXY_USER}
Password = {config.PROXY_PASS}
"""

    return wg_file_str

def _get_pia_token():
    r = requests.post(
        "https://www.privateinternetaccess.com/api/client/v2/token",
        data={
            "username": config.PIA_USER,
            "password": config.PIA_PASS,
        },
    )
    r.raise_for_status()

    token = r.json()["token"]

    TOKEN_FILE.write_text(
        json.dumps({
            "token": token,
            "expires": time.time() + config.TOKEN_LIFETIME,
        })
    )

    return token

def get_pia_token(force_refresh=False):
    if not force_refresh and TOKEN_FILE.exists():
        try:
            cache = json.loads(TOKEN_FILE.read_text())
            if cache["expires"] > time.time():
                print("retrieving cached pia token")
                return cache["token"]
        except Exception:
            pass

    print("requesting new pia token")
    return _get_pia_token()

def start_wireproxy_process(cfg_filename, healthport):
    haddr = f"127.0.0.1:{healthport}"
    print(f"starting wireproxy server with config {cfg_filename}, health ip: {haddr}")
    p = subprocess.Popen([config.WIREPROXY_BIN, "--config", cfg_filename, "--info", haddr, "--silent"])
    return p

def start_wireproxy(token, s):
    cfg_str = get_wg_config(s["region"], token, s["socks_port"], s["http_port"])

    os.makedirs(config.WG_DIR, exist_ok=True)

    regname = s["region"]["cn"]
    cfg_filename = f"{config.WG_DIR}/{regname}.conf"

    with open(cfg_filename, "w") as f:
        f.write(cfg_str)
        print(f"wrote config to {cfg_filename}")

    return start_wireproxy_process(cfg_filename, s["healthport"])

def check_health(servers):
    # give time for wireproxy to start
    if shutdown_event.wait(config.HEALTH_SLEEP):
        return False

    while not shutdown_event.is_set():
        for srv in servers:
            url = f"http://127.0.0.1:{srv['healthport']}"
            endpoint = "/readyz"

            r = requests.get(url + endpoint)
            if r.status_code != 200:
                return False

            if shutdown_event.wait(config.HEALTH_SLEEP):
                return False

    return False

def shutdown(signum, frame):
    print(f"received signal {signal.Signals(signum).name}, shutting down...", flush=True)
    shutdown_event.set()

    for s in servers:
        if s["proc"].poll() is None:
            print(f"terminating wireproxy pid={s['proc'].pid}")
            s["proc"].terminate()

    for s in servers:
        s["proc"].wait()

    sys.exit(0)

def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    regions = get_wg_regions()

    force_refresh = False
    for i in range(0, 2):
        try:
            token = get_pia_token(force_refresh)
            break
        except requests.exceptions.HTTPError as e:
            print(f"error retrieving PIA token: {e}")
            force_refresh = True

    n_servers = len(config.PIA_LOCS)

    for i in range(0, n_servers):
        s = {
            "loc": config.PIA_LOCS[i],
            "socks_port": config.PROXY_SOCKS_PORTS[i],
            "http_port": config.PROXY_HTTP_PORTS[i],
            "healthport": config.HEALTH_PORTS[i],
            "region": regions[config.PIA_LOCS[i]][0],
        }

        s["proc"] = start_wireproxy(token, s)
        servers.append(s)

    if not check_health(servers):
        sys.exit(1)

main()

