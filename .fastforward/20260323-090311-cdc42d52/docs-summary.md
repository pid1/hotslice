# Documentation Summary

## Changes Made

### README.md

- **Slide Format section**: Updated frontmatter example from `theme = "dark"` to `theme = "pizza-dark"` (both the inline example and the frontmatter reference block).
- **CLI Reference**: Changed `--theme` default from `light` to `pizza-light` in the flags table.
- **Web UI description**: Expanded the `hotslice serve` section to describe the new pizza-themed design, two-column layout with live preview panel, and grouped theme picker with human-readable names.
- **Built-in Themes section**: Replaced old `light`/`dark` theme descriptions with `pizza-light` and `pizza-dark`, including their color palettes and highlight.js stylesheet mappings.
- **New Highlight.js Themes section**: Added documentation explaining that all 255 highlight.js themes are available as selectable options, with automatic pizza base theme selection based on light/dark variant.
- **Configuration examples**: Updated user config example from `theme = "dark"` to `theme = "pizza-dark"`, and project config example from `theme = "light"` to `theme = "pizza-light"`.

### AGENTS.md

- **Key Files table**: Added `hotslice/hljs_themes.py` entry (highlight.js theme registry with 255 themes, display names, light/dark classification).
- **Key Files table**: Updated `themes/` description from "(light, dark) with GitHub-inspired palettes" to "(pizza-light, pizza-dark) with onapizza-inspired palettes".
- **Frontmatter example**: Changed `theme = "light"` to `theme = "pizza-light"` in the file structure example.
- **Frontmatter rules**: Updated theme examples from `"dark"`, `"light"` to `"pizza-dark"`, `"pizza-light"`, added hljs theme slug example (`"monokai"`).
- **Building section**: Changed `--theme dark` to `--theme pizza-dark`, added `--theme monokai` example for highlight.js theme usage.

## Verification

All documentation changes were verified against the actual implementation:
- `hotslice/config.py` confirms default theme is `"pizza-light"` (line 20)
- `hotslice/web.py` confirms form default is `Form("pizza-light")` (line 42)
- `hotslice/renderer.py` confirms hljs theme integration with pizza base theme mapping (lines 127-132)
- `hotslice/hljs_themes.py` confirms 255 themes with display names and variant classification
- `themes/` directory contains only `pizza-light/` and `pizza-dark/`
- `hotslice.toml` confirms project default is `theme = "pizza-light"`
