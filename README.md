# hotslice 🍕

A hot take, one slice at a time. **Markdown → HTML slide decks from the CLI.**

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

Open `http://localhost:8000` in your browser to upload a `.md` file, choose a theme, preview it live, and download the generated HTML. The web UI features a pizza-themed design with a two-column layout: the upload form on the left and a live preview panel on the right. The theme picker groups options into Hotslice Themes, Light Code Themes, and Dark Code Themes, with human-readable names.

**API endpoints:**

| Method | Path          | Description                              |
|--------|---------------|------------------------------------------|
| GET    | `/`           | Upload form (HTML)                       |
| GET    | `/api/themes` | List available themes (JSON)             |
| POST   | `/convert`    | Convert uploaded Markdown to HTML (multipart form) |

## Themes

### Built-in Themes

- **pizza-light** (default): Warm pizza-inspired light theme with cream background (#FFF8F0), red/orange accents, and Fredoka font. Uses `github` highlight.js stylesheet.
- **pizza-dark**: Rich dark pizza-inspired theme with charcoal background (#1A0F0A), orange/red accents, and Fredoka font. Uses `github-dark` highlight.js stylesheet.

Use with `--theme pizza-dark` or set in frontmatter/config.

Each theme specifies its own highlight.js color scheme via the `hljs_theme` field in `theme.toml`. The matching stylesheet is loaded from the highlight.js CDN automatically.

### Highlight.js Themes

In addition to the built-in themes, hotslice includes all 255 highlight.js themes as selectable options. When you use an hljs theme (e.g., `--theme monokai` or `--theme nord`), hotslice automatically selects the appropriate pizza base theme (pizza-light for light hljs themes, pizza-dark for dark hljs themes) and applies the chosen highlight.js stylesheet for code blocks.

The web UI and `/api/themes` endpoint display human-readable theme names grouped by variant (Light Code Themes and Dark Code Themes).

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
  theme.toml      # Optional: metadata (name, description, author, hljs_theme)
```

The `theme.toml` file supports these fields:

```toml
name = "my-theme"
description = "A brief description of the theme."
author = "Your Name"
hljs_theme = "github"   # highlight.js stylesheet name (default: "github-dark")
```

The `hljs_theme` value maps to a stylesheet on the highlight.js CDN. See the [highlight.js demo](https://highlightjs.org/demo) for available style names.

Override the CSS custom properties to restyle everything:

```css
:root {
  --slide-bg: #ffffff;     /* slide background */
  --slide-fg: #111111;     /* text color */
  --accent: #4f46e5;       /* headings, links, accents */
  --code-bg: #f3f4f6;      /* code block background */
  --code-fg: #1f2937;      /* code text color */
  --font-sans: system-ui, sans-serif;
  --font-mono: 'SF Mono', monospace;
  --slide-padding: 64px;
  --slide-max-width: 1100px;
}
```

The optional `theme.js` runs after the deck runtime, so you can add animations, custom key bindings, or other enhancements.

## Slide Layout

### Auto-scaling

Slides automatically scale down when their content exceeds the viewport height. This prevents text from overflowing or being clipped. The scaling recalculates on window resize.

### Two-column layout

Slides that contain exactly one code block alongside other content (headings, paragraphs, lists) are automatically rendered in a side-by-side two-column layout. Text appears on the left and the code block on the right. On viewports narrower than 900px, columns stack vertically.

Slides with multiple code blocks or code-only slides are not affected.

## Docker

Run the web UI in a container:

```bash
docker build -t hotslice .
docker run -p 8000:8000 hotslice
```

Open `http://localhost:8000` to access the upload form. The container runs as a non-root user and exposes port 8000.

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
