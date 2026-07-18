import os

PIA_USER = os.environ["PIA_USER"]
PIA_PASS = os.environ["PIA_PASS"]
PIA_LOCS = os.environ["PIA_LOCS"].split(",")

PROXY_SOCKS_PORTS = [int(x) for x in os.environ["PROXY_SOCKS_PORTS"].split(",")]
PROXY_HTTP_PORTS = [int(x) for x in os.environ["PROXY_HTTP_PORTS"].split(",")]
PROXY_USER = os.environ["PROXY_USER"]
PROXY_PASS = os.environ["PROXY_PASS"]

HEALTH_PORTS = [int(x) for x in os.environ["HEALTH_PORTS"].split(",")]
HEALTH_SLEEP = int(os.environ["HEALTH_SLEEP"])
HEALTH_IP = os.environ["HEALTH_IP"]

WG_DIR = "/tmp/wg"
WIREPROXY_BIN = "/app/wireproxy"
CA_FILE = "/app/ca.rsa.4096.crt"

TOKEN_CACHE_FILE = "/data/token.json"
TOKEN_LIFETIME = 23 * 60 * 60
