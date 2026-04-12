# ANTIGRAVITY :: n-autoresearch/Kosmos/BioAgentss Container
# 650-Agent Squadron for Cloud Run

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment configuration
ENV PORT=8600
ENV PYTHONPATH=/app:/app/src
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run n-autoresearch/Kosmos/BioAgentss server
CMD ["python", "bin/n-autoresearch/Kosmos/BioAgentss-server"]
