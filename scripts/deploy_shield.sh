#!/bin/bash
set -e

echo "Deploying CR Shield 17-Layer Interceptor to Global Edge..."

PROJECT_ID="shadowtag-omega-v4"
REGION="us-central1"
SERVICE_NAME="edge-shield-b2b"

gcloud run deploy $SERVICE_NAME \
  --source ./apps/aiyou_stack/shield \
  --project $PROJECT_ID \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --max-instances 10

echo "Deployment triggered. Traffic interceptor is warming."
