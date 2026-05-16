#!/bin/bash
# YouAi Governance Service Deployment Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 YouAi Governance Service Deployment${NC}"
echo "========================================="

# Check deployment type
DEPLOY_TYPE=${1:-local}

case $DEPLOY_TYPE in
  local)
    echo -e "${YELLOW}📦 Deploying locally with Docker Compose...${NC}"

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
      echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
      exit 1
    fi

    # Copy env file if it doesn't exist
    if [ ! -f .env ]; then
      echo -e "${YELLOW}📝 Creating .env file from .env.example...${NC}"
      cp .env.example .env
    fi

    # Build and start services
    echo -e "${YELLOW}🔨 Building Docker images...${NC}"
    docker-compose build

    echo -e "${YELLOW}🚀 Starting services...${NC}"
    docker-compose up -d

    echo -e "${GREEN}✅ Services started!${NC}"
    echo ""
    echo "Service URLs:"
    echo "  - API Documentation: http://localhost:8000/docs"
    echo "  - Health Check: http://localhost:8000/health"
    echo "  - KPI Dashboard: http://localhost:8000/api/v1/kpi/dashboard"
    echo ""
    echo "View logs:"
    echo "  docker-compose logs -f youai-governance"
    ;;

  kubernetes|k8s)
    echo -e "${YELLOW}☸️  Deploying to Kubernetes...${NC}"

    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
      echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
      exit 1
    fi

    # Apply Kubernetes manifests
    echo -e "${YELLOW}📝 Applying Kubernetes manifests...${NC}"
    kubectl apply -f k8s/

    # Wait for deployment
    echo -e "${YELLOW}⏳ Waiting for deployment to be ready...${NC}"
    kubectl wait --for=condition=available --timeout=300s deployment/youai-governance-service

    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo "Get service status:"
    echo "  kubectl get pods -l app=youai-governance"
    echo "  kubectl get svc youai-governance-service"
    ;;

  cloud)
    echo -e "${YELLOW}☁️  Deploying to cloud (Docker image push)...${NC}"

    # Build image
    echo -e "${YELLOW}🔨 Building Docker image...${NC}"
    docker build -t youai-governance:latest .

    # Tag for registry
    REGISTRY=${DOCKER_REGISTRY:-registry.example.com}
    IMAGE_TAG=${IMAGE_TAG:-latest}

    echo -e "${YELLOW}🏷️  Tagging image...${NC}"
    docker tag youai-governance:latest ${REGISTRY}/youai-governance:${IMAGE_TAG}

    # Push to registry
    echo -e "${YELLOW}📤 Pushing to registry...${NC}"
    docker push ${REGISTRY}/youai-governance:${IMAGE_TAG}

    echo -e "${GREEN}✅ Image pushed to ${REGISTRY}/youai-governance:${IMAGE_TAG}${NC}"
    ;;

  *)
    echo -e "${RED}❌ Unknown deployment type: $DEPLOY_TYPE${NC}"
    echo ""
    echo "Usage: ./deploy.sh [local|kubernetes|cloud]"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh local       # Deploy locally with Docker Compose"
    echo "  ./deploy.sh kubernetes  # Deploy to Kubernetes cluster"
    echo "  ./deploy.sh cloud       # Build and push Docker image"
    exit 1
    ;;
esac

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo "========================================="
echo ""
echo "Persona IQ Override: 160"
echo "All governance engines running at maximum intelligence."
