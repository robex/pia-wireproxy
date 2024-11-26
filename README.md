# pia-wireproxy
Docker container that automatically creates a number of SOCKS5 proxies to PIA (privateinternetaccess) VPN Wireguard servers, via [Wireproxy](https://github.com/pufferffish/wireproxy).

**You will need a valid, paid PIA account.**

## Setup
Change the environment variables in `docker-compose.yml` to the appropriate values. The `PIA_LOCS` variable accepts a list of comma-separated ISO country codes for which there is a PIA WG server available. Selecting a particular location inside a country is not currently supported, though it is not particularly hard to implement.

You must **manually** adjust the number and range of ports in the `ports` section if you add more or less locations, and/or if you change the `PIA_START_PORT` variable.

Afterwards, just build the container and run it:

```
docker compose up -d
```

You can now, on the host or any machine that can see the host (assuming no firewalls), use the exposed proxies. Example to test if everything is working:

```
curl --proxy "socks5://socks:s0ck5@<host-ip>:26000" https://icanhazip.com
curl --proxy "socks5://socks:s0ck5@<host-ip>:26001" https://icanhazip.com
```

If you want to alter the config in any way, edit the `docker-compose.yml` file and recreate the container:

```
docker compose up -d --force-recreate
```
