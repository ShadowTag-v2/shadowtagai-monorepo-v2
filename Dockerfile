# Pnkln Ultrathink Framework - Production Dockerfile
# Version: 1.0.0
# Philosophy: Minimal, secure, optimized

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pnkln/ ./pnkln/
COPY shadowtagai/ ./shadowtagai/
COPY api/ ./api/
COPY data/ ./data/

# Create non-root user for security
RUN useradd -m -u 1000 pnkln && \
    chown -R pnkln:pnkln /app && \
    mkdir -p /app/data && \
    chown -R pnkln:pnkln /app/data

# Switch to non-root user
USER pnkln

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
