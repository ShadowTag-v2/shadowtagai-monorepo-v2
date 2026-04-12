#!/usr/bin/env bash
# title: Deploy Kafka Consumer (Omega Protocol)
# description: Deploys the Kafka Consumer to Cloud Run with "Insanely Great" precision.
# author: Antigravity (Steve Jobs Persona)

set -euo pipefail

# --- Configuration (The "Soul" of the deployment) ---
PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
CLUSTER_NAME="my-cluster"
TOPIC_ID="test-topic"
IMAGE_NAME="kafka-consumer"
SERVICE_NAME="kafka-consumer"
REPO_NAME="cloud-run-source-deploy"

# --- Aesthetics (Visual Feedback) ---
GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

log() { echo -e "${BOLD}${GREEN}==> ${1}${NC}"; }
error() { echo -e "${BOLD}${RED}ERROR: ${1}${NC}"; exit 1; }

# --- Execution ---

log "Ignition: Deploying to ${PROJECT_ID}..."

# 1. Verify Project Context
CURRENT_PROJECT=$(gcloud config get-value project)
if [[ "$CURRENT_PROJECT" != "$PROJECT_ID" ]]; then
    log "Switching context to ${PROJECT_ID}..."
    gcloud config set project "$PROJECT_ID"
fi

# 2. Artifact Registry (The Canvas)
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" &>/dev/null; then
    log "Creating Artifact Registry: ${REPO_NAME}..."
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Docker repository for Kafka Consumer"
else
    log "Artifact Registry exists. Good."
fi

# 3. Build (The Craft)
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"
log "Building Container Image: ${IMAGE_URI}..."
gcloud builds submit --tag "$IMAGE_URI" . || error "Build failed."

# 4. Deploy (The Release)
log "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_URI" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "PROJECT_ID=${PROJECT_ID},REGION=${REGION},CLUSTER_NAME=${CLUSTER_NAME},TOPIC_ID=${TOPIC_ID}" \
    --service-account "kafka-worker-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    || error "Deployment failed."

log "Deployment Complete. It is insanely great."
