FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY src/ ./src/

# Cloud Run expects PORT env
ENV PORT=8080
ENV APP_ENV=production

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import httpx; r=httpx.get('http://localhost:8080/health'); assert r.status_code==200" || exit 1

CMD ["uvicorn", "api.fastapi_kovel_enclave:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
