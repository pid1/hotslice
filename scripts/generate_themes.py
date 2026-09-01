#!/usr/bin/env python3
"""Generate on-disk hotslice theme directories for all highlight.js themes.

Fetches each hljs CSS file from the CDN, extracts key colors (background,
foreground, keyword/accent), and writes theme.css + theme.toml into
themes/<slug>/.

Run from the repo root:
    python scripts/generate_themes.py
"""

from __future__ import annotations

import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add repo root to path so we can import hotslice
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from hotslice.hljs_themes import HLJS_THEMES  # noqa: E402

THEMES_DIR = REPO_ROOT / "themes"
CDN_BASE = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles"
MAX_WORKERS = 20

# Default colors by variant when extraction fails
DEFAULTS = {
    "dark": {
        "slide_bg": "#1a1a2e",
        "slide_fg": "#e0e0e0",
        "accent": "#7c3aed",
        "code_bg": "#1a1a2e",
        "code_fg": "#e0e0e0",
    },
    "light": {
        "slide_bg": "#ffffff",
        "slide_fg": "#1a1a2e",
        "accent": "#4f46e5",
        "code_bg": "#ffffff",
        "code_fg": "#1a1a2e",
    },
}

# Common CSS named colors mapped to hex
NAMED_COLORS: dict[str, str] = {
    "white": "#ffffff",
    "black": "#000000",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "orange": "#ffa500",
    "purple": "#800080",
    "gray": "#808080",
    "grey": "#808080",
    "silver": "#c0c0c0",
    "navy": "#000080",
    "teal": "#008080",
    "maroon": "#800000",
    "olive": "#808000",
    "aqua": "#00ffff",
    "fuchsia": "#ff00ff",
    "lime": "#00ff00",
}

# Kept in the exact shape prettier produces, so the generated files pass the
# CSS_PRETTIER lint without a formatting pass after generation. If you edit
# this, run prettier over themes/ and make the template match the result.
THEME_CSS_TEMPLATE = """\
/* hotslice {slug} theme (auto-generated from highlight.js) */

:root {{
  --slide-bg: {slide_bg};
  --slide-fg: {slide_fg};
  --accent: {accent};
  --code-bg: {code_bg};
  --code-fg: {code_fg};
  --font-mono: "Atkinson Hyperlegible Mono", monospace;
}}

html,
body {{
  background: var(--slide-bg);
}}

.slide h2 {{
  color: var(--accent);
}}
.slide h3 {{
  color: var(--accent);
  opacity: 0.85;
}}

.slide pre {{
  background: var(--code-bg);
  border: 1px solid color-mix(in srgb, var(--slide-fg) 15%, transparent);
  border-radius: 8px;
}}

.slide blockquote {{
  border-left: 4px solid var(--accent);
}}

.slide a {{
  color: var(--accent);
}}
.slide th {{
  color: var(--accent);
}}
.slide li::marker {{
  color: var(--accent);
}}

#progress-bar {{
  background: var(--accent);
}}
"""

THEME_TOML_TEMPLATE = """\
name = "{display_name}"
description = "{display_name} theme (generated from highlight.js)"
author = "hotslice (generated)"
hljs_theme = "{slug}"
variant = "{variant}"

[colors]
slide_bg = "{slide_bg}"
slide_fg = "{slide_fg}"
accent = "{accent}"
code_bg = "{code_bg}"
code_fg = "{code_fg}"
"""


def normalize_color(value: str) -> str:
    """Normalize a CSS color value to hex or pass through rgb()/rgba()."""
    value = value.strip().lower()

    # Named color
    if value in NAMED_COLORS:
        return NAMED_COLORS[value]

    # Already hex
    if value.startswith("#"):
        return value

    # rgb/rgba - convert to hex if possible
    rgb_match = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", value)
    if rgb_match:
        r, g, b = (
            int(rgb_match.group(1)),
            int(rgb_match.group(2)),
            int(rgb_match.group(3)),
        )
        return f"#{r:02x}{g:02x}{b:02x}"

    return value


def extract_colors(css_text: str, variant: str) -> dict[str, str]:
    """Extract slide_bg, slide_fg, accent from hljs CSS text."""
    defaults = DEFAULTS[variant]

    # Find the standalone .hljs { ... } block (not code.hljs or pre code.hljs).
    # Strip CSS comments first, then search for blocks with a background property.
    stripped_css = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    block_content = None
    for match in re.finditer(r"(?:^|[},;\s])\.hljs\s*\{([^}]+)\}", stripped_css):
        candidate = match.group(1)
        if re.search(r"background", candidate):
            block_content = candidate
            break

    if block_content is None:
        return dict(defaults)

    # Extract background color
    bg_match = re.search(r"background(?:-color)?\s*:\s*([^;}\s]+(?:\([^)]*\))?)", block_content)
    slide_bg = normalize_color(bg_match.group(1)) if bg_match else defaults["slide_bg"]

    # Extract text color (not background-color)
    fg_match = re.search(r"(?:^|;)\s*color\s*:\s*([^;}\s]+(?:\([^)]*\))?)", block_content)
    slide_fg = normalize_color(fg_match.group(1)) if fg_match else defaults["slide_fg"]

    # Find .hljs-keyword color for accent
    kw_block = re.search(r"\.hljs-keyword[^{]*\{([^}]+)\}", css_text)
    if kw_block:
        accent_match = re.search(r"color\s*:\s*([^;}\s]+(?:\([^)]*\))?)", kw_block.group(1))
        accent = normalize_color(accent_match.group(1)) if accent_match else defaults["accent"]
    else:
        accent = defaults["accent"]

    return {
        "slide_bg": slide_bg,
        "slide_fg": slide_fg,
        "accent": accent,
        "code_bg": slide_bg,
        "code_fg": slide_fg,
    }


def fetch_css(slug: str) -> str | None:
    """Fetch hljs CSS from CDN. Try primary URL, then base16 alternative."""
    urls = [f"{CDN_BASE}/{slug}.min.css"]

    # For base16 themes, also try the base16/ subdirectory
    if slug.startswith("base16-"):
        suffix = slug[len("base16-") :]
        urls.append(f"{CDN_BASE}/base16/{suffix}.min.css")

    for url in urls:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "hotslice-theme-generator/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8")
        except Exception:
            continue

    return None


def is_manually_authored(theme_dir: Path) -> bool:
    """Check if a theme directory contains a manually authored theme."""
    css_path = theme_dir / "theme.css"
    if not css_path.is_file():
        return False
    first_line = css_path.read_text(encoding="utf-8").split("\n", 1)[0]
    return "auto-generated" not in first_line


def generate_theme(slug: str, display_name: str, variant: str) -> str:
    """Generate a single theme directory. Returns a status string."""
    theme_dir = THEMES_DIR / slug

    # Skip manually authored themes
    if theme_dir.is_dir() and is_manually_authored(theme_dir):
        return f"skipped (manual): {slug}"

    # Fetch CSS
    css_text = fetch_css(slug)
    if css_text:
        colors = extract_colors(css_text, variant)
    else:
        colors = dict(DEFAULTS[variant])

    # Create theme directory
    theme_dir.mkdir(parents=True, exist_ok=True)

    # Write theme.css
    css_content = THEME_CSS_TEMPLATE.format(slug=slug, **colors)
    (theme_dir / "theme.css").write_text(css_content, encoding="utf-8")

    # Write theme.toml
    toml_content = THEME_TOML_TEMPLATE.format(
        display_name=display_name,
        slug=slug,
        variant=variant,
        **colors,
    )
    (theme_dir / "theme.toml").write_text(toml_content, encoding="utf-8")

    status = "generated" if css_text else "generated (defaults)"
    return f"{status}: {slug}"


def main() -> None:
    """Generate theme directories for all hljs themes."""
    print(f"Generating themes for {len(HLJS_THEMES)} highlight.js themes...")
    print(f"Output directory: {THEMES_DIR}")
    print()

    generated = 0
    skipped = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(generate_theme, slug, name, variant): slug
            for slug, name, variant in HLJS_THEMES
        }

        for future in as_completed(futures):
            slug = futures[future]
            try:
                result = future.result()
                print(f"  {result}")
                if result.startswith("skipped"):
                    skipped += 1
                else:
                    generated += 1
            except Exception as exc:
                print(f"  FAILED: {slug} - {exc}")
                failed += 1

    print()
    print(f"Done! Generated: {generated}, Skipped: {skipped}, Failed: {failed}")


if __name__ == "__main__":
    main()
