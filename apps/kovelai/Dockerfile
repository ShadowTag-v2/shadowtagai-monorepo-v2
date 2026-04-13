# ════════════════════════════════════════════════════════════
# KovelAI — 1-Click Appliance Docker Image
# Secure, privilege-preserving legal AI proxy
#
# Security posture:
#   - Non-root execution
#   - No NODE_OPTIONS propagation (Heppner compliance)
#   - Read-only filesystem compatible
#   - No pip cache, no dev tools, no shell history
#   - Anti-forensic: PYTHONDONTWRITEBYTECODE=1
# ════════════════════════════════════════════════════════════

# ── Stage 1: Builder ──────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies only (removed after this stage)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Create virtualenv for clean separation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python deps (cached layer if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: prevent bytecode artifacts and buffer delays
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    # Anti-exfiltration: block NODE_OPTIONS injection vector
    NODE_OPTIONS="" \
    # Default port (overridable)
    PORT=8080

# Create non-root user
RUN groupadd -r kovelai && \
    useradd -r -g kovelai -d /app -s /sbin/nologin kovelai

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
WORKDIR /app
COPY api/ ./api/
COPY agent/ ./agent/

# Set ownership
RUN chown -R kovelai:kovelai /app

# Drop to non-root
USER kovelai

# Health check (S.E.U. proxy health endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:${PORT}/api/v1/health'); exit(0 if r.status_code == 200 else 1)"

# Expose both API and Agent ports
EXPOSE 8080 8000

# Default: start the S.E.U. proxy API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2", "--log-level", "info"]
