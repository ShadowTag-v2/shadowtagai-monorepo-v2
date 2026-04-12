# Dockerfile for Flying n-autoresearch/Kosmos/BioAgents Server (ShadowTag Juggernaut)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY n-autoresearch/Kosmos/BioAgentss-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY n-autoresearch/Kosmos/BioAgentss-server/src/ src/

# Copy UI (Face)
COPY agent-manager-ui/ /agent-manager-ui/

# Environment Variables
ENV PORT=8080
# ensure 'aiyou' (in src/libs) is importable
ENV PYTHONPATH=/app/src:/app/src/libs

# Run
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
