import os

PIA_USER = os.environ["PIA_USER"]
PIA_PASS = os.environ["PIA_PASS"]

PIA_LOCS = os.environ["PIA_LOCS"].split(",")
PIA_SOCKS_PORTS = [int(x) for x in os.environ["PIA_SOCKS_PORTS"].split(",")]
PIA_HTTP_PORTS = [int(x) for x in os.environ["PIA_HTTP_PORTS"].split(",")]

PROXY_USER = os.environ["PROXY_USER"]
PROXY_PASS = os.environ["PROXY_PASS"]

HEALTH_PORT_START = int(os.environ["HEALTH_PORT_START"])
HEALTH_SLEEP = int(os.environ["HEALTH_SLEEP"])
HEALTH_IP = os.environ["HEALTH_IP"]
