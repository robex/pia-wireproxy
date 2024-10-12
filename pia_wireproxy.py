import requests
import json
import subprocess
import os

from config import PIA_USER, PIA_PASS, PIA_LOCS, PIA_PORT_START, SOCKS_USER, SOCKS_PASS
from key import gen_wg_keys


def get_wg_regions():
    regions = {}
    serverlist_url = "https://serverlist.piaservers.net/vpninfo/servers/v6"

    r = requests.get(serverlist_url)
    r_no_cert = r.text.partition("\n")[0]
    server_list = json.loads(r_no_cert)

    for region in server_list["regions"]:
        if region["country"] not in regions:
            regions[region["country"]] = []

        if not region["offline"]:
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
        "Host": region["dns"]
    }

    r = requests.get(baseurl + endpoint, headers=headers, params=params, verify=False)
    return r.json()

def get_wg_config(region, token, socks_port):
    sk, pk = gen_wg_keys()

    j = get_wg_json(region, token, pk)

    wg_file_str = f"""
[Interface]
Address = {j["peer_ip"]}/32
PrivateKey = {sk}

[Peer]
PersistentKeepalive = 25
PublicKey = {j["server_key"]}
AllowedIPs = 0.0.0.0/0
Endpoint = {j["server_ip"]}:{j["server_port"]}

[Socks5]
BindAddress = 0.0.0.0:{socks_port}
Username = {SOCKS_USER}
Password = {SOCKS_PASS}
"""

    return wg_file_str

def get_pia_token():
    token_url = "https://www.privateinternetaccess.com/api/client/v2/token"

    data = {
        "username": PIA_USER,
        "password": PIA_PASS
    }

    r = requests.post(token_url, data=data)
    j = r.json()

    return j["token"]

def start_wireproxy_process(cfg_filename, port):
    p = subprocess.Popen(["./wireproxy", "--config", cfg_filename])
    return p

def start_wireproxy(region, token, socks_port):
    cfg_str = get_wg_config(region, token, socks_port)

    cfg_dir = "wg"
    if not os.path.exists(cfg_dir):
        os.makedirs(cfg_dir)

    cfg_filename = f"{cfg_dir}/{region['cn']}.conf"

    with open(cfg_filename, "w") as f:
        f.write(cfg_str)
        print(f"wrote config to {cfg_filename}")
    
    return start_wireproxy_process(cfg_filename, socks_port)

def main():
    regions = get_wg_regions()

    token = get_pia_token()

    server_candidate_locations = PIA_LOCS
    socks_port_start = PIA_PORT_START
    n_servers = len(PIA_LOCS)

    for i in range(0, n_servers):
        loc = server_candidate_locations[i]
        port = socks_port_start + i
        region = regions[loc][0]

        print(region, port)
        p = start_wireproxy(region, token, port)

    p.wait()

main()

