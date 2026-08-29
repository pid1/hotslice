# hotslice 🍕

A hot take, one slice at a time. **Markdown → HTML slide decks from the CLI.**

See it in action, and use the MCP, at [hotslice.pizza](https://hotslice.pizza/).

hotslice converts a single Markdown file into a self-contained HTML presentation with keyboard/click navigation, syntax highlighting, and pluggable themes. Build decks from the CLI or upload Markdown through the built-in web UI.

## Quick Start

```bash
# Install (one-liner for macOS and Linux)
curl -fsSL https://raw.githubusercontent.com/pid1/hotslice/main/install.sh | bash

# Build a deck
hotslice build slides.md

# Open it (output defaults to <input_stem>.html in PWD)
open slides.html
```

## Installation

### One-line installer (recommended)

The install script works on macOS and Linux. It installs [uv](https://docs.astral.sh/uv/) if needed, then installs hotslice:

```bash
curl -fsSL https://raw.githubusercontent.com/pid1/hotslice/main/install.sh | bash
```

The installer:
- Detects your OS (macOS or Linux)
- Installs `uv` if it is not already present
- Installs hotslice to `~/.local/bin/` via `uv tool install`
- Creates a user config directory at `~/.config/hotslice/`
- Writes a default `~/.config/hotslice/hotslice.toml` (preserves any existing file)
- Creates `~/.config/hotslice/themes/` for user-installed themes

### Manual install with uv

```bash
uv add hotslice
```

Or install as a standalone tool:

```bash
uv tool install git+https://github.com/pid1/hotslice
```

## Slide Format

Write slides in Markdown, separated by `---`:

```markdown
+++
title = "My Talk"
theme = "pizza-dark"
+++

# Welcome

This is the title slide.

---

## Second Slide

- Point one
- Point two

---

## Code Example

\```python
print("hello from hotslice")
\```
```

### Frontmatter

Add optional TOML frontmatter between `+++` fences at the top of your file:

```toml
+++
title = "My Talk"
theme = "pizza-dark"
+++
```

Supported fields:
- `title` — presentation title (used in `<title>` tag)
- `theme` — theme name override

### Markdown Support

hotslice uses the GFM-like preset from markdown-it-py, which includes:
- Full CommonMark spec
- Tables
- Strikethrough (`~~text~~`)
- Linkification
- Typographic replacements (smart quotes, etc.)
- Fenced code blocks with syntax highlighting (via highlight.js)

## CLI Reference

### `hotslice build`

```
hotslice build <input.md> [options]
```

| Flag            | Default              | Description                        |
|-----------------|----------------------|------------------------------------|
| `-o, --output`  | `<input_stem>.html`  | Output HTML file path              |
| `--theme`       | `pizza-light`        | Theme name or path                 |
| `--theme-dir`   | bundled `themes/`    | Directory to search for themes     |
| `--title`       | auto-detected        | Presentation title override        |
| `--separator`   | `^---$`              | Slide separator regex              |

When no `-o` flag is provided, the output file is written to the current directory using the input file's stem. For example, `hotslice build training.md` produces `training.html` in the current directory.

### `hotslice serve`

Start a web server with an upload form for converting Markdown to HTML presentations.

```
hotslice serve [options]
```

| Flag       | Default    | Description                    |
|------------|------------|--------------------------------|
| `--host`   | `0.0.0.0` | Host to bind to                |
| `--port`   | `8000`     | Port to listen on              |

Open `http://localhost:8000` in your browser. The landing page explains what hotslice is, shows how to get started, and provides the upload form for converting Markdown to slides.

The web UI features a pizza-themed design with a two-column layout: the upload form on the left and a live preview panel on the right. The theme picker lists all 257 installed themes, grouped by Light and Dark, with a search box for quick filtering. Selecting a theme updates the preview with that theme's actual colors.

Below the form, three info cards cover the main usage paths: CLI quick start, the web UI and its API endpoints, and the MCP server with its connection config. The footer includes a link to sponsor the project via [GitHub Sponsors](https://github.com/sponsors/pid1).

**Upload restrictions:** The `/convert` endpoint accepts `.md`, `.markdown`, and `.txt` files up to 2 MB. Files must be valid UTF-8 text. Uploads that exceed the size limit receive an HTTP 413 response.

**API endpoints:**

| Method | Path          | Description                              |
|--------|---------------|------------------------------------------|
| GET    | `/`           | Landing page with upload form (HTML)     |
| GET    | `/api/themes` | List available themes (JSON)             |
| POST   | `/convert`    | Convert uploaded Markdown to HTML (multipart form) |
| POST   | `/mcp`        | MCP server endpoint (see [MCP Server](#mcp-server)) |

## Themes

### Built-in Themes

hotslice ships with 257 themes: 2 hand-crafted pizza themes and 255 themes generated from the highlight.js stylesheet library.

**Hand-crafted themes:**

- **pizza-light** (default): Warm pizza-inspired light theme with cream background (#FFF8F0), red/orange accents, and Fredoka font. Uses `github` highlight.js stylesheet.
- **pizza-dark**: Rich dark pizza-inspired theme with charcoal background (#1A0F0A), orange/red accents, and Fredoka font. Uses `github-dark` highlight.js stylesheet.

**Generated themes** (255 total, 74 light + 183 dark):

Each highlight.js theme has an on-disk directory under `themes/` containing a `theme.css` and `theme.toml` with extracted colors. Use any of them by name:

```bash
hotslice build slides.md --theme monokai
hotslice build slides.md --theme nord
hotslice build slides.md --theme base16-dracula
```

All 257 themes appear in the web UI theme picker, grouped by Light and Dark. Each theme specifies its own highlight.js color scheme via the `hljs_theme` field in `theme.toml`. The matching stylesheet is loaded from the highlight.js CDN automatically.

### Theme Resolution Order

When you specify a theme name, hotslice searches these locations in order:

1. `--theme-dir` argument (if provided)
2. `~/.config/hotslice/themes/<name>/` (user themes)
3. Bundled `themes/` directory (ships with hotslice)
4. Direct path (absolute or relative)

### User Themes

Place custom themes in `~/.config/hotslice/themes/` to make them available across all your projects. For example, a theme called `corporate` would live at:

```
~/.config/hotslice/themes/corporate/
  theme.css       # Required
  theme.js        # Optional
  theme.toml      # Optional
```

Then use it with `hotslice build slides.md --theme corporate`.

### Creating a Theme

A theme is a directory with at minimum a `theme.css` file:

```
themes/my-theme/
  theme.css       # Required: CSS overrides
  theme.js        # Optional: JS that runs after deck runtime
  theme.toml      # Optional: metadata (name, description, author, hljs_theme, variant, colors)
```

The `theme.toml` file supports these fields:

```toml
name = "my-theme"
description = "A brief description of the theme."
author = "Your Name"
hljs_theme = "github"   # highlight.js stylesheet name (default: "github-dark")
variant = "light"       # "light" or "dark" (controls web UI grouping)

[colors]
slide_bg = "#ffffff"
slide_fg = "#111111"
accent = "#4f46e5"
code_bg = "#f3f4f6"
code_fg = "#1f2937"
```

The `hljs_theme` value maps to a stylesheet on the highlight.js CDN. See the [highlight.js demo](https://highlightjs.org/demo) for available style names. The `[colors]` section provides the web UI with color data for its live preview. The `variant` field controls whether the theme appears in the Light or Dark group in the web UI picker.

Override the CSS custom properties to restyle everything:

```css
:root {
  --slide-bg: #ffffff;     /* slide background */
  --slide-fg: #111111;     /* text color */
  --accent: #4f46e5;       /* headings, links, accents */
  --code-bg: #f3f4f6;      /* code block background */
  --code-fg: #1f2937;      /* code text color */
  --font-sans: 'Atkinson Hyperlegible Next', system-ui, sans-serif;
  --font-mono: 'Atkinson Hyperlegible Mono', 'SF Mono', 'Fira Code', monospace;
  --slide-padding: 64px;
  --slide-max-width: 1100px;
}
```

Body text uses [Atkinson Hyperlegible Next](https://fonts.google.com/specimen/Atkinson+Hyperlegible+Next) by default, and code blocks use [Atkinson Hyperlegible Mono](https://fonts.google.com/specimen/Atkinson+Hyperlegible+Mono). Both fonts are loaded from Google Fonts and designed for maximum legibility at all sizes. The pizza themes override the body font to Fredoka.

The optional `theme.js` runs after the deck runtime, so you can add animations, custom key bindings, or other enhancements.

## Slide Layout

### Auto-scaling

Slides automatically scale down when their content exceeds the viewport height. This prevents text from overflowing or being clipped. The scaling recalculates on window resize.

### Two-column layout

Slides that contain exactly one code block alongside other content (headings, paragraphs, lists) are automatically rendered in a side-by-side two-column layout. Text appears on the left and the code block on the right. On viewports narrower than 900px, columns stack vertically.

Slides with multiple code blocks or code-only slides are not affected.

## MCP Server

hotslice includes a [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that lets AI agents generate presentations programmatically.

### Connecting via HTTP

When running the web server (`hotslice serve`), the MCP endpoint is available at `/mcp`:

```json
{
  "mcpServers": {
    "hotslice": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Connecting via stdio

For local use with MCP-compatible tools:

```json
{
  "mcpServers": {
    "hotslice": {
      "command": "hotslice-mcp"
    }
  }
}
```

### Available Capabilities

| Type   | Name                 | Description                                       |
|--------|----------------------|---------------------------------------------------|
| Prompt | `write_presentation` | Guide for writing hotslice Markdown presentations |
| Tool   | `build_presentation` | Convert Markdown to an HTML slide deck            |
| Tool   | `list_themes`        | List all available themes with metadata           |

## Configuration

hotslice supports two levels of TOML configuration that are layered together.

### User config (`~/.config/hotslice/hotslice.toml`)

Set personal defaults that apply to all your projects:

```toml
[defaults]
theme = "pizza-dark"
separator = "^---$"

[metadata]
author = "Your Name"
date = ""
```

The install script creates this file automatically. You can also create it by hand.

You can add an explicit `output` key to always write to a fixed path (e.g., `output = "dist/index.html"`). When omitted, the output path is derived from the input filename.

### Project config (`hotslice.toml` in project root)

Override user defaults for a specific project:

```toml
[defaults]
theme = "pizza-light"
separator = "^---$"

[metadata]
author = "Team Name"
date = "2026-01-01"
```

As with user config, you can add `output = "build/slides.html"` to force a fixed output path for the project.

### Priority order

Settings are resolved with the highest-priority source winning:

CLI flags > frontmatter > project `hotslice.toml` > user `~/.config/hotslice/hotslice.toml` > built-in defaults

Metadata fields merge across layers. If the user config sets `author` and the project config sets `date`, both values are preserved in the final configuration.

## Navigation

Once your deck is open in a browser:

| Input                | Action         |
|----------------------|----------------|
| → / Space / Enter    | Next slide     |
| ← / Backspace        | Previous slide |
| Home                 | First slide    |
| End                  | Last slide     |
| Click right half     | Next slide     |
| Click left half      | Previous slide |

Deep-link to any slide with `#N` in the URL (e.g., `slides.html#3`).

## Self-hosting

hotslice is stateless and small, so it runs comfortably on hardware you already
own. Behind a Cloudflare Tunnel there are no open ports, no certificates to
renew, and no origin IP in DNS — `docker compose up -d` plus a tunnel token is
the whole of it.

See [docs/deploy.md](docs/deploy.md) for the full path, including the edge rules
worth adding in front of a public, unauthenticated `/convert` and `/mcp`.

## Development

### Prerequisites

- [Nix](https://nixos.org/download.html) with flakes enabled
- [devenv](https://devenv.sh/getting-started/)

### Getting Started

```bash
devenv shell
setup
dev
```

### Available Commands

Run these inside `devenv shell`:

| Command        | Description                           |
|----------------|---------------------------------------|
| `setup`        | Install dependencies                  |
| `dev`          | Build demo deck and open in browser   |
| `build`        | Build demo deck to demo.html          |
| `serve`        | Start the hotslice web server         |
| `lint`         | Run ruff linter                       |
| `lint-fix`     | Auto-fix lint issues                  |
| `format`       | Run ruff formatter                    |
| `test`         | Run pytest                            |
| `install-deps` | Install Python dependencies with uv   |
