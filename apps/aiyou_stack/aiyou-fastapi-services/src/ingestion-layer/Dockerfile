FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ingestion_orchestrator.py .

# Create workspace and cache directories
RUN mkdir -p /workspace /cache && \
    chown -R 1000:3000 /workspace /cache

# Set user
USER 1000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "print('healthy')"

# Run orchestrator
CMD ["python", "-u", "ingestion_orchestrator.py"]
