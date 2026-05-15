#!/bin/bash
set -e

# ========================================================================================
# UPHILL SNOWBALL: Cor.58 2.0 Deployment Actuator
# Orchestrates ShadowTagAI deployment to Google Cloud Run (Pure Serverless Doctrine)
# ========================================================================================

PROJECT_ID="shadowtag-omega-v2"
MY_EMAIL="founder@shadowtagai.com"
REGION="us-central1"
REPO_NAME="shadowtag-omega"

echo "🏔️  Initiating Uphill Snowball Protocol..."
echo "📍 Project: $PROJECT_ID"
echo "📍 Region: $REGION"

# 0. Set Project Context & Quota
gcloud config set project $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID

# 1. Enable Required APIs (Including AI Ultra Bypass)
echo "🛠️  Enabling APIs (Cloud Run, Artifact Registry, AI Companion)..."
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    cloudaicompanion.googleapis.com \
    aiplatform.googleapis.com

# 1.5. Bind License / IAM Roles (The Golden Key)
echo "🔑 Binding Ultra License for $MY_EMAIL..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$MY_EMAIL" \
    --role="roles/cloudaicompanion.user" \
    --condition=None > /dev/null

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$MY_EMAIL" \
    --role="roles/serviceusage.serviceUsageConsumer" \
    --condition=None > /dev/null

# 2. Create Artifact Registry (if not exists)
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION >/dev/null 2>&1; then
    echo "📦 Creating Artifact Registry: $REPO_NAME..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="ShadowTag Omega Serverless Repository"
else
    echo "✅ Artifact Registry exists."
fi

# 3. Build & Deploy: Judge 6 (Governance Engine)
echo "⚖️  Building Judge 6 (Omega Governance)..."
gcloud builds submit . \
    --config=cloudbuild.yaml \
    --substitutions=_SERVICE_NAME=judge-six-omega

echo "🚀 Deploying Judge 6 to Cloud Run..."
gcloud run deploy judge-six-omega \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/judge-six-omega:latest \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --set-env-vars=MODE=CLOUDRUN,PROJECT_ID=$PROJECT_ID

# 4. Build & Deploy: Jetski Sidecar (Browser Automation)
echo "🚤 Building Jetski Sidecar..."
# Requires custom build step as it's a different Dockerfile
gcloud builds submit . \
    --tag=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/jetski-sidecar:latest \
    --file=jetski.Dockerfile

echo "🚀 Deploying Jetski Sidecar to Cloud Run..."
gcloud run deploy jetski-sidecar \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/jetski-sidecar:latest \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --port=8081 \
    --memory=2Gi \
    --cpu=2

# 5. Build & Deploy: SeatJudge MCP (.NET Sidecar)
echo "💎 Building SeatJudge MCP (.NET)..."
gcloud builds submit . \
    --tag=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/seatjudge-mcp:latest \
    --file=Dockerfile.mcp

echo "🚀 Deploying SeatJudge MCP to Cloud Run..."
gcloud run deploy seatjudge-mcp \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/seatjudge-mcp:latest \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080

echo "✅ Uphill Snowball Protocol Complete."
echo "🌍 ShadowTag Omega is LIVE on Cloud Run."
echo "   - Judge: $(gcloud run services describe judge-six-omega --region=$REGION --format='value(status.url)')"
echo "   - Jetski: $(gcloud run services describe jetski-sidecar --region=$REGION --format='value(status.url)')"
echo "   - MCP: $(gcloud run services describe seatjudge-mcp --region=$REGION --format='value(status.url)')"
