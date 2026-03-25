# Documentation Summary

## What Changed

Updated `README.md` to reflect the new landing page content added to the hotslice web server.

## Files Modified

### README.md

**`hotslice serve` section (lines 136-140):** Revised the description to cover the three new landing page features:

1. The landing page now explains what hotslice is and how to get started (header description paragraph).
2. Three info cards below the form cover the main usage paths: CLI quick start, the web UI and API endpoints, and MCP server connection config.
3. The footer includes a GitHub Sponsors link for the `pid1` account.

**API endpoints table:** Changed the `GET /` description from "Upload form (HTML)" to "Landing page with upload form (HTML)" to reflect that the root page now serves more than the upload form alone.

### AGENTS.md

No changes. The implementation was a single-file HTML/CSS change to `hotslice/templates/web.html.j2` with no new hidden coupling, design decisions, or gotchas that agents need to know about. The AGENTS.md is already over 200 lines; adding content about a visual-only template update would increase noise without preventing mistakes.

## Verification

- Confirmed the README description matches the actual template content in `web.html.j2` (lines 414-536).
- Confirmed the three info cards (Quick Start, Web UI, MCP Server) and the sponsor link exist in the template as described.
- Confirmed no Python code, JavaScript, or Jinja2 logic changed, so no code-level documentation updates are needed.
