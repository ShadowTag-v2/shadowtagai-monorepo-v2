#!/bin/bash
# Deploy UphillSnowball (SovereignKosmos Edition) to Cloud Run
# PROJECT_ID: acquired-jet-478701-b3
# SERVICE: uphillsnowball-sovereign

set -e

echo "🚀 Deploying UphillSnowball (Sovereign Kosmos)..."

# 1. Configuration
PROJECT_ID="shadowtag-omega-v2"
SERVICE_NAME="uphillsnowball-sovereign"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# 2. Build
echo "📦 Building Container..."
gcloud builds submit --tag $IMAGE --project $PROJECT_ID

# 3. Deploy
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_MODEL=gemini-2.5-pro,PYTHONPATH=/app" \
  --service-account="sovereign-agent@$PROJECT_ID.iam.gserviceaccount.com"

echo "✅ Deployment Complete!"
echo "➡️  Endpoint: $(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')"
