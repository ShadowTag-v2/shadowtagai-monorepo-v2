#!/bin/bash
export GCP_PROJECT_ID="shadowtag-omega-v4"
IMAGE_URL="gcr.io/$GCP_PROJECT_ID/temporal-worker:latest"

echo ">>> 🚀 Building and pushing Temporal Worker image..."
docker build -t $IMAGE_URL -f infrastructure/temporal.Dockerfile .
docker push $IMAGE_URL

echo ">>> ⚡ Deploying Temporal Worker to Cloud Run Worker Pools..."
gcloud beta run worker-pools deploy shadowtag-temporal-worker \
  --image $IMAGE_URL \
  --region us-central1 \
  --project $GCP_PROJECT_ID \
  --set-env-vars TEMPORAL_ADDRESS="namespace.tmprl.cloud:7233",TEMPORAL_NAMESPACE="namespace"

echo ">>> ✅ Worker pool deployed successfully."
