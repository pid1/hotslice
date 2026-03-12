+++
title = "hotslice Demo"
theme = "light"
+++

# hotslice 🍕

A hot take, one slice at a time.

Markdown → HTML presentations from the CLI.

---

## Why hotslice?

- **Minimal** — only 2 runtime dependencies
- **Fast** — builds a deck in milliseconds
- **Themeable** — drop in CSS/JS, done
- **Portable** — output is a single HTML file
- **Hackable** — it's ~300 lines of Python

> "The best presentation tool is the one you'll actually use."

---

## Getting Started

Install and build your first deck:

```bash
uv add hotslice
hotslice build slides.md
open slides.html
```

That's it. No config required.

---

## Slide Format

Slides are separated by `---` on its own line.

Add **TOML frontmatter** between `+++` fences at the top:

```toml
+++
title = "My Talk"
theme = "dark"
+++
```

Then just write Markdown. Each `---` starts a new slide.

---

## Code Highlighting

Fenced code blocks get syntax highlighting via highlight.js:

```python
from hotslice.parser import parse_deck

deck = parse_deck(Path("slides.md").read_text())
for slide in deck.slides:
    print(f"Slide {slide.index}: {len(slide.html)} bytes")
```

Languages are auto-detected, or specify them explicitly.

---

## Tables Work Too

| Feature        | hotslice | Marp  | reveal.js |
|----------------|----------|-------|-----------|
| Dependencies   | 2        | 12+   | 30+       |
| Output         | HTML     | HTML/PDF | HTML   |
| Config         | TOML     | YAML  | JSON      |
| Themes         | CSS/JS   | CSS   | CSS/JS    |
| Learning curve | Low      | Low   | Medium    |

GFM-style tables just work.

---

## Rich Markdown

You get the full **CommonMark** spec plus GFM extras:

- **Bold** and *italic* and ~~strikethrough~~
- [Links](https://github.com) that work
- Inline `code` with nice styling
- Ordered and unordered lists
- Blockquotes (you saw one earlier)

### Nested lists

1. First item
   - Sub-item A
   - Sub-item B
2. Second item
3. Third item

---

## Theming

Themes are just directories with a `theme.css` file:

```
themes/my-theme/
  theme.css       ← required
  theme.js        ← optional (runs after deck JS)
  theme.toml      ← optional (metadata)
```

Override CSS custom properties to restyle everything:

```css
:root {
  --slide-bg: #0f172a;
  --slide-fg: #e2e8f0;
  --accent: #38bdf8;
}
```

---

## Navigation

| Key                    | Action         |
|------------------------|----------------|
| →  Space  Enter        | Next slide     |
| ←  Backspace           | Previous slide |
| Home                   | First slide    |
| End                    | Last slide     |
| Click right half       | Next slide     |
| Click left half        | Previous slide |

Deep-link to any slide with `#N` in the URL.

---

# Thanks! 🍕

`pip install hotslice` and start slicing.

github.com/pid1/hotslice
