# Self-hosting hotslice

hotslice runs as a container behind a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
This document covers the whole path from a fresh NAS to `hotslice.pizza`
serving traffic.

## Why a tunnel and not a reverse proxy

A conventional nginx or Caddy setup means forwarding 80 and 443 from the router
to a machine that also holds your data, which publishes your home IP and
associates it permanently with the domain. `cloudflared` inverts that: the
connector dials **out** to Cloudflare and traffic returns down that connection.
There is no inbound firewall rule, no DDNS, no certificate to renew, and the
origin address never appears in DNS.

Caddy's ACME automation is genuinely good. It solves a problem this setup does
not have.

## Prerequisites

- A host running Docker, up continuously. An Unraid box is the assumed case.
- `hotslice.pizza` on Cloudflare DNS.
- A Cloudflare Zero Trust account. The free plan covers everything here.

## 1. Create the tunnel

In the Cloudflare dashboard, **Zero Trust → Networks → Tunnels**.

Either create a new tunnel or reuse an existing connector and add a hostname to
it. Reusing is fine and usually preferable: one connector can front any number
of services, and each additional hostname is a routing rule rather than another
daemon.

Under **Install and run a connector**, copy the tunnel token. It is a
credential — it authorizes anything to serve your hostname — so treat it like a
password.

## 2. Point the hostname at the container

On the tunnel's **Published application routes** tab, add:

| Field | Value |
| --- | --- |
| Subdomain | *(blank)* |
| Domain | `hotslice.pizza` |
| Service type | `HTTP` |
| URL | `hotslice:8000` |

`hotslice:8000` is the container name on the compose network, which is why the
compose file publishes no ports. Cloudflare creates the proxied DNS record for
you; if a record for the apex already exists pointing at Railway, this replaces
it.

Repeat with subdomain `www` if you want it.

## 3. Run the stack

```bash
git clone https://github.com/pid1/hotslice
cd hotslice
cp .env.example .env
# paste the tunnel token into .env
docker compose up -d --build
```

Then check both halves:

```bash
docker compose logs -f cloudflared   # want: "Registered tunnel connection"
curl -sf localhost:8000/api/themes   # from the host, only if you publish a port
curl -sI https://hotslice.pizza      # the real test
```

On Unraid, Community Applications has a `cloudflared` template if you would
rather not run compose; point it at the same token and run the hotslice
container on a shared custom Docker network so `hotslice:8000` resolves.

## 4. Harden the public surface

hotslice on the public internet is an unauthenticated endpoint that accepts
uploads and renders them. The container is already unprivileged, read-only,
capability-dropped and CPU-capped by `docker-compose.yml`. Three things are
worth adding at the edge, where they cost nothing:

**Cap the request body.** `web.py` reads the upload before checking it against
`_MAX_UPLOAD_SIZE`, so an oversized POST is buffered in full and only then
rejected. Cloudflare's free plan caps bodies at 100 MB, which bounds the damage
but well above the 2 MB hotslice actually accepts. A WAF rule rejecting
`http.request.body.size > 2097152` on `/convert` moves the rejection to the
edge, off the NAS.

**Rate-limit `/convert` and `/mcp`.** Both spend CPU per request. A rule of
roughly 10 requests per minute per IP is generous for real use and closes the
cheap flood.

**Decide about `/mcp`.** Public and unauthenticated, the MCP endpoint is free
compute for anyone who finds it. If it should stay open, rate-limiting is the
floor. If not, put a Cloudflare Access policy with a service token on that path
and leave the landing page open — also free, up to 50 users.

Optionally cache `/` at the edge. The landing page is static per deploy and
caching it means routine traffic never reaches the NAS at all.

## Rolling back

`docker compose down` stops the connector, and the hostname immediately returns
Cloudflare's origin-unreachable error rather than falling through to anything.
Deleting the hostname route removes the DNS record too.
