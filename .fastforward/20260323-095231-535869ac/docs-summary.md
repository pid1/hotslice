# Documentation Summary

## Overview

Updated `README.md` and `AGENTS.md` to reflect the addition of 255 generated on-disk highlight.js themes, the searchable web UI theme picker, and the Atkinson Hyperlegible Mono code font.

## Changes

### README.md

- **Themes > Built-in Themes**: Replaced the two-theme description with a section covering all 257 themes (2 hand-crafted + 255 generated). Added usage examples for generated themes (`--theme monokai`, `--theme nord`, `--theme base16-dracula`). Noted that all themes appear in the web UI.
- **Removed "Highlight.js Themes (CLI Only)" section**: This section was no longer accurate. All hljs themes now have on-disk directories and are available in both the CLI and web UI.
- **Web UI description** (under `hotslice serve`): Updated to describe the searchable theme picker with Light/Dark grouping and dynamic color preview for all 257 themes.
- **Creating a Theme > theme.toml**: Added documentation for the `variant` field and `[colors]` section. Updated the directory structure listing to mention the new fields.
- **CSS Custom Properties**: Updated `--font-mono` default value from `'SF Mono', monospace` to `'Atkinson Hyperlegible Mono', 'SF Mono', 'Fira Code', monospace`. Added note about the Atkinson Hyperlegible Mono font from Google Fonts.

### AGENTS.md

- **Design Decisions**: Updated the `list_available_themes()` decision to reflect that it now returns 257 themes including generated ones. Added three new decisions:
  - `render_deck()` on-disk-first resolution order with hljs fallback.
  - Generated theme `auto-generated` CSS comment marker protects hand-crafted pizza themes from the generator.
  - Web template color data attributes (`data-slide-bg`, etc.) drive the dynamic preview.
- **Key Files**: Added `scripts/generate_themes.py`. Updated `themes/` description from "2 pizza themes" to "257 bundled themes."
- **CSS Custom Properties**: Updated `--font-mono` default value.
- **Theme directory structure**: Added `variant` and `[colors]` to `theme.toml` description.

## Verification

All documentation changes verified against:
- `hotslice/renderer.py`: Confirmed `list_available_themes()` returns color metadata and sorts alphabetically; `render_deck()` tries on-disk first.
- `hotslice/templates/deck.html.j2`: Confirmed Google Fonts link and `--font-mono` value.
- `hotslice/templates/web.html.j2`: Confirmed search input, `<optgroup>` grouping, and `data-*` color attributes.
- `themes/monokai/theme.toml` and `theme.css`: Confirmed generated theme structure matches documentation.
- `themes/pizza-light/theme.toml` and `theme.css`: Confirmed `[colors]` section and updated `--font-mono`.
- QA report: All 23 verification criteria passed.
