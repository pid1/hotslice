#!/usr/bin/env bash
# Stages the Worker bundle. wrangler runs this before every `dev` and
# `deploy` (build.command in wrangler.jsonc), under Workers Builds and the
# fallback workflow alike.

set -euo pipefail
cd "$(dirname "$0")"

# Wrangler does not follow symlinks, so the package and themes are copied in
# beside the entrypoint (both paths are gitignored). renderer.py resolves
# bundled themes as <package dir>/../themes, which this layout preserves.
rm -rf src/hotslice src/themes
cp -R ../hotslice ../themes src/
find src -name __pycache__ -prune -exec rm -rf {} +

# Identifies the deployed commit so the fallback workflow can tell whether
# Cloudflare already published this tree; entry.py serves it at /.build-id.
#
# Read it from the checkout rather than the environment. Workers Builds sets
# WORKERS_CI_COMMIT_SHA to the *branch name* for a manually started build, and
# the fallback compares this value against github.sha -- so trusting the
# variable would leave a deployed site permanently looking stale and make the
# fallback redeploy on every push, which is precisely what it exists to avoid.
sha=$(git rev-parse HEAD 2>/dev/null || echo "${WORKERS_CI_COMMIT_SHA:-${GITHUB_SHA:-local}}")
printf 'BUILD_ID = "%s"\n' "$sha" > src/build_id.py
