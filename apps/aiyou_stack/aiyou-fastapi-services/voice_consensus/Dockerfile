# Production Dockerfile for Consensus Orchestrator API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies (skip optional voice deps for API-only)
RUN pip install --no-cache-dir \
    aiohttp \
    anthropic \
    google-generativeai \
    openai \
    fastapi \
    uvicorn[standard] \
    pydantic \
    google-cloud-storage \
    PyYAML \
    python-dotenv

# Copy application code
COPY atomic_consensus_orchestrator.py /app/
COPY message_consensus.py /app/
COPY cost_tracker.py /app/
COPY transcript_archive.py /app/
COPY api_server.py /app/
COPY claude_code_memory.py /app/
COPY vertex_gke_deployment.py /app/

# Create memory directory
RUN mkdir -p /memory /data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run API server
CMD ["python", "api_server.py"]
