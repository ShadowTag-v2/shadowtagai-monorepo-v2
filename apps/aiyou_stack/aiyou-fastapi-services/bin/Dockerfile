# n-autoresearch/Kosmos/BioAgentss Server Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for n-autoresearch/Kosmos/BioAgentss
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic

# Copy the server script
COPY n-autoresearch/Kosmos/BioAgentss-server /app/bin/n-autoresearch/Kosmos/BioAgentss-server

# Copy agents and lib if needed
COPY ../agents/ /app/agents/ 2>/dev/null || true
COPY ../lib/ /app/lib/ 2>/dev/null || true

# Expose port (Cloud Run uses PORT env var, default 8080)
EXPOSE 8080

# Run the server
CMD ["python", "/app/bin/n-autoresearch/Kosmos/BioAgentss-server"]
