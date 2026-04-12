#!/bin/bash
# Deployment script for Vertex AI / Cloud Run

set -e

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-gcp-project-id}"
REGION="${VERTEX_AI_LOCATION:-us-central1}"
SERVICE_NAME="ShadowTag-v2-agent-service"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================="
echo "AI You - Vertex AI Deployment Script"
echo "========================================="
echo ""
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Authenticate (if needed)
echo "Step 1: Authenticating with Google Cloud..."
gcloud auth application-default login

# Set project
echo "Step 2: Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Step 3: Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    aiplatform.googleapis.com \
    sqladmin.googleapis.com

# Build the container image
echo "Step 4: Building container image..."
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo "Step 5: Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "CLAUDE_CODE_USE_VERTEX=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},VERTEX_AI_LOCATION=${REGION}" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --min-instances 0

# Get the service URL
echo ""
echo "Step 6: Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Service URL: $SERVICE_URL"
echo "Health Check: ${SERVICE_URL}/health"
echo "API Docs: ${SERVICE_URL}/docs"
echo ""
echo "To test the deployment:"
echo "curl ${SERVICE_URL}/health"
echo ""
