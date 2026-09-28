# Deploying hotslice

The public instance at <https://hotslice.pid1.space> is a
[Python Worker](https://developers.cloudflare.com/workers/languages/python/)
on Cloudflare. The same FastAPI app that `hotslice serve` runs locally is served
through the Workers ASGI adapter, so there's no second implementation to keep in
sync. Nothing runs on hardware you own.

## Plan: Workers Paid, not Free

The Workers Free plan allows **10 ms of CPU per request**. hotslice doesn't fit
in that under Pyodide. Measured on the live Worker (September 2026, demo deck):

| Request                        | Warm CPU | Cold isolate |
| ------------------------------ | -------- | ------------ |
| `GET /`                        | 5–14 ms  | ~45 ms       |
| `POST /convert`                | 11–58 ms | 200–550 ms   |
| MCP `build_presentation`       | 22–58 ms | 230–780 ms   |
| `POST /convert` over the limit | ~11 ms   | —            |

On Free, nearly every conversion would fail with error 1102. The account needs
Workers Paid, where the default CPU limit is 30 s per request. Everything else
(requests, bundle size, memory) stays well inside the included limits.

Markdown parsing accounts for most of the warm cost, and it already runs as
little Python per request as it can (see
[What the runtime changes](#what-the-runtime-changes)). Fitting in 10 ms would
mean serving the conversion path from JavaScript instead of Python.

## Layout

```text
worker/
  pyproject.toml   # runtime deps only; pywrangler vendors these into the bundle
  wrangler.jsonc   # Worker config: route, data-file rules, build step
  build.sh         # the build step: copies the package in, writes build_id.py
  src/entry.py     # entrypoint: size check, then hands off to hotslice.web.app
  src/hotslice/    # copied from ../hotslice by build.sh (gitignored)
  src/themes/      # copied from ../themes by build.sh (gitignored)
  src/build_id.py  # commit served at /.build-id, written by build.sh (gitignored)
```

`worker/` is its own project because pywrangler vendors every dependency into
the bundle, and the root project depends on `uvicorn[standard]`, whose native
extensions have no WebAssembly build.

Wrangler doesn't follow symlinks, so `build.sh` (wrangler's `build.command`) copies
the package and themes in before every `dev` and `deploy`. Always edit the
top-level `hotslice/` and `themes/`, never the copies.

## Deploying

From a devenv shell:

```bash
worker-dev      # local workerd on http://localhost:8787
worker-deploy   # build, bundle, upload, and generate the memory snapshot
```

Both need Node (pywrangler shells out to `npx wrangler`). `worker-deploy` also
needs a logged-in `wrangler` (`uv run pywrangler login`) or the API token below.

### On push to main

Deploys follow the same two-layer pattern as the other `pid1.space` sites:

1. **Workers Builds** (primary). Cloudflare builds and deploys every push to
   `main`. Configure it under **Workers & Pages → hotslice → Settings → Build**:
   connect `pid1/hotslice`, branch `main`, root directory `/worker`, build
   command empty (`build.sh` runs inside the deploy), deploy command
   `uv run pywrangler deploy`.
2. **`.github/workflows/cf-fallback.yml`** (backup). Ten minutes after a push
   that touches `hotslice/`, `themes/`, or `worker/`, it reads
   `https://hotslice.pid1.space/.build-id`. If the live Worker isn't serving that
   commit, it deploys. It needs two repository secrets:
   - `CLOUDFLARE_ACCOUNT_ID`: `5c9482b9c0fe698b745e95011ac5ced4`
   - `CLOUDFLARE_API_TOKEN`: from the **Edit Cloudflare Workers** template,
     limited to this account and the `pid1.space` zone.

`/.build-id` comes from `git rev-parse HEAD` in `build.sh`, not from
`WORKERS_CI_COMMIT_SHA`, which Workers Builds sets to the branch name on manual
builds and would make the fallback redeploy every time.

## Routing

`wrangler.jsonc` attaches the Worker to `hotslice.pid1.space/*` with a **zone
route**. A route intercepts every request before the origin is contacted, so
all it needs is some proxied DNS record for the hostname.

Right now that record is the leftover CNAME to the deleted `nas` tunnel
(`f047a2ad-….cfargotunnel.com`). It is never reached, but it's misleading.
The cleaner end state is a custom domain, which owns its own record and
certificate, matching the other `*.pid1.space` Workers. Cloudflare refuses to
attach a custom domain while an externally managed record exists, and neither
the wrangler OAuth token nor the automation token used for the migration can
edit DNS. So this step is manual:

1. In the dashboard, delete the `hotslice` CNAME in the `pid1.space` zone. The
   site is down from here until step 3 finishes, usually well under a minute.
2. In `worker/wrangler.jsonc`, replace the route with
   `{ "pattern": "hotslice.pid1.space", "custom_domain": true }`.
3. `worker-deploy`.

## What the runtime changes

Python Workers run CPython on Pyodide (WebAssembly) inside workerd. A few
behaviors differ from a normal server, and the code is shaped around them.

**Import time is free; request time is metered.** At deploy, Cloudflare imports
the entrypoint and snapshots the interpreter's memory, and every cold start
restores that snapshot. Work at module level is paid once, at deploy. So
`web.py` scans the themes, serializes `/api/themes`, and renders the landing page
at import; `mcp_server.py` builds the theme list at import; the Jinja environment
and markdown parser are module-level. Scanning the themes alone takes about
15 ms natively, more than the whole Free-plan budget.

**No randomness at import.** Anything random in the snapshot would be shared by
every instance, so `os.urandom` raises during import. The MCP SDK's
`MCPServer()` generates its request-state key that way, so `mcp_server.py`
passes a codec that creates the key on first use instead.

**Lifespan runs per request, not per process.** The ASGI adapter runs a full
lifespan startup and shutdown around every request, and the MCP SDK's
`StreamableHTTPSessionManager.run()` works only once per instance. Rather than
start one manager from the app lifespan, `mcp_server.http_app` creates a
short-lived manager per request. The server is stateless, so nothing is lost.

**The body is read before the app runs.** The adapter buffers the whole
request body into Python before FastAPI sees it, so `web.py`'s 2 MB check comes
after the damage. `entry.py` rejects on `Content-Length` first, which turns a
multi-megabyte upload into an 11 ms 413.

**Only `.py` files are bundled by default.** The `rules` in `wrangler.jsonc`
ship templates, theme CSS/JS, and `theme.toml` as data modules. They appear
in the Worker's filesystem at their relative paths, so `renderer.py` reads them
unchanged.

## Hardening

On the public internet hotslice is an unauthenticated endpoint that renders
uploads. On Workers a flood costs requests and CPU time rather than degrading a
machine, but it still costs something. Both of these are free on the zone:

**Rate-limit `/convert` and `/mcp`.** Around 10 requests per minute per IP is
generous for real use.

**Decide about `/mcp`.** If it shouldn't be open to anyone, put a Cloudflare
Access policy with a service token on that path and leave the landing page
public.

## Verifying

```bash
B=https://hotslice.pid1.space
curl -s -o /dev/null -w "%{http_code}\n" $B/                 # 200
curl -s $B/api/themes | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))'   # 257
curl -s -o /dev/null -w "%{http_code}\n" -F file=@examples/demo.md $B/convert   # 200
curl -s -o /dev/null -w "%{http_code}\n" $B/mcp              # 405
```

A plain `GET /mcp` answers `405` by design: the server is stateless and has
nothing to stream, which the MCP spec allows servers to signal this way. An MCP
client talks to it with `POST`.

CPU time per request is in **Workers & Pages → hotslice → Observability**, or
queryable through the Workers observability API. Watch for the `exceededCpu`
outcome.

## Rolling back

```bash
cd worker && uv run pywrangler rollback   # previous version, instantly
```

`uv run pywrangler deployments list` shows what's available.
