"""Cloudflare Workers entrypoint: serves the hotslice FastAPI app."""

import json
import logging
from urllib.parse import urlsplit

from workers import Response, WorkerEntrypoint, asgi

from hotslice.web import _MAX_UPLOAD_SIZE, app

try:
    # Written by build.sh; absent only if something bypassed the build step.
    from build_id import BUILD_ID
except ImportError:
    BUILD_ID = "unknown"

# The MCP SDK logs session start/stop at INFO on every request, and the Workers
# runtime surfaces Python log records as errors. Keep warnings and up.
logging.getLogger("mcp").setLevel(logging.WARNING)

# Room for the multipart envelope around a maximum-size upload: boundaries,
# part headers, and the theme field.
_MAX_BODY_SIZE = _MAX_UPLOAD_SIZE + 64 * 1024


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # The commit this Worker was built from, for the cf-fallback workflow.
        # no-store so it always reflects the deployed Worker, never a cache.
        if request.method == "GET" and urlsplit(request.url).path == "/.build-id":
            return Response(
                BUILD_ID + "\n",
                headers={"Content-Type": "text/plain", "Cache-Control": "no-store"},
            )

        # The Workers ASGI adapter reads the entire body into Python before the
        # app sees the request, so web.py's own size check runs only after a
        # 100 MB upload has been buffered and parsed, long past the free
        # plan's 10 ms CPU limit. Reject on Content-Length first. Browsers and
        # MCP clients always send it; a chunked body without one falls
        # through to web.py's check.
        length = request.headers.get("content-length")
        if length and length.isdigit() and int(length) > _MAX_BODY_SIZE:
            limit_mb = _MAX_UPLOAD_SIZE // 1024 // 1024
            return Response(
                json.dumps({"detail": f"File too large. Maximum size is {limit_mb} MB."}),
                status=413,
                headers={"Content-Type": "application/json"},
            )
        return await asgi.fetch(app, request, self.env, self.ctx)
