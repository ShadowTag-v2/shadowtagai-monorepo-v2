#!/bin/bash
# Deploy Real Uphill Snowball (Next.js Frontend)
# Source: knowledge/drive_resources/uphillsnowball/frontend

set -e

# Configuration
PROJECT_ID="shadowtag-omega-v2"
SERVICE_NAME="uphillsnowball-sovereign"
REGION="us-central1"
SOURCE_ROOT="knowledge/drive_resources/uphillsnowball/frontend"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "🚀 Initiating Real Deployment for $SERVICE_NAME (Next.js)..."

# 1. Verify Source
if [ ! -d "$SOURCE_ROOT" ]; then
    echo "❌ Error: Source directory $SOURCE_ROOT not found!"
    exit 1
fi

# 2. Build
echo "📦 Building Container from $SOURCE_ROOT..."
gcloud builds submit "$SOURCE_ROOT" --tag "$IMAGE" --project "$PROJECT_ID"

# 3. Deploy
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --allow-unauthenticated \
  --service-account="sovereign-agent@$PROJECT_ID.iam.gserviceaccount.com"

echo "✅ Real Uphill Snowball IS LIVE."
echo "➡️  URL: $(gcloud run services describe $SERVICE_NAME --region $REGION --project $PROJECT_ID --format 'value(status.url)')"
