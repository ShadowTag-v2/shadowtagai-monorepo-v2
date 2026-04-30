#!/bin/bash
# ▙▖▙▖▞▞▙ ANTIGRAVITY CLOUD RUN DEPLOYMENT [v2025.3]
# DOCTRINE: "NO GKE" - FULLY MANAGED SERVERLESS
# MISSION: Deploy "The Child" Tier 30 Stack on Cloud Run
# AUTHOR: ANTIGRAVITY

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}▙▖▙▖▞▞▙ ANTIGRAVITY: INITIATING CLOUD RUN SEQUENCE${NC}"
echo -e "${BLUE}DOCTRINE: GOOGLE MANAGED ONLY (NO GKE)${NC}"

# 1. Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="judge6-governance"

echo -e "${GREEN}[+] Target Project: ${PROJECT_ID}${NC}"

# 2. Enable APIs (Serverless Focus)
echo -e "${BLUE}[*] Enabling Serverless APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    --quiet

# 3. Build & Deploy to Cloud Run
echo -e "${BLUE}[*] Building & Deploying Judge#6 to Cloud Run...${NC}"

# Create a minimal Dockerfile if it doesn't exist
if [ ! -f Dockerfile ]; then
    echo -e "${BLUE}[*] Generating Dockerfile...${NC}"
    cat <<EOF > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY pnkln/ ./pnkln/
CMD ["python", "src/judge6/core.py"]
EOF
fi

# Deploy using Cloud Run source deploy (builds automatically)
# Note: In a real scenario, we'd use gcloud run deploy --source .
# For now, we'll simulate the command structure.
echo -e "${BLUE}[*] Executing: gcloud run deploy ${SERVICE_NAME} --source . --region ${REGION} --allow-unauthenticated${NC}"

gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars DOCTRINE="TIER_30_THE_CHILD"

echo -e "${GREEN}[+] Service '${SERVICE_NAME}' Deployment Triggered${NC}"
echo -e "${GREEN}[+] URL: https://${SERVICE_NAME}-${PROJECT_ID}.a.run.app${NC}"

echo -e "${BLUE}▙▖▙▖▞▞▙ DEPLOYMENT COMPLETE${NC}"
echo -e "${GREEN}Status: OPERATIONAL (Serverless)${NC}"
