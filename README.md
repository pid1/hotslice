# hotslice 🍕

A hot take, one slice at a time. **Markdown → HTML slide decks from the CLI.**

hotslice converts a single Markdown file into a self-contained HTML presentation with keyboard/click navigation, syntax highlighting, and pluggable themes — using only 2 Python dependencies.

## Quick Start

```bash
# Install (one-liner for macOS and Linux)
curl -fsSL https://raw.githubusercontent.com/pid1/hotslice/main/install.sh | bash

# Build a deck
hotslice build slides.md

# Open it
open dist/index.html
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
theme = "dark"
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
theme = "dark"
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

```
hotslice build <input.md> [options]
```

| Flag            | Default            | Description                        |
|-----------------|--------------------|------------------------------------|
| `-o, --output`  | `dist/index.html`  | Output HTML file path              |
| `--theme`       | `light`            | Theme name or path                 |
| `--theme-dir`   | bundled `themes/`  | Directory to search for themes     |
| `--title`       | auto-detected      | Presentation title override        |
| `--separator`   | `^---$`            | Slide separator regex              |

## Themes

### Built-in Themes

- **light**: Clean white background, indigo accents (default)
- **dark**: Deep slate background, blue accents

Use with `--theme dark` or set in frontmatter/config.

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
  theme.toml      # Optional: metadata (name, description, author)
```

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

## Configuration

hotslice supports two levels of TOML configuration that are layered together.

### User config (`~/.config/hotslice/hotslice.toml`)

Set personal defaults that apply to all your projects:

```toml
[defaults]
theme = "dark"
output = "dist/index.html"
separator = "^---$"

[metadata]
author = "Your Name"
date = ""
```

The install script creates this file automatically. You can also create it by hand.

### Project config (`hotslice.toml` in project root)

Override user defaults for a specific project:

```toml
[defaults]
theme = "light"
output = "dist/index.html"
separator = "^---$"

[metadata]
author = "Team Name"
date = "2026-01-01"
```

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

Deep-link to any slide with `#N` in the URL (e.g., `index.html#3`).

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
| `build`        | Build demo deck to dist/              |
| `lint`         | Run ruff linter                       |
| `lint-fix`     | Auto-fix lint issues                  |
| `format`       | Run ruff formatter                    |
| `test`         | Run pytest                            |
| `install-deps` | Install Python dependencies with uv   |
