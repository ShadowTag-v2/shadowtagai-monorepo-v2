#!/bin/bash
set -e

# ShadowTag Omega V7: Cloud Run Deployment script
PROJECT_ID="shadowtag-omega-v2"
SERVICE_NAME="autonomous-sentinel"
REGION="us-central1"

echo "🚀 INITIATING DEPLOYMENT: $SERVICE_NAME..."

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GCP_PROJECT_ID=$PROJECT_ID

echo "✅ DEPLOYMENT COMPLETE. Sentinel is live."
