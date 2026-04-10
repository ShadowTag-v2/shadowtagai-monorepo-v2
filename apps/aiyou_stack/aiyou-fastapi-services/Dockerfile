# ==============================================================================
# STAGE 1: Builder
# ==============================================================================
FROM python:3.11-slim AS builder

# Copy the uv binary directly from Astral's official Docker image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Optimize uv for Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 1. Copy ONLY the dependency files first to leverage Docker layer caching.
# If your dependencies don't change, Docker skips this entire step on the next build!
COPY pyproject.toml uv.lock ./

# 2. Install dependencies into a local .venv
# --frozen: Fails if uv.lock is out of sync with pyproject.toml
# --no-dev: Excludes Ruff, basedpyright, and testing libraries to save space
# --no-install-project: Installs only the dependencies, not the app itself yet
RUN uv sync --frozen --no-dev --no-install-project

# 3. Copy the rest of the FastAPI application code
COPY . .

# 4. Install the application code itself into the .venv
RUN uv sync --frozen --no-dev

# ==============================================================================
# STAGE 2: Production Runtime
# ==============================================================================
FROM shadowtag/uvicorn-base:latest AS runtime

WORKDIR /app

# Prevent Python from writing .pyc files or buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy ONLY the pre-built virtual environment and application code from the builder.
# This leaves behind the `uv` binary, build caches, and system dependencies!
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Expose the standard FastAPI port
EXPOSE 8000

# Drop root privileges for better security (Best Practice)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Start Uvicorn directly from the virtual environment
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
