# V2X Mesh Service - Production Dockerfile
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 v2xuser && chown -R v2xuser:v2xuser /app
USER v2xuser

# Expose ports
EXPOSE 8010 8011 8012
# 8010: HTTP API
# 8011: WebSocket (real-time mesh updates)
# 8012: Metrics/Health

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8012/health')"

# Run application
CMD ["python", "api.py"]
