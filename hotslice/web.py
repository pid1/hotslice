"""FastAPI web interface for hotslice."""

from __future__ import annotations

import contextlib
import re
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.types import ASGIApp, Receive, Scope, Send

from hotslice.config import Config
from hotslice.mcp_server import mcp as mcp_server
from hotslice.parser import parse_deck
from hotslice.renderer import list_available_themes, render_deck

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB
_THEME_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
_ALLOWED_EXTENSIONS = {".md", ".markdown", ".txt"}


@contextlib.asynccontextmanager
async def _lifespan(app: FastAPI):
    async with mcp_server.session_manager.run():
        yield


app = FastAPI(
    title="hotslice",
    description="Markdown to HTML slide decks",
    lifespan=_lifespan,
)
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def _validate_theme(name: str) -> None:
    """Raise HTTPException if the theme name contains unsafe characters."""
    if not _THEME_NAME_RE.match(name):
        raise HTTPException(
            status_code=400,
            detail="Invalid theme name. Use only letters, digits, hyphens, and underscores.",
        )


def _safe_stem(filename: str | None) -> str:
    """Extract a safe filename stem from an upload filename."""
    if not filename:
        return "presentation"
    # Use only the final path component, then take its stem
    name = Path(filename).name
    stem = Path(name).stem
    # Replace anything that is not alphanumeric, hyphen, underscore, or dot
    stem = re.sub(r"[^\w.-]", "_", stem)
    return stem or "presentation"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the upload form."""
    themes = list_available_themes()
    return templates.TemplateResponse(
        request=request,
        name="web.html.j2",
        context={"themes": themes},
    )


@app.get("/api/themes")
async def get_themes():
    """Return available themes as JSON."""
    return list_available_themes()


@app.post("/convert")
async def convert(
    file: UploadFile,
    theme: str = Form("pizza-light"),
):
    """Convert uploaded markdown to HTML and return as download."""
    # Validate theme name (blocks path traversal)
    _validate_theme(theme)

    # Validate file extension
    if file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext and ext not in _ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only .md, .markdown, and .txt files are accepted.",
            )

    # Read with size limit
    content = await file.read()
    if len(content) > _MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {_MAX_UPLOAD_SIZE // 1024 // 1024} MB.",
        )

    # Decode with error handling
    try:
        markdown_text = content.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="File must be valid UTF-8 text.",
        )

    config = Config(theme=theme)
    deck = parse_deck(markdown_text)

    # Apply frontmatter overrides (re-validate theme if frontmatter changes it)
    if "theme" in deck.frontmatter:
        fm_theme = str(deck.frontmatter["theme"])
        if _THEME_NAME_RE.match(fm_theme):
            config.theme = fm_theme
    if "title" in deck.frontmatter:
        config.title = str(deck.frontmatter["title"])

    html = render_deck(deck, config)

    stem = _safe_stem(file.filename)
    filename = f"{stem}.html"

    return Response(
        content=html,
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


# MCP server for AI agent integration
app.mount("/mcp", mcp_server.streamable_http_app())


# ---------------------------------------------------------------------------
# Middleware: rewrite /mcp → /mcp/ internally so Starlette's Mount never
# issues a 307 trailing-slash redirect.  Behind an HTTPS reverse-proxy the
# redirect's Location header used http://, which caused 421 Misdirected
# Request.  Rewriting the path at the ASGI scope level eliminates the
# redirect entirely — no extra round-trip, no scheme mismatch.
#
# This is a raw ASGI middleware (not BaseHTTPMiddleware) so it doesn't
# interfere with MCP Streamable HTTP's streaming responses.
# ---------------------------------------------------------------------------
class _MCPPathRewrite:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["path"] == "/mcp":
            scope = dict(scope, path="/mcp/")
        await self.app(scope, receive, send)


app.add_middleware(_MCPPathRewrite)


def main(host: str = "0.0.0.0", port: int = 8000):
    """Run the web server."""
    uvicorn.run(
        app,
        host=host,
        port=port,
        # Trust X-Forwarded-Proto / X-Forwarded-For from reverse proxies (Cloudflare
        # Tunnel, etc.) so Starlette's trailing-slash redirects use https:// instead of
        # http://.  Without this the /mcp → /mcp/ 307 redirect sends an http://
        # Location header, which fails with 421 Misdirected Request on the HTTPS edge.
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
