# PNKLN Core Stack - Ingestion Layer Container
# Multi-stage build for optimized Python container

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY ingestion/ ./ingestion/
COPY shared/ ./shared/

# Add Python user packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Set Python to run in unbuffered mode (better for logging)
ENV PYTHONUNBUFFERED=1

# Default environment (override in k8s)
ENV LOG_LEVEL=INFO
ENV ENABLE_STRUCTURED_LOGGING=true

# Health check endpoint (for future FastAPI integration)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run ingestion pipeline by default
ENTRYPOINT ["python", "-m", "ingestion.main"]

# Allow passing arguments to main.py
CMD []
