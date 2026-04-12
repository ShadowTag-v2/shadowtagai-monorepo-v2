#!/bin/bash
# PNKLN Core Stack - Build and Deploy Script
# Builds Docker image and deploys to GKE

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
IMAGE_NAME="pnkln-ingestion"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')}"
REGISTRY="gcr.io"
FULL_IMAGE="${REGISTRY}/${PROJECT_ID}/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}PNKLN Ingestion Layer - Build & Deploy${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Image: ${FULL_IMAGE}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command_exists gcloud; then
    echo -e "${RED}Error: gcloud SDK is not installed${NC}"
    exit 1
fi

if ! command_exists kubectl; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}\n"

# Parse command-line arguments
BUILD_ONLY=false
DEPLOY_ONLY=false
DRY_RUN=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --build-only) BUILD_ONLY=true ;;
        --deploy-only) DEPLOY_ONLY=true ;;
        --dry-run) DRY_RUN=true ;;
        --tag) IMAGE_TAG="$2"; shift ;;
        --project) PROJECT_ID="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Build Docker image
if [ "$DEPLOY_ONLY" = false ]; then
    echo -e "${YELLOW}Building Docker image...${NC}"

    cd "$(dirname "$0")/.."

    docker build \
        -f infrastructure/docker/Dockerfile \
        -t "${IMAGE_NAME}:${IMAGE_TAG}" \
        -t "${IMAGE_NAME}:latest" \
        -t "${FULL_IMAGE}" \
        .

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Docker build successful${NC}\n"
    else
        echo -e "${RED}✗ Docker build failed${NC}"
        exit 1
    fi

    # Test image locally
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}Running dry-run test...${NC}"
        docker run --rm \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
            "${IMAGE_NAME}:${IMAGE_TAG}" \
            --dry-run

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Dry-run test passed${NC}\n"
        else
            echo -e "${RED}✗ Dry-run test failed${NC}"
            exit 1
        fi
    fi

    # Push to Google Container Registry
    echo -e "${YELLOW}Pushing image to GCR...${NC}"

    gcloud auth configure-docker --quiet

    docker push "${FULL_IMAGE}"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Image pushed to GCR${NC}\n"
    else
        echo -e "${RED}✗ Image push failed${NC}"
        exit 1
    fi
fi

# Deploy to GKE
if [ "$BUILD_ONLY" = false ]; then
    echo -e "${YELLOW}Deploying to GKE...${NC}"

    # Update kubeconfig
    gcloud container clusters get-credentials pnkln-cluster \
        --region="${REGION}" \
        --project="${PROJECT_ID}"

    # Create namespace if it doesn't exist
    kubectl create namespace pnkln-core --dry-run=client -o yaml | kubectl apply -f -

    # Update image tag in CronJob manifest
    cd "$(dirname "$0")"
    sed "s|gcr.io/PROJECT_ID/pnkln-ingestion:latest|${FULL_IMAGE}|g" \
        k8s/cronjob.yaml > /tmp/cronjob-deploy.yaml

    # Apply manifests
    kubectl apply -f /tmp/cronjob-deploy.yaml

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Deployment successful${NC}\n"
    else
        echo -e "${RED}✗ Deployment failed${NC}"
        exit 1
    fi

    # Verify deployment
    echo -e "${YELLOW}Verifying deployment...${NC}"
    kubectl get cronjob -n pnkln-core
    kubectl get configmap -n pnkln-core
    kubectl get serviceaccount -n pnkln-core

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Next CronJob run: $(kubectl get cronjob pnkln-ingestion -n pnkln-core -o jsonpath='{.status.lastScheduleTime}')"
    echo ""
    echo "To trigger a manual run:"
    echo "  kubectl create job --from=cronjob/pnkln-ingestion pnkln-ingestion-manual -n pnkln-core"
    echo ""
    echo "To view logs:"
    echo "  kubectl logs -l app=pnkln-ingestion -n pnkln-core --tail=100 -f"
fi

echo ""
echo -e "${GREEN}✓ Done!${NC}"
