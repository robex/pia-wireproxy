import os

PIA_USER = os.environ["PIA_USER"]
PIA_PASS = os.environ["PIA_PASS"]
PIA_LOCS = os.environ["PIA_LOCS"].split(",")
PIA_PORT_START = int(os.environ["PIA_PORT_START"])
SOCKS_USER = os.environ["SOCKS_USER"]
SOCKS_PASS = os.environ["SOCKS_PASS"]
