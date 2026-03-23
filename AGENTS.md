# AGENTS.md — hotslice

Instructions for AI agents working in this repository.

## Development Environment

This project uses [devenv](https://devenv.sh) for reproducible development environments.

### Quick Setup

```bash
devenv shell
setup
dev
```

### Commands

| Command        | Description                         |
|----------------|-------------------------------------|
| `setup`        | Initialize repo (runs install-deps) |
| `dev`          | Build demo deck and open in browser |
| `build`        | Build demo deck to demo.html        |
| `serve`        | Start the hotslice web server       |
| `lint`         | Run ruff linter                     |
| `lint-fix`     | Run ruff with auto-fix              |
| `format`       | Run ruff formatter                  |
| `test`         | Run pytest                          |
| `install-deps` | Install dependencies with uv        |

### For AI Agents

**IMPORTANT**: When working in this repository:

1. **Always use devenv scripts** — Run `lint` not `ruff check .`
2. **Use `build`** to test changes: it builds `examples/demo.md` to `demo.html`
3. **Run `lint`** before considering work complete

### Key Files

| File | Purpose |
|------|---------|
| `hotslice/config.py` | Config loading with layered user/project support |
| `hotslice/renderer.py` | Theme resolution, HTML rendering, `list_available_themes()` |
| `hotslice/cli.py` | CLI entry point (argparse): `build` and `serve` subcommands |
| `hotslice/parser.py` | Markdown parsing and slide splitting |
| `hotslice/web.py` | FastAPI web app (upload form, theme API, conversion endpoint) |
| `install.sh` | `curl \| bash` installer for macOS and Linux |
| `hotslice.toml` | Project-level config (repo root) |
| `hotslice/hljs_themes.py` | Highlight.js theme registry (255 themes with display names, light/dark classification) |
| `themes/` | Bundled themes (pizza-light, pizza-dark) with onapizza-inspired palettes |
| `Dockerfile` | Multi-stage build for containerized web server |

---

## Slide Authoring Format

This section describes how to write `.md` files that hotslice can build into HTML presentations.

### File Structure

```markdown
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
```

### Rules

1. **Slide separator**: Use `---` on its own line (three dashes, nothing else) to start a new slide.

2. **Frontmatter** (optional): Place TOML between `+++` fences at the very top of the file.
   - `title` — Sets the HTML `<title>` and can be used by themes
   - `theme` — Overrides the default theme (e.g., `"pizza-dark"`, `"pizza-light"`, or any highlight.js theme slug like `"monokai"`)

3. **Headings**:
   - `# Heading` — Use for slide titles. Best on the first slide or section breaks.
   - `## Heading` — Use for regular slide titles.
   - `### Heading` — Use for subtitles or subsections within a slide. Rendered in the accent color.

4. **Code blocks**: Use fenced code blocks with a language tag for syntax highlighting:
   ````markdown
   ```python
   def hello():
       print("world")
   ```
   ````
   highlight.js handles syntax highlighting on the frontend. Most common languages are supported.

5. **Tables**: GFM-style tables are supported:
   ```markdown
   | Header 1 | Header 2 |
   |----------|----------|
   | Cell 1   | Cell 2   |
   ```

6. **Other Markdown features**:
   - **Bold**: `**text**`
   - *Italic*: `*text*`
   - ~~Strikethrough~~: `~~text~~`
   - Links: `[text](url)`
   - Images: `![alt](url)` — images are auto-sized to fit the slide
   - Blockquotes: `> text`
   - Ordered and unordered lists
   - Inline code: `` `code` ``

7. **Keep slides focused**: One main idea per slide. Avoid cramming too much content — the audience should be able to read everything at a glance.

8. **Section break slides**: Use a single `# Heading` with no other content for clean section transitions.

### Example: Minimal Deck

```markdown
# My Talk

Speaker Name — February 2026

---

## The Problem

- Users are frustrated
- Current solution is too slow
- We need a better approach

---

## Our Solution

```python
result = hotslice.build("slides.md")
# That's it. That's the solution.
```

---

# Questions?

@speaker on twitter
```

### Building

```bash
hotslice build slides.md                   # → slides.html
hotslice build slides.md -o output.html    # custom output path
hotslice build slides.md --theme pizza-dark # use dark theme
hotslice build slides.md --theme monokai   # use highlight.js theme
```

---

## Theme Authoring

Themes are directories containing at minimum a `theme.css` file.

### Theme Resolution Order

When hotslice resolves a theme name, it searches in this order:

1. `--theme-dir` argument (custom themes directory, if provided)
2. `~/.config/hotslice/themes/<name>/` (user themes directory)
3. Bundled `themes/` directory (ships with the package)
4. Direct path (treats the theme name as an absolute or relative path)

The first match wins. This means user themes override bundled themes of the same name.

### Directory Structure

```
themes/my-theme/
  theme.css       # REQUIRED: CSS overrides and custom styles
  theme.js        # OPTIONAL: JavaScript that runs after deck runtime
  theme.toml      # OPTIONAL: metadata (name, description, author, hljs_theme)
```

User themes follow the same structure. Place them in `~/.config/hotslice/themes/`:

```
~/.config/hotslice/themes/my-theme/
  theme.css
  theme.js        # optional
  theme.toml      # optional
```

The `hljs_theme` field in `theme.toml` controls which highlight.js stylesheet is loaded from the CDN. It defaults to `"github-dark"` if omitted. Set it to any valid highlight.js style name (e.g., `"github"`, `"monokai"`, `"nord"`).

### CSS Custom Properties

The base template defines these CSS custom properties. Override them in your `theme.css`:

```css
:root {
  --slide-bg: #ffffff;          /* slide background color */
  --slide-fg: #111111;          /* main text color */
  --accent: #4f46e5;            /* accent color for headings, links, markers */
  --code-bg: #f3f4f6;           /* code block background */
  --code-fg: #1f2937;           /* code block text color */
  --font-sans: system-ui, sans-serif;  /* body font stack */
  --font-mono: 'SF Mono', monospace;   /* code font stack */
  --slide-padding: 64px;        /* slide content padding */
  --slide-max-width: 1100px;    /* max content width */
}
```

### HTML Structure

Each slide is rendered as:

```html
<section class="slide" data-index="N">
  <div class="slide-inner">
    <!-- parsed markdown HTML here -->
  </div>
</section>
```

The first slide has `data-index="0"`. The active slide has the `active` class.

### Theme JS

If your theme includes a `theme.js`, it runs after the deck's navigation runtime is initialized. You can use it for:
- Adding CSS transitions between slides
- Custom key bindings
- Analytics hooks
- Animation triggers

The deck runtime exposes no global API — interact via DOM events and the `.slide.active` class.
