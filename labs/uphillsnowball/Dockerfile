# Dockerfile — The Sealed Apple Box
#
# Multi-stage build:
#   Stage 1 (rust-builder): Compile ast-grep (sg) from Rust source
#   Stage 2 (cpp-builder):  Compile Midas C++ IPC client
#   Stage 3 (runtime):      Python runtime with all dependencies
#
# The final image contains:
#   - ast-grep (sg) binary for zero-latency AST mitigation
#   - Midas C++ binary for ZMQ IPC quant operations
#   - Python Temporal workers for durable execution
#   - Playwright/Chromium for Scrapling web automation

# ── Stage 1: ast-grep from Rust ────────────────────────────────
FROM rust:1.78-slim AS rust-builder
RUN cargo install ast-grep --locked

# ── Stage 2: Midas C++ from GCC ───────────────────────────────
FROM gcc:13 AS cpp-builder
RUN apt-get update && apt-get install -y libzmq3-dev nlohmann-json3-dev && rm -rf /var/lib/apt/lists/*
COPY src/native/ /usr/src/native/
WORKDIR /usr/src/native/core
RUN g++ -std=c++17 -O2 -o /usr/src/midas_ipc midas_ipc_client.cpp -lzmq

# ── Stage 3: Python Runtime ───────────────────────────────────
FROM python:3.12-slim

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl jq ffmpeg libnss3 libzmq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy compiled binaries from builder stages
COPY --from=rust-builder /usr/local/cargo/bin/sg /usr/local/bin/sg
COPY --from=cpp-builder /usr/src/midas_ipc /usr/local/bin/midas_ipc

# Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium --with-deps

# Application code
COPY . /app/

# Runtime configuration
ENV PORT=8080
ENV HEALTH_PORT=8080
ENV METRICS_PORT=9090
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8080
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

# Start Temporal worker
CMD ["python", "-m", "src.worker"]
