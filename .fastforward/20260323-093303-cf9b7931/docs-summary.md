# Documentation Summary: Web UI Theme Cleanup and Emoji Removal

## Files Updated

### README.md

Two sections updated to reflect the web UI theme dropdown changes:

1. **`hotslice serve` description (line 136)**: Removed outdated mention of the theme picker grouping options into "Hotslice Themes, Light Code Themes, and Dark Code Themes." Replaced with accurate description: "The theme dropdown lists all installed on-disk themes."

2. **Highlight.js Themes section (lines 157-161)**: Renamed from "Highlight.js Themes" to "Highlight.js Themes (CLI Only)" to make the scope clear. Updated body text to state that hljs themes are available from the CLI only. Replaced the incorrect claim that the web UI displays hljs themes grouped by variant with accurate guidance: "The web UI theme dropdown and `/api/themes` endpoint show only on-disk themes."

### AGENTS.md

Added a **Design Decisions** subsection (2 bullet points) to the Development Environment section:

1. Documents that `list_available_themes()` intentionally returns only on-disk themes, and that agents should not add hljs-only themes back to this function. Explains the separation between web UI (on-disk themes only) and CLI (hljs themes via `get_hljs_theme_info()`).

2. Documents the `data-hljs-theme` attribute pattern on `<option>` elements and warns agents not to replace it with hardcoded slug-to-stylesheet mappings.

Both entries target decisions an agent might try to "fix" without understanding the intent.

## Verification

All documentation changes verified against the actual implementation:

- `renderer.py`: `list_available_themes()` confirmed to return only on-disk themes (lines 73-108). The `all_hljs_themes` import is removed.
- `web.html.j2`: Theme dropdown confirmed to be a flat list with `data-hljs-theme` attributes (lines 340-349). Build button confirmed to have no emoji (line 351). Footer confirmed to have no emoji (line 381).
- CLI behavior unchanged: `render_deck()` still calls `get_hljs_theme_info()` for hljs theme resolution.
