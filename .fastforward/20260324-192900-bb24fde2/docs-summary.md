# Documentation Summary

## Changes Made

### README.md

1. **Added upload restrictions paragraph** to the `hotslice serve` section (after the web UI description). Documents the `/convert` endpoint's new security constraints: accepted file extensions (`.md`, `.markdown`, `.txt`), 2 MB size limit, and UTF-8 requirement. These are user-facing behaviors added by the security hardening workstream.

2. **Added `/mcp` endpoint to the API table.** The MCP server endpoint was missing from the API endpoints table despite being mounted on the web server. Added a row linking to the MCP Server section for details.

### AGENTS.md

1. **Added theme name validation regex coupling.** Documented that `_THEME_NAME_RE` (`^[a-zA-Z0-9][a-zA-Z0-9_-]*$`) is defined independently in both `hotslice/web.py` and `hotslice/mcp_server.py`. Both files also re-validate frontmatter theme overrides and apply matching size limits. Agents changing validation rules in one file must update the other.

2. **Added MCP mount path coupling.** Documented that `streamable_http_path="/"` in `hotslice/mcp_server.py` is coupled with `app.mount("/mcp", ...)` in `hotslice/web.py`. Changing either without updating the other breaks the endpoint or doubles the prefix.

## Verified Against Implementation

- Confirmed `hotslice/mcp_server.py` line 176: `_THEME_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")`
- Confirmed `hotslice/web.py` line 22: same regex pattern
- Confirmed `hotslice/mcp_server.py` line 20: `streamable_http_path="/"`
- Confirmed `hotslice/web.py` line 140: `app.mount("/mcp", mcp_server.streamable_http_app())`
- Confirmed `hotslice/web.py` lines 21-23: `_MAX_UPLOAD_SIZE = 2 * 1024 * 1024`, `_ALLOWED_EXTENSIONS = {".md", ".markdown", ".txt"}`
- Confirmed `hotslice/web.py` lines 105-111: UTF-8 decode validation
- Confirmed MCP Server section in README.md matches actual capabilities (prompt: `write_presentation`, tools: `build_presentation`, `list_themes`)

## No Changes Needed

The implementation phase already completed these documentation updates correctly:
- README.md: Docker section removed, MCP Server section added with HTTP/stdio connection examples and capabilities table
- AGENTS.md: Dockerfile removed from Key Files table, `hotslice/mcp_server.py` added
