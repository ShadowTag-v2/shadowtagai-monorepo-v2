# Nightly Intel Pipeline - GKE Optimized Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/repos data/papers data/briefings storage logs

# Set permissions for non-root user
RUN useradd -m -u 1000 pipeline && \
    chown -R pipeline:pipeline /app

# Switch to non-root user
USER pipeline

# Health check (optional for CronJob, useful for testing)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden in CronJob)
CMD ["python", "main.py"]

# Labels for metadata
LABEL maintainer="PNKLN Core Stack" \
      version="1.0.0" \
      description="Nightly Intel Pipeline - Ethical Intelligence Gathering" \
      component="ingestion-layer"
