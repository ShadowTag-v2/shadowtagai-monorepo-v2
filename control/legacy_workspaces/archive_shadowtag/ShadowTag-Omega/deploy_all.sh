#!/bin/bash
set -e

echo ">>> 🏗️  Generating Dockerfiles for the Pipeline..."

# 1. Define Bridge Dockerfile (Node.js)
# Located in ../jetski-bridge/Dockerfile
cat <<EOF > ../jetski-bridge/Dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY bridge-server.js .
CMD ["node", "bridge-server.js"]
EOF

# 2. Define Agent Dockerfile (Python)
# Root of ShadowTag-Omega
cat <<EOF > Dockerfile.agent
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the libs (Logic)
COPY libs/ ./libs/
# Copy the apps (Server)
COPY apps/ ./apps/
# Copy the beads (Memory)
COPY .beads/ ./.beads/
# Copy the source (if distinct)
COPY src/ ./src/

# Cloud Run Native Entrypoint (Dynamic Discovery)
# Checks for main.py in common locations
CMD ["sh", "-c", "if [ -f apps/n-autoresearch/Kosmos/BioAgentss-server/src/main.py ]; then uvicorn apps.n-autoresearch/Kosmos/BioAgentss-server.src.main:app --host 0.0.0.0 --port 8080; else uvicorn src.main:app --host 0.0.0.0 --port 8080; fi"]
EOF

echo ">>> 🚀 Triggering Cloud Build (Infra + Code)..."
gcloud builds submit --config cloudbuild.yaml .

echo ">>> ✅ DEPLOYMENT COMPLETE."
echo "Your Agent Platform is live. Check Cloud Run console for the URL."
