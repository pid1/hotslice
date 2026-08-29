# Self-hosting hotslice

hotslice is a small stateless web service, so it is cheap to run on hardware you
already own — a home server, a NAS, a spare box. This document covers putting it
on the public internet behind a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/),
which is free and does not require opening a port.

If you only want it on your LAN, skip to [Running the container](#running-the-container)
and stop there.

## Why a tunnel and not a reverse proxy

The conventional answer is nginx or Caddy plus a port forward. That means
forwarding 80 and 443 from your router to a machine that probably also holds
your data, which publishes your home IP address and ties it to a domain name
permanently.

`cloudflared` inverts the direction: the connector dials **out** to Cloudflare
and traffic returns down that connection. There is no inbound firewall rule, no
dynamic DNS, no certificate to renew, and the origin address never appears in
DNS.

Caddy's ACME automation is genuinely good. It solves a problem this setup does
not have.

## Prerequisites

- A host running Docker, up continuously.
- A Cloudflare account with Zero Trust enabled. The free plan covers all of this.
- A domain served by Cloudflare's nameservers — see below.

### The domain has to use Cloudflare DNS

This is the step people get stuck on. A tunnel's public hostname is a CNAME into
`cfargotunnel.com` that only Cloudflare can create, so the zone has to live on
Cloudflare. Registration does not: leave the domain registered wherever it is
and delegate only DNS.

1. Add the domain in the Cloudflare dashboard. It imports the existing records
   and assigns you two nameservers.
2. At your registrar, replace the current nameservers with those two. Every
   registrar words this differently — look for "custom DNS" or "nameservers"
   on the domain's settings page.
3. Wait for Cloudflare to mark the zone Active. Usually minutes, occasionally
   longer depending on the TLD.
4. Delete any imported record for the hostname you are about to use. If the
   domain previously pointed at a PaaS, that is typically an `ALIAS`/`CNAME` to
   the old provider, or an `A` record. The tunnel writes its own replacement.

Your registrar keeps billing and renewals. Only resolution moves.

## 1. Create the tunnel

In the Cloudflare dashboard, **Zero Trust → Networks → Tunnels**.

Create a tunnel, or add a hostname to a connector you already run. Reusing is
usually preferable: one connector can front any number of services, and each
additional hostname is a routing rule rather than another daemon.

Under **Install and run a connector**, copy the tunnel token. It authorizes
anything holding it to serve your hostname, so treat it like a password.

## 2. Point the hostname at the container

On the tunnel's published routes, add:

| Field | Value |
| --- | --- |
| Subdomain | *(blank, or `www`)* |
| Domain | your domain |
| Service type | `HTTP` |
| URL | `hotslice:8000` |

`hotslice:8000` is the container name on the shared Docker network, which is why
nothing below publishes a port. Cloudflare creates the proxied DNS record for
you.

## Running the container

The published image is `ghcr.io/pid1/hotslice:latest`, built from this repo by
`.github/workflows/container.yml` on every push to `main`. `docker build -t
hotslice .` works too.

### With compose

```bash
cp .env.example .env      # paste your tunnel token
docker compose up -d
```

### Without compose

Not every host has the compose plugin — stock Unraid, for one. The equivalent:

```bash
docker network create hotslice-net

docker run -d --name hotslice --restart unless-stopped \
  --network hotslice-net \
  --read-only --tmpfs /tmp:size=64m,mode=1777,noexec,nosuid,nodev \
  --security-opt no-new-privileges:true --cap-drop ALL \
  --cpus 1.0 --memory 512m \
  ghcr.io/pid1/hotslice:latest

docker run -d --name hotslice-cloudflared --restart unless-stopped \
  --network hotslice-net \
  --read-only --security-opt no-new-privileges:true --cap-drop ALL \
  -e TUNNEL_TOKEN=your-token-here \
  cloudflare/cloudflared:latest tunnel --no-autoupdate run
```

Drop the second container and add `-p 8000:8000` to the first for a LAN-only
install.

### A note for Unraid

Community Applications has a `CloudflaredTunnel` template that uses the same
official `cloudflare/cloudflared` image. Two of its defaults are worth changing
if you use it:

- It runs with `Network = host`, which lets the connector reach every service on
  the box. On a bridge network it can reach hotslice and nothing else, so a
  leaked token routes to one container rather than to your whole LAN.
- It passes the token as `--token <value>` in `PostArgs`, which puts a live
  credential into `docker inspect` and `ps` output. An `--env-file` keeps it in
  one file you control the permissions on.

Containers started with plain `docker run` show up in the Docker tab as orphans
that the UI cannot edit, and are lost if `docker.img` is ever recreated. To
manage them normally, drop a template in
`/boot/config/plugins/dockerMan/templates-user/` whose `<Name>` matches the
container, with the hardening flags in `<ExtraParams>`.

Check both halves:

```bash
docker logs -f hotslice-cloudflared   # want: "Registered tunnel connection"
curl -sI https://your-domain          # the real test
```

## Hardening a public instance

On the public internet hotslice is an unauthenticated endpoint that accepts
uploads and renders them. The container above is already unprivileged and
read-only, with all capabilities dropped and CPU and memory capped, so a flood
degrades hotslice rather than the host. Three things are worth adding at the
edge, where they cost nothing:

**Cap the request body.** `web.py` reads an upload before checking it against
`_MAX_UPLOAD_SIZE`, so an oversized POST is buffered in full and only then
rejected with a 413. Cloudflare's free plan caps bodies at 100 MB, far above the
2 MB hotslice accepts. A WAF rule rejecting `http.request.body.size > 2097152`
on `/convert` moves that rejection to the edge.

**Rate-limit `/convert` and `/mcp`.** Both spend CPU per request. Roughly 10
requests per minute per IP is generous for real use and closes the cheap flood.

**Decide about `/mcp`.** Public and unauthenticated, the MCP endpoint is free
compute for anyone who finds it. If it should stay open, rate-limiting is the
floor. If not, put a Cloudflare Access policy with a service token on that path
and leave the landing page open — also free.

Optionally cache `/` at the edge. The landing page is static per deploy, so
caching it means routine traffic never reaches your hardware at all.

## Verifying

The read-only root filesystem means `docker cp` into the container fails by
design, so pipe scripts in on stdin instead:

```bash
docker exec hotslice python -c "import urllib.request as u; \
  print(u.urlopen('http://127.0.0.1:8000/api/themes').status)"
```

A healthy instance answers `200` on `/` and `/api/themes` (257 themes), returns
rendered HTML from `POST /convert`, and rejects an oversized upload with `413`.

A plain `GET /mcp` answers `406`, which is correct — MCP Streamable HTTP expects
an SSE `Accept` header. What matters is that it is not a `307` or `421`; that is
what the `_MCPPathRewrite` middleware exists to prevent.

## Rolling back

`docker compose down`, or stopping the connector, makes the hostname return
Cloudflare's origin-unreachable error rather than falling through to anything
else. Deleting the hostname route removes the DNS record with it.
