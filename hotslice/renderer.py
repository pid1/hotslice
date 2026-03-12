"""HTML rendering for hotslice decks."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from hotslice.config import USER_CONFIG_DIR, Config
from hotslice.parser import DeckData

# Bundled themes directory (sibling to this package)
_PACKAGE_DIR = Path(__file__).parent
_BUNDLED_THEMES_DIR = _PACKAGE_DIR.parent / "themes"
_TEMPLATES_DIR = _PACKAGE_DIR / "templates"


def _resolve_theme_dir(theme_name: str, theme_dir: str | None) -> Path:
    """Resolve a theme name to its directory path.

    Search order:
    1. theme_dir argument (custom themes directory)
    2. User themes directory (~/.config/hotslice/themes/)
    3. Bundled themes directory
    4. Treat theme_name as an absolute/relative path
    """
    # Check custom theme directory first
    if theme_dir:
        custom = Path(theme_dir) / theme_name
        if custom.is_dir():
            return custom

    # Check user themes directory
    user_theme = USER_CONFIG_DIR / "themes" / theme_name
    if user_theme.is_dir():
        return user_theme

    # Check bundled themes
    bundled = _BUNDLED_THEMES_DIR / theme_name
    if bundled.is_dir():
        return bundled

    # Try as a direct path
    direct = Path(theme_name)
    if direct.is_dir():
        return direct

    raise FileNotFoundError(
        f"Theme '{theme_name}' not found. "
        f"Searched: {theme_dir or '(none)'}, {USER_CONFIG_DIR / 'themes'}, "
        f"{_BUNDLED_THEMES_DIR}, {theme_name}"
    )


def _read_file_or_empty(path: Path) -> str:
    """Read a file's contents, or return empty string if it doesn't exist."""
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def render_deck(deck: DeckData, config: Config) -> str:
    """Render a DeckData object to a complete HTML string."""
    theme_dir = _resolve_theme_dir(config.theme, config.theme_dir)

    theme_css = _read_file_or_empty(theme_dir / "theme.css")
    theme_js = _read_file_or_empty(theme_dir / "theme.js")

    title = config.title or deck.title or "Untitled Presentation"

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,  # We're generating HTML, slides contain raw HTML
    )
    template = env.get_template("deck.html.j2")

    return template.render(
        title=title,
        slides=deck.slides,
        theme_css=theme_css,
        theme_js=theme_js,
        metadata=config.metadata,
    )


def write_deck(html: str, output_path: str) -> Path:
    """Write the rendered HTML to the output file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
