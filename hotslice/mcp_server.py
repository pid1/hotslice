"""MCP server exposing hotslice capabilities to AI agents."""

from __future__ import annotations

import re

from mcp.server.fastmcp import FastMCP

from hotslice.config import Config
from hotslice.parser import parse_deck
from hotslice.renderer import list_available_themes, render_deck

mcp = FastMCP(
    "hotslice",
    instructions="Use the write_presentation prompt to learn the slide authoring format. "
    "Use build_presentation to convert Markdown to an HTML slide deck. "
    "Use list_themes to browse available themes.",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",
)

_AUTHORING_GUIDE = """\
# How to Write a hotslice Presentation

hotslice converts a single Markdown file into a self-contained HTML slide deck
with keyboard/click navigation, syntax highlighting, and pluggable themes.

## File Structure

A hotslice Markdown file has optional TOML frontmatter at the top, followed by
slides separated by `---`:

    +++
    title = "My Presentation"
    theme = "pizza-light"
    +++

    # Title Slide

    Subtitle or description here.

    ---

    ## Second Slide

    Content goes here.

    ---

    ## Third Slide

    More content.

## Frontmatter

Place optional TOML between +++ fences at the very top of the file:

- `title` - Sets the HTML <title> and can be used by themes.
- `theme` - Overrides the default theme (e.g., "pizza-dark", "monokai", "nord").

## Slide Separator

Use `---` on its own line (three dashes, nothing else) to start a new slide.

## Headings

- `# Heading` - Title slide heading. Best for the first slide or section breaks.
- `## Heading` - Regular slide title.
- `### Heading` - Subtitle, rendered in the accent color.

## Code Blocks

Use fenced code blocks with a language tag for syntax highlighting:

    ```python
    def hello():
        print("world")
    ```

highlight.js handles syntax highlighting. Most common languages are supported.

## Tables

GFM-style tables are supported:

    | Header 1 | Header 2 |
    |----------|----------|
    | Cell 1   | Cell 2   |

## Other Markdown Features

- **Bold**: `**text**`
- *Italic*: `*text*`
- ~~Strikethrough~~: `~~text~~`
- Links: `[text](url)`
- Images: `![alt](url)` (auto-sized to fit the slide)
- Blockquotes: `> text`
- Ordered and unordered lists
- Inline code: `code`

## Best Practices

- One main idea per slide.
- Keep slides readable at a glance. Avoid cramming too much content.
- Use a single `# Heading` with no other content for clean section transitions.
- Use code blocks to demonstrate technical concepts.
- Aim for 5-15 slides for a typical presentation.

## Themes

Use the `list_themes` tool to browse all 257 available themes. Popular choices:

- `pizza-light` (default) - Warm, pizza-inspired light theme
- `pizza-dark` - Rich dark pizza-inspired theme
- `monokai` - Classic dark code theme
- `nord` - Arctic, north-bluish color palette
- `github` - GitHub-style light theme
- `github-dark` - GitHub-style dark theme
- `dracula` - Popular dark theme

Specify the theme in frontmatter (`theme = "monokai"`) or pass it to `build_presentation`.

## Complete Example

    +++
    title = "My Talk"
    theme = "pizza-light"
    +++

    # My Talk

    Speaker Name - March 2026

    ---

    ## The Problem

    - Users are frustrated
    - Current solution is too slow
    - We need a better approach

    ---

    ## Our Solution

    ```python
    result = hotslice.build("slides.md")
    # That's it.
    ```

    ---

    ## Key Metrics

    | Metric     | Before | After |
    |------------|--------|-------|
    | Build time | 30s    | 0.1s  |
    | File size  | 5 MB   | 50 KB |
    | Dependencies | 30+  | 2     |

    ---

    # Questions?

    @speaker on twitter

## Building

After writing your Markdown, use the `build_presentation` tool:
- Pass the full Markdown text as the `markdown` parameter.
- Optionally specify a `theme` (defaults to "pizza-light").
- The tool returns a complete HTML string. Save it as an .html file and open it in any browser.
"""

_THEME_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
_MAX_MARKDOWN_SIZE = 2 * 1024 * 1024  # 2 MB


@mcp.prompt()
def write_presentation() -> str:
    """Get instructions for writing a hotslice Markdown presentation."""
    return _AUTHORING_GUIDE


@mcp.tool()
def build_presentation(markdown: str, theme: str = "pizza-light") -> str:
    """Convert Markdown to a self-contained HTML slide deck.

    Slides are separated by `---` on its own line. Optional TOML frontmatter
    between `+++` fences at the top can set `title` and `theme`. Use
    `list_themes` to see available theme options.
    """
    if not _THEME_NAME_RE.match(theme):
        return (
            "Error: Invalid theme name. Theme names may only contain letters, "
            "digits, hyphens, and underscores. Use list_themes to see valid options."
        )
    if len(markdown) > _MAX_MARKDOWN_SIZE:
        return "Error: Markdown text exceeds 2MB limit."
    if len(markdown.strip()) == 0:
        return "Error: Markdown text is empty."

    config = Config(theme=theme)
    deck = parse_deck(markdown)

    # Apply frontmatter overrides
    if "theme" in deck.frontmatter:
        fm_theme = str(deck.frontmatter["theme"])
        if _THEME_NAME_RE.match(fm_theme):
            config.theme = fm_theme
    if "title" in deck.frontmatter:
        config.title = str(deck.frontmatter["title"])

    try:
        return render_deck(deck, config)
    except FileNotFoundError as e:
        return f"Error: {e}"


@mcp.tool()
def list_themes() -> list[dict]:
    """List all available themes with name, display name, and variant (light or dark)."""
    return [
        {"name": t["name"], "display_name": t["display_name"], "variant": t["variant"]}
        for t in list_available_themes()
    ]


def main():
    """Run the MCP server in stdio mode for local agent connections."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
