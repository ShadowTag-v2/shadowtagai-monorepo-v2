#!/bin/bash
set -e

PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
SERVICE_NAME="judge-six-core"

echo ">>> 🧠 DEPLOYING JUDGE 6 CORE (Brain Only) TO CLOUD RUN..."

# Build the Core Image using the root Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found in $(pwd)"
    exit 1
fi

gcloud builds submit \
  --project=$PROJECT_ID \
  --tag gcr.io/$PROJECT_ID/judge-core:latest \
  .

# Deploy Standard Service (No Sidecar)
gcloud run deploy $SERVICE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --image gcr.io/$PROJECT_ID/judge-core:latest \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300s \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,JETSKI_URL="http://localhost:8081"

echo "    ✅ JUDGE CORE DEPLOYED."
echo "    Target: https://$SERVICE_NAME-uc.a.run.app"
