"""HTML rendering for hotslice decks."""

from __future__ import annotations

import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from hotslice.config import USER_CONFIG_DIR, Config
from hotslice.hljs_themes import get_hljs_theme_info
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


def _read_theme_meta(theme_dir: Path) -> dict:
    """Read theme.toml and return its contents as a dict."""
    toml_path = theme_dir / "theme.toml"
    if toml_path.is_file():
        with open(toml_path, "rb") as f:
            return tomllib.load(f)
    return {}


def list_available_themes(theme_dir: str | None = None) -> list[dict]:
    """List all available on-disk themes with their metadata.

    Returns a list of dicts with keys: name, display_name, description,
    hljs_theme, variant, type. Only includes themes that have a theme.css
    file on disk.
    """
    themes = []
    seen: set[str] = set()

    # On-disk themes
    search_dirs = []
    if theme_dir:
        search_dirs.append(Path(theme_dir))
    search_dirs.append(USER_CONFIG_DIR / "themes")
    search_dirs.append(_BUNDLED_THEMES_DIR)

    for base in search_dirs:
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and (entry / "theme.css").is_file() and entry.name not in seen:
                seen.add(entry.name)
                meta = _read_theme_meta(entry)
                colors = meta.get("colors", {})
                themes.append(
                    {
                        "name": entry.name,
                        "display_name": meta.get("name", entry.name),
                        "description": meta.get("description", ""),
                        "hljs_theme": meta.get("hljs_theme", "github-dark"),
                        "variant": meta.get(
                            "variant",
                            "light" if "light" in entry.name else "dark",
                        ),
                        "type": "builtin",
                        "colors": {
                            "slide_bg": colors.get("slide_bg", "#ffffff"),
                            "slide_fg": colors.get("slide_fg", "#111111"),
                            "accent": colors.get("accent", "#4f46e5"),
                            "code_bg": colors.get("code_bg", "#f3f4f6"),
                            "code_fg": colors.get("code_fg", "#1f2937"),
                        },
                    }
                )

    return sorted(themes, key=lambda t: t["display_name"].lower())


def render_deck(deck: DeckData, config: Config) -> str:
    """Render a DeckData object to a complete HTML string."""
    # Try on-disk theme first (covers generated hljs themes and custom themes)
    try:
        theme_dir = _resolve_theme_dir(config.theme, config.theme_dir)
        meta = _read_theme_meta(theme_dir)
        hljs_theme = meta.get("hljs_theme", "github-dark")
    except FileNotFoundError:
        # Fall back to hljs slug -> pizza base theme mapping
        hljs_info = get_hljs_theme_info(config.theme)
        if hljs_info:
            base = "pizza-dark" if hljs_info["variant"] == "dark" else "pizza-light"
            theme_dir = _resolve_theme_dir(base, config.theme_dir)
            hljs_theme = config.theme
        else:
            raise FileNotFoundError(
                f"Theme '{config.theme}' not found on disk and is not a known highlight.js theme."
            ) from None

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
        hljs_theme=hljs_theme,
    )


def write_deck(html: str, output_path: str) -> Path:
    """Write the rendered HTML to the output file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
