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

1. **Always use devenv scripts** -- Run `lint` not `ruff check .`
2. **Use `build`** to test changes: it builds `examples/demo.md` to `demo.html`
3. **Run `lint`** before considering work complete

### Design Decisions

- `list_available_themes()` returns only on-disk themes (directories with `theme.css`). All 255 hljs themes now have generated on-disk directories, so this function returns 257 themes total. Do not add dynamic theme discovery to this function; it scans directories, reads `theme.toml`, and returns color metadata.
- `render_deck()` tries on-disk theme resolution first, then falls back to hljs slug-to-pizza-base mapping. Since all hljs slugs now have on-disk themes, the fallback only triggers if a generated theme directory is deleted. Do not reverse this priority order.
- Generated theme CSS files contain `auto-generated` in their first-line comment. The generator script (`scripts/generate_themes.py`) uses this marker to distinguish generated themes from hand-crafted ones (pizza-light, pizza-dark). Do not add this marker to hand-crafted themes; it would cause the generator to overwrite them.
- The web template stores each theme's color values in `data-slide-bg`, `data-slide-fg`, `data-accent`, `data-code-bg`, `data-code-fg` attributes on `<option>` elements. The preview JS reads these attributes to apply inline styles. Do not replace this with hardcoded color mappings.
- Base16 theme slugs (e.g., `base16-monokai`) must be converted to CDN subdirectory paths (`base16/monokai`) before constructing highlight.js CDN URLs. The CDN hosts base16 CSS under `styles/base16/{name}.min.css`, not `styles/base16-{name}.min.css`. This conversion lives in two places that must stay in sync: `_hljs_slug_to_cdn_path()` in `hotslice/renderer.py` (for built deck output) and the equivalent JavaScript in `hotslice/templates/web.html.j2`'s `applyPreview()` function (for web UI preview). If you change one, update the other.
- Theme name validation regex `^[a-zA-Z0-9][a-zA-Z0-9_-]*$` is defined independently in `hotslice/web.py` (`_THEME_NAME_RE`) and `hotslice/mcp_server.py` (`_THEME_NAME_RE`). Both files also re-validate frontmatter theme overrides and apply matching size limits. If you change validation rules in one, update the other.
- The MCP server sets `streamable_http_path="/"` in `hotslice/mcp_server.py` so the endpoint resolves to `/mcp` when mounted via `app.mount("/mcp", ...)` in `hotslice/web.py`. If you change the mount path, update `streamable_http_path` to match (or vice versa), otherwise the endpoint breaks or doubles the prefix.

### Key Files

| File | Purpose |
|------|---------|
| `hotslice/config.py` | Config loading with layered user/project support |
| `hotslice/renderer.py` | Theme resolution, HTML rendering, `list_available_themes()` |
| `hotslice/cli.py` | CLI entry point (argparse): `build` and `serve` subcommands |
| `hotslice/parser.py` | Markdown parsing and slide splitting |
| `hotslice/web.py` | FastAPI web app (upload form, theme API, conversion endpoint) |
| `hotslice/mcp_server.py` | MCP server: prompt and tools for AI agent integration |
| `install.sh` | `curl \| bash` installer for macOS and Linux |
| `hotslice.toml` | Project-level config (repo root) |
| `hotslice/hljs_themes.py` | Highlight.js theme registry (255 themes with display names, light/dark classification) |
| `scripts/generate_themes.py` | One-time generator: fetches hljs CSS from CDN, extracts colors, writes theme directories |
| `themes/` | 257 bundled themes (2 hand-crafted pizza themes + 255 generated hljs themes) |
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
  theme.toml      # OPTIONAL: metadata (name, description, author, hljs_theme, variant, [colors])
```

User themes follow the same structure. Place them in `~/.config/hotslice/themes/`:

```
~/.config/hotslice/themes/my-theme/
  theme.css
  theme.js        # optional
  theme.toml      # optional
```

The `hljs_theme` field in `theme.toml` controls which highlight.js stylesheet is loaded from the CDN. It defaults to `"github-dark"` if omitted. Set it to any valid highlight.js style name (e.g., `"github"`, `"monokai"`, `"nord"`). The `variant` field (`"light"` or `"dark"`) controls grouping in the web UI. The `[colors]` section (`slide_bg`, `slide_fg`, `accent`, `code_bg`, `code_fg`) provides the web UI with data for its live preview.

### CSS Custom Properties

The base template defines these CSS custom properties. Override them in your `theme.css`:

```css
:root {
  --slide-bg: #ffffff;          /* slide background color */
  --slide-fg: #111111;          /* main text color */
  --accent: #4f46e5;            /* accent color for headings, links, markers */
  --code-bg: #f3f4f6;           /* code block background */
  --code-fg: #1f2937;           /* code block text color */
  --font-sans: 'Atkinson Hyperlegible Next', system-ui, sans-serif;  /* body font stack */
  --font-mono: 'Atkinson Hyperlegible Mono', 'SF Mono', 'Fira Code', monospace; /* code font stack */
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
