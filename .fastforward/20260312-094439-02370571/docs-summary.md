# Documentation Summary

## Feature

Default build output changed from `dist/index.html` to `<input_stem>.html` in the current working directory.

## Changes Made

### README.md

Six updates to reflect the new default output behavior:

1. **Quick Start section**: Changed `open dist/index.html` to `open slides.html` with a comment clarifying the default output convention.
2. **CLI Reference table**: Updated the default for `-o, --output` from `dist/index.html` to `<input_stem>.html`. Added an explanatory paragraph below the table describing the dynamic default.
3. **User config example**: Removed `output` from the TOML example since it is now optional. Added a note explaining that `output` can be set explicitly to force a fixed path.
4. **Project config example**: Removed `output` from the TOML example to match the actual `hotslice.toml` in the repo. Added a note about explicit overrides.
5. **Available Commands table**: Updated the `build` row from "Build demo deck to dist/" to "Build demo deck to demo.html".
6. **Navigation deep-link example**: Changed `index.html#3` to `slides.html#3`.

### examples/demo.md

Updated the Quick Start code block in the demo slide deck from `open dist/index.html` to `open slides.html`.

### AGENTS.md

No changes needed. The implementor already updated all three relevant sections:
- Commands table: "Build demo deck to demo.html"
- "For AI Agents" section: references `demo.html`
- Building examples: shows `# -> slides.html`

## Verification

- Confirmed all code changes match the documentation updates by reading `hotslice/cli.py`, `hotslice/config.py`, and `hotslice.toml`.
- Searched for remaining `dist/index.html` references. The only remaining instance is in README.md line 201, which is intentional: it shows an example of how to set an explicit output path via config.
- QA report confirms all tests pass and behavior matches documentation.
