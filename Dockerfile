# Stage 1: Builder
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual env
RUN uv sync --no-dev --frozen

# Copy application code
COPY hotslice/ hotslice/
COPY themes/ themes/

# Install the project itself
RUN uv sync --no-dev --frozen

# Stage 2: Runtime
FROM python:3.14-slim

# Create non-root user
RUN groupadd -r hotslice && useradd -r -g hotslice -d /app -s /sbin/nologin hotslice

WORKDIR /app

# Copy the virtual env and app code from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/hotslice /app/hotslice
COPY --from=builder /app/themes /app/themes
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Put the venv on PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER hotslice

EXPOSE 8000

CMD ["uvicorn", "hotslice.web:app", "--host", "0.0.0.0", "--port", "8000"]
