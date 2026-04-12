#!/bin/bash
# Production Deployment Script for Consensus Orchestrator on GKE

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-pnkln-production}"
REGION="${REGION:-us-central1}"
CLUSTER_NAME="${CLUSTER_NAME:-consensus-cluster}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "================================"
echo "CONSENSUS ORCHESTRATOR DEPLOYMENT"
echo "================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Cluster: $CLUSTER_NAME"
echo "Image Tag: $IMAGE_TAG"
echo ""

# Function to print colored output
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is configured
print_step "Checking gcloud configuration..."
if ! gcloud config get-value project &> /dev/null; then
    print_error "gcloud not configured. Run: gcloud auth login"
    exit 1
fi

# Set project
print_step "Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

# Build Docker image
print_step "Building Docker image..."
cd "$(dirname "$0")"
docker build -t "gcr.io/$PROJECT_ID/consensus-orchestrator:$IMAGE_TAG" .

# Push to GCR
print_step "Pushing image to GCR..."
docker push "gcr.io/$PROJECT_ID/consensus-orchestrator:$IMAGE_TAG"

# Get GKE credentials
print_step "Getting GKE credentials..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"

# Update manifests with project ID
print_step "Updating Kubernetes manifests with project ID..."
sed -i.bak "s/PROJECT_ID/$PROJECT_ID/g" k8s/*.yaml
rm -f k8s/*.yaml.bak

# Create namespace
print_step "Creating namespace..."
kubectl apply -f k8s/01-namespace.yaml

# Check if secrets exist
if ! kubectl get secret api-keys -n consensus &> /dev/null; then
    print_warning "Secrets not found. You need to create them manually:"
    echo ""
    echo "kubectl create secret generic api-keys \\"
    echo "  --from-literal=google-api-key=\$GOOGLE_API_KEY \\"
    echo "  --from-literal=anthropic-api-key=\$ANTHROPIC_API_KEY \\"
    echo "  --from-literal=openai-api-key=\$OPENAI_API_KEY \\"
    echo "  --from-literal=xai-api-key=\$XAI_API_KEY \\"
    echo "  --from-literal=perplexity-api-key=\$PERPLEXITY_API_KEY \\"
    echo "  --from-literal=api-keys=\$API_KEYS \\"
    echo "  --namespace=consensus"
    echo ""
    read -p "Press Enter to continue after creating secrets..."
fi

# Apply manifests
print_step "Applying Kubernetes manifests..."
kubectl apply -f k8s/02-serviceaccount.yaml
kubectl apply -f k8s/03-pvc.yaml
kubectl apply -f k8s/04-configmap.yaml
kubectl apply -f k8s/06-deployment.yaml
kubectl apply -f k8s/07-service.yaml
kubectl apply -f k8s/08-hpa.yaml

# Wait for deployment
print_step "Waiting for deployment to be ready..."
kubectl rollout status deployment/consensus-orchestrator -n consensus --timeout=5m

# Get service details
print_step "Getting service details..."
EXTERNAL_IP=$(kubectl get service consensus-orchestrator -n consensus -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo ""
echo "================================"
echo "DEPLOYMENT COMPLETE"
echo "================================"
echo ""
echo "External IP: $EXTERNAL_IP"
echo "API Endpoint: http://$EXTERNAL_IP/docs"
echo ""
echo "Test with:"
echo "  curl -X POST http://$EXTERNAL_IP/query \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -H 'X-API-Key: YOUR_API_KEY' \\"
echo "    -d '{\"message\": \"Test query\"}'"
echo ""
echo "Monitor pods:"
echo "  kubectl get pods -n consensus -w"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/consensus-orchestrator -n consensus"
echo ""
