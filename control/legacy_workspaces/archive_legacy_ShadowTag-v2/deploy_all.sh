#!/bin/bash
set -e

echo ">>> 🏗️  Generating Dockerfiles for the Pipeline..."

# 1. Define Bridge Dockerfile (Node.js)
# Note: copying everything in jetski-bridge to ensure extension files are present
cat <<EOF > Dockerfile.bridge
FROM node:20-slim
WORKDIR /app
COPY jetski-bridge/package*.json ./
RUN npm install
COPY jetski-bridge/ ./
CMD ["node", "bridge-server.js"]
EOF

# 2. Define Agent Dockerfile (Python)
# Note: Using python:3.11-slim as base
# CRITICAL: We copy 'libs/' (The Arsenal) and 'src/' (The Brain)
cat <<EOF > Dockerfile.agent
FROM python:3.11-slim
WORKDIR /app
# Install dependencies including the new 'playwright' and 'google-genai'
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir fastapi uvicorn google-genai playwright
RUN playwright install --with-deps chromium

COPY src/ ./src/
COPY libs/ ./libs/
COPY .beads/ ./.beads/

# Cloud Run Native Entrypoint
# Pointing to src/libs/aiyou/main.py. 
# PYTHONPATH must include /app (root) to find 'libs' and 'src'
ENV PYTHONPATH=/app:/app/src
CMD ["uvicorn", "src.libs.aiyou.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

echo ">>> 🚀 Triggering Cloud Build (Infra + Code)..."
gcloud builds submit --config cloudbuild.yaml .

echo ">>> ✅ DEPLOYMENT COMPLETE."
echo "Your Agent Platform is live. Check Cloud Run console for the URL."
