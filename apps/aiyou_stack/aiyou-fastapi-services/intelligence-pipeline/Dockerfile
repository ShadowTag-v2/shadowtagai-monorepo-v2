# PNKLN Intelligence Pipeline - Production Dockerfile
# Multi-stage build for optimized image size
# ATP 5-19 RA-1 Compliant | Ethical Scraping

# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/

# Create non-root user for security
RUN useradd -m -u 1000 pnkln && \
    chown -R pnkln:pnkln /app

USER pnkln

# Health check (for debugging - CronJob doesn't use this)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set Python to run in unbuffered mode for real-time logging
ENV PYTHONUNBUFFERED=1

# Default command (overridden by CronJob)
CMD ["python", "-m", "src.pipeline.ingestion"]

# Labels for metadata
LABEL maintainer="intelligence@pnkln.ai"
LABEL version="1.0.0"
LABEL description="PNKLN Intelligence Pipeline - Nightly intelligence gathering with ethical scraping"
LABEL atp-5-19="ra-1"
LABEL component="intelligence-pipeline"
