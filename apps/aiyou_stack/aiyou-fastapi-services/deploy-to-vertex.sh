#!/bin/bash

# Deployment script for Vertex AI Workbench
# This script builds and deploys the Code Refactorer service to Google Cloud Vertex AI

set -e

# Configuration
PROJECT_ID="${VERTEX_PROJECT_ID:-your-gcp-project-id}"
REGION="${VERTEX_LOCATION:-us-central1}"
SERVICE_NAME="code-refactorer-service"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "======================================"
echo "Deploying Code Refactorer to Vertex AI"
echo "======================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Image: ${IMAGE_NAME}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
echo "[1/6] Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "[2/6] Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    aiplatform.googleapis.com \
    containerregistry.googleapis.com

# Build the container image
echo "[3/6] Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Create a service account if it doesn't exist
echo "[4/6] Setting up service account..."
SERVICE_ACCOUNT="${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT} &> /dev/null; then
    gcloud iam service-accounts create ${SERVICE_NAME} \
        --display-name="Code Refactorer Service Account"
fi

# Grant necessary permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user"

# Deploy to Cloud Run (alternative to Vertex AI Workbench for API serving)
echo "[5/6] Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --service-account ${SERVICE_ACCOUNT} \
    --memory 4Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "APP_NAME=AI Code Refactorer Service,DEBUG=false,MODEL=claude-sonnet-4-5-20250929" \
    --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest"

# Get the service URL
echo "[6/6] Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo "Service URL: ${SERVICE_URL}"
echo "API Docs: ${SERVICE_URL}/docs"
echo "Health Check: ${SERVICE_URL}/health"
echo ""
echo "Example usage:"
echo "curl -X POST \"${SERVICE_URL}/api/v1/refactor/\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"code\": \"def foo():\\n    x=1\\n    return x\", \"language\": \"python\", \"refactor_type\": \"full\"}'"
echo ""
