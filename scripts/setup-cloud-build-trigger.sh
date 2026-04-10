#!/bin/bash
# Setup Cloud Build triggers for shadowtagai orchestrator

set -e

PROJECT_ID="${1:-your-project-id}"
REPO_NAME="ShadowTag-v2-fastapi-services"
REPO_OWNER="ehanc69"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setting up Cloud Build triggers for shadowtagai orchestrator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable \
  cloudbuild.googleapis.com \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  containerscanning.googleapis.com \
  --project="$PROJECT_ID"

# Create Artifact Registry repository
echo "🏗️  Creating Artifact Registry repository..."
gcloud artifacts repositories create shadowtagai \
  --repository-format=docker \
  --location=us-central1 \
  --description="shadowtagai orchestrator container images" \
  --project="$PROJECT_ID" || echo "Repository already exists"

# Grant Cloud Build permissions
echo "🔐 Granting Cloud Build permissions..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Create trigger for main branch (production deployments)
echo "🚀 Creating production trigger..."
gcloud builds triggers create github \
  --name="shadowtagai-production-deploy" \
  --repo-name="$REPO_NAME" \
  --repo-owner="$REPO_OWNER" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --description="Deploy to production on main branch" \
  --project="$PROJECT_ID" || echo "Trigger already exists"

# Create trigger for PRs (build and test only)
echo "🔬 Creating PR trigger..."
gcloud builds triggers create github \
  --name="shadowtagai-pr-validation" \
  --repo-name="$REPO_NAME" \
  --repo-owner="$REPO_OWNER" \
  --pull-request-pattern=".*" \
  --build-config="cloudbuild.pr.yaml" \
  --description="Validate PRs" \
  --project="$PROJECT_ID" || echo "Trigger already exists"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cloud Build triggers configured successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Connect your GitHub repository in Cloud Build console"
echo "2. Push to main branch to trigger production deployment"
echo "3. Monitor builds at: https://console.cloud.google.com/cloud-build/builds"
