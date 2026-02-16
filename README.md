# hotslice 🍕

A hot take, one slice at a time. **Markdown → HTML slide decks from the CLI.**

hotslice converts a single Markdown file into a self-contained HTML presentation with keyboard/click navigation, syntax highlighting, and pluggable themes — using only 2 Python dependencies.

## Quick Start

```bash
# Install
uv add hotslice

# Build a deck
hotslice build slides.md

# Open it
open dist/index.html
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

- **light** — Clean white background, indigo accents (default)
- **dark** — Deep slate background, blue accents

Use with `--theme dark` or set in frontmatter/config.

### Creating a Theme

A theme is a directory with at minimum a `theme.css` file:

```
themes/my-theme/
  theme.css       # Required — CSS overrides
  theme.js        # Optional — JS that runs after deck runtime
  theme.toml      # Optional — metadata (name, description, author)
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

Create a `hotslice.toml` in your project root for defaults:

```toml
[defaults]
theme = "light"
output = "dist/index.html"
separator = "^---$"

[metadata]
author = "Your Name"
date = "2026-01-01"
```

Priority order: CLI flags > frontmatter > `hotslice.toml` > built-in defaults.

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
