#!/bin/bash
set -e

# ==============================================================================
# 🏛️ PROVISIONING PROTOCOL: IRONWOOD & AXION (SOVEREIGN STACK)
# ==============================================================================
# 1. Brain: Ironwood (TPU v7) via Gemini 3.0 Flash (Inference)
# 2. Body: Axion (Arm CPU) via Cloud Run (Hosting)
# ==============================================================================

PROJECT_ID="shadowtag-omega-v4"
REGION="us-central1"
REPO_NAME="shadowtag-artifacts"
SERVICE_NAME="shadowtag-web"
SOURCE_DIR="apps/shadowtag-web"
IMAGE_TAG="us-central1-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME:latest"

echo "🏔️  Initiating Sovereign Stack Provisioning..."
echo "📍 Project: $PROJECT_ID"
echo "📍 Region: $REGION"
echo "📍 Repository: $REPO_NAME"

# 1. Enable Critical APIs
echo "🛠️  Enabling Sovereign APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    compute.googleapis.com \
    > /dev/null 2>&1
echo "✅ APIs Enabled."

# 2. Recreate Artifact Registry (The Vault)
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "📦 Creating Artifact Registry: $REPO_NAME..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="ShadowTag Sovereign Artifacts (Axion Optimized)" \
        --project=$PROJECT_ID
else
    echo "✅ Artifact Registry ($REPO_NAME) exists."
fi

# 3. Build Container (Axion/Arm64 optimized)
# Note: Using standard build for reliability, running on Cloud Run Gen 2
echo "🏗️  Building Container Image (Ironwood/Axion Protocol)..."
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory $SOURCE_DIR not found."
    exit 1
fi

gcloud builds submit $SOURCE_DIR \
    --tag $IMAGE_TAG \
    --project $PROJECT_ID

# 4. Deploy to Cloud Run (The Body)
echo "🚀 Deploying $SERVICE_NAME to Cloud Run (Axion-Ready)..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --project $PROJECT_ID \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 3000 \
    --memory 1Gi \
    --execution-environment=gen2 \
    --service-account 767252945109-compute@developer.gserviceaccount.com

# 5. Restore Domain Mapping
echo "🔗 Restoring Domain Mapping (www.shadowtagai.com)..."
# Attempt to create mapping, ignoring if it already exists (though it might have been deleted)
gcloud beta run domain-mappings create \
    --service $SERVICE_NAME \
    --domain www.shadowtagai.com \
    --region $REGION \
    --project $PROJECT_ID \
    --platform managed || echo "⚠️  Domain mapping might already exist or failed. Check console."

echo "✅ Sovereign Stack Provisioned."
echo "🌍 Live URL: $(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --project $PROJECT_ID --format 'value(status.url)')"
