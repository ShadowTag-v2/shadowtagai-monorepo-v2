# ── Stage 1: Dependencies ──────────────────────────────────────────────────
FROM python:3.14-slim AS deps

WORKDIR /app

# Install dependencies in isolated layer (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ───────────────────────────────────────────────────────
FROM python:3.14-slim AS runtime

# OCI image labels
LABEL org.opencontainers.image.title="CounselConduit" \
      org.opencontainers.image.description="Privileged Legal AI — Kovel Enclave" \
      org.opencontainers.image.version="3.3.2" \
      org.opencontainers.image.vendor="ShadowTagAI" \
      org.opencontainers.image.source="https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball" \
      org.opencontainers.image.licenses="PROPRIETARY"

WORKDIR /app

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application code
COPY api/ ./api/
COPY src/ ./src/
COPY static/ ./static/
COPY middleware/ ./middleware/

# Non-root user (Cor.30 R19)
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

# Cloud Run expects PORT env
ENV PORT=8080
ENV APP_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

# Health check (Item 16)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import httpx; r=httpx.get('http://localhost:8080/health'); assert r.status_code==200" || exit 1

# Item 21: Structured JSON logging (Cloud Run auto-parses)
CMD ["uvicorn", "api.fastapi_kovel_enclave:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2", "--log-level", "info"]
