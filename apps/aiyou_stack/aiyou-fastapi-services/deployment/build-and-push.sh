#!/bin/bash
# Build and push Docker image to GCR

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
IMAGE_NAME="cor17-api"
VERSION=${VERSION:-"latest"}
TAG="gcr.io/$PROJECT_ID/$IMAGE_NAME:$VERSION"

echo "🐳 Building Docker image for Cor.17 AI Architecture"

# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Build image
echo "🔨 Building image: $TAG"
docker build -t $TAG .

# Tag as latest
docker tag $TAG gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

# Push to GCR
echo "📤 Pushing image to Google Container Registry..."
docker push $TAG
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

echo "✅ Image pushed successfully!"
echo "   Image: $TAG"
echo ""
echo "To deploy:"
echo "  kubectl set image deployment/cor17-api api=$TAG -n cor17"
