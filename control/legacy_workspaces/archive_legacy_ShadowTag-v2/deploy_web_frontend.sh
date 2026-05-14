#!/bin/bash
set -e

PROJECT_ID="shadowtag-omega-v4"
REGION="us-central1"
SERVICE_NAME="shadowtag-web"
SOURCE_DIR="apps/shadowtag-web"
IMAGE_TAG="us-central1-docker.pkg.dev/$PROJECT_ID/cloud-workstations-images/$SERVICE_NAME:latest"

echo "🚀 Deploying $SERVICE_NAME (Docker Strategy)..."
echo "📍 Project: $PROJECT_ID"
echo "📍 Region: $REGION"
echo "📍 Source: $SOURCE_DIR"
echo "📍 Image: $IMAGE_TAG"

# Ensure we are in the root
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory $SOURCE_DIR not found. Run from valid root."
    exit 1
fi

# 1. Build Container (Explicitly using the Dockerfile in apps/shadowtag-web)
echo "📦 Building Container Image..."
gcloud builds submit $SOURCE_DIR \
    --tag $IMAGE_TAG \
    --project $PROJECT_ID

# 2. Deploy Container
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_TAG \
  --project $PROJECT_ID \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --service-account 767252945109-compute@developer.gserviceaccount.com

echo "✅ Deployment Complete."
echo "🌍 Live URL: $(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --project $PROJECT_ID --format 'value(status.url)')"
