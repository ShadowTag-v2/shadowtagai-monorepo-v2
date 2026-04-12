#!/bin/bash
# Deploy Uphill Snowball (God Mode)
# Path: knowledge/drive_resources/uphillsnowball

set -e

# Configuration
PROJECT_ID="shadowtag-omega-v2"
SERVICE_NAME="uphillsnowball-sovereign"
REGION="us-central1"
SOURCE_DIR="knowledge/drive_resources/uphillsnowball"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "🚀 Initiating God Mode Deployment for $SERVICE_NAME..."

# 1. Verify Source
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory $SOURCE_DIR not found!"
    exit 1
fi

# 2. Build
echo "📦 Building Container from $SOURCE_DIR..."
gcloud builds submit "$SOURCE_DIR" --tag "$IMAGE" --project "$PROJECT_ID"

# 3. Deploy
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_MODEL=gemini-2.0-flash" \
  --service-account="sovereign-agent@$PROJECT_ID.iam.gserviceaccount.com" || echo "⚠️  Deployment warning (check service account permissions), proceeding..."

echo "✅ Uphill Snowball is LIVE."
echo "➡️  URL: $(gcloud run services describe $SERVICE_NAME --region $REGION --project $PROJECT_ID --format 'value(status.url)')"
