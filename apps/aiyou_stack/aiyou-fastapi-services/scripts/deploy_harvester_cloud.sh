#!/bin/bash
set -e

# CONFIG
PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/harvester:latest"
JOB_NAME="harvester-job"

echo ">>> 📦 PACKAGING HARVESTER (TROJAN HORSE)..."
# Build the image with the current repo context (including .git)
# Note: The Dockerfile (or default builder) needs to run pip install.
# Since we are using 'gcloud builds submit' with a default builder,
# we should ideally have a Dockerfile.
# For now, we will assume a Dockerfile exists or create one.
# Let's verify if a Dockerfile exists. If not, we should create it.
echo "Checking for Dockerfile..."
if [ ! -f Dockerfile ]; then
    echo "Creating Dockerfile..."
    cat <<EOF > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["python", "scripts/harvest_docs_producer.py"]
EOF
fi

gcloud builds submit --tag $IMAGE . --project $PROJECT_ID

echo ">>> 🚀 DEPLOYING CLOUD RUN JOB..."
# Deploy with Direct VPC Egress to talk to Private Kafka
gcloud run jobs deploy $JOB_NAME \
  --image $IMAGE \
  --region $REGION \
  --project $PROJECT_ID \
  --vpc-network default \
  --vpc-subnet default \
  --vpc-egress all-traffic \
  --task-timeout 60m \
  --set-env-vars PROJECT_ID=$PROJECT_ID

echo ">>> 🦍 EXECUTING INGESTION..."
gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID

echo ">>> ✅ Harvester launched in the Cloud. Check logs via: gcloud run jobs logs read $JOB_NAME"
