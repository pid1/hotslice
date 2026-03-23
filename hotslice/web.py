"""FastAPI web interface for hotslice."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from hotslice.config import Config
from hotslice.parser import parse_deck
from hotslice.renderer import list_available_themes, render_deck

_TEMPLATES_DIR = Path(__file__).parent / "templates"

app = FastAPI(title="hotslice", description="Markdown to HTML slide decks")
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


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
    content = await file.read()
    markdown_text = content.decode("utf-8")

    config = Config(theme=theme)
    deck = parse_deck(markdown_text)

    # Apply frontmatter overrides
    if "theme" in deck.frontmatter:
        config.theme = deck.frontmatter["theme"]
    if "title" in deck.frontmatter:
        config.title = deck.frontmatter["title"]

    html = render_deck(deck, config)

    # Derive filename from upload name
    stem = Path(file.filename).stem if file.filename else "presentation"
    filename = f"{stem}.html"

    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def main(host: str = "0.0.0.0", port: int = 8000):
    """Run the web server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
