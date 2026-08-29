FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY hotslice/ hotslice/

RUN uv sync --no-dev --frozen

FROM python:3.14-slim

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY --from=builder /app/hotslice hotslice/

# renderer.py resolves bundled themes as <package dir>/../themes, so the themes
# tree has to sit beside the package rather than inside it.
COPY themes/ themes/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp

# Unprivileged, and deliberately no VOLUME: a conversion is read → parse →
# render → respond, entirely in memory, so the container holds no state worth
# persisting and can run with a read-only root filesystem. docker-compose.yml
# does exactly that. Keep it that way — if something here ever needs to write,
# give it a tmpfs rather than a bind mount to the array.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin hotslice
USER 10001

EXPOSE 8000

# hotslice-web, not a bare `uvicorn` invocation, so the proxy_headers /
# forwarded_allow_ips settings that keep the /mcp redirect on https live in
# web.py alone (see AGENTS.md).
CMD ["hotslice-web"]
