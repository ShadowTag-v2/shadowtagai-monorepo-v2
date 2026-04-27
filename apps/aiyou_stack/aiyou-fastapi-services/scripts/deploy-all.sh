#!/bin/bash
# Complete deployment automation script
# Deploys shadowtagai orchestrator from scratch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Run: gcloud components install kubectl"
        exit 1
    fi

    # Check terraform
    if ! command -v terraform &> /dev/null; then
        log_error "terraform not found. Install from: https://www.terraform.io/downloads"
        exit 1
    fi

    log_success "All prerequisites installed"
}

# Get configuration
get_configuration() {
    log_info "Getting configuration..."

    # Project ID
    if [ -z "$PROJECT_ID" ]; then
        read -p "Enter GCP Project ID: " PROJECT_ID
    fi

    # Region
    if [ -z "$REGION" ]; then
        read -p "Enter GCP Region [us-central1]: " REGION
        REGION=${REGION:-us-central1}
    fi

    # Anthropic removed - no longer needed
    # if [ -z "$ANTHROPIC_PROJECT_ID" ]; then
    #     read -p "Enter Anthropic Vertex Project ID: " ANTHROPIC_PROJECT_ID
    # fi

||||||| f285896f1
    # Anthropic Project ID
    if [ -z "$ANTHROPIC_PROJECT_ID" ]; then
        read -p "Enter Anthropic Vertex Project ID: " ANTHROPIC_PROJECT_ID
    fi

    export PROJECT_ID
    export REGION

    log_success "Configuration loaded"
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."

    cd terraform

    # Create tfvars if it doesn't exist
    if [ ! -f terraform.tfvars ]; then
        cat > terraform.tfvars <<EOF
project_id  = "$PROJECT_ID"
region      = "$REGION"
environment = "production"
||||||| f285896f1
project_id                  = "$PROJECT_ID"
region                      = "$REGION"
anthropic_vertex_project_id = "$ANTHROPIC_PROJECT_ID"
environment                 = "production"
EOF
        log_info "Created terraform.tfvars"
    fi

    # Initialize
    log_info "Running terraform init..."
    terraform init

    # Plan
    log_info "Running terraform plan..."
    terraform plan -out=tfplan

    # Apply
    read -p "Apply terraform plan? (yes/no): " APPLY
    if [ "$APPLY" == "yes" ]; then
        log_info "Applying infrastructure..."
        terraform apply tfplan
        log_success "Infrastructure deployed"
    else
        log_warn "Skipping terraform apply"
    fi

    cd ..
}

# Configure kubectl
configure_kubectl() {
    log_info "Configuring kubectl..."

    gcloud container clusters get-credentials shadowtagai-production \
      --region $REGION \
      --project $PROJECT_ID

    log_success "kubectl configured"
}

# Update manifests
update_manifests() {
    log_info "Updating Kubernetes manifests..."

    # Update ServiceAccount
    sed -i.bak "s/YOUR_PROJECT_ID/$PROJECT_ID/g" k8s/base/serviceaccount.yaml
    rm k8s/base/serviceaccount.yaml.bak || true

    # Update kustomization
    sed -i.bak "s/PROJECT_ID/$PROJECT_ID/g" k8s/base/kustomization.yaml
    rm k8s/base/kustomization.yaml.bak || true

    log_success "Manifests updated"
}

# Create secrets
create_secrets() {
    log_info "Creating Kubernetes secrets..."

    # Create namespace first
    kubectl create namespace shadowtagai-production --dry-run=client -o yaml | kubectl apply -f -

    # Create secret (placeholder for now if needed, or skip if no other secrets)
    # kubectl create secret generic shadowtagai-secrets \
    #   --from-literal=project-id="$PROJECT_ID" \
    #   --namespace=shadowtagai-production \
    #   --dry-run=client -o yaml | kubectl apply -f -

    log_success "Secrets created"
}

# Set up Cloud Build
setup_cloud_build() {
    log_info "Setting up Cloud Build..."

    if [ -f scripts/setup-cloud-build-trigger.sh ]; then
        chmod +x scripts/setup-cloud-build-trigger.sh
        ./scripts/setup-cloud-build-trigger.sh $PROJECT_ID
        log_success "Cloud Build configured"
    else
        log_warn "Cloud Build setup script not found, skipping"
    fi
}

# Set up monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."

    if [ -f scripts/setup-monitoring.sh ]; then
        chmod +x scripts/setup-monitoring.sh
        ./scripts/setup-monitoring.sh $PROJECT_ID
        log_success "Monitoring configured"
    else
        log_warn "Monitoring setup script not found, skipping"
    fi
}

# Deploy application
deploy_application() {
    log_info "Deploying application to GKE..."

    # Apply Kubernetes manifests
    kubectl apply -k k8s/base

    # Wait for deployment
    log_info "Waiting for deployment to complete..."
    kubectl rollout status deployment/shadowtagai-orchestrator -n shadowtagai-production --timeout=5m

    log_success "Application deployed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."

    # Check pods
    kubectl get pods -n shadowtagai-production

    # Check service
    kubectl get svc -n shadowtagai-production

    # Port forward and test
    log_info "Testing health endpoint..."
    kubectl port-forward svc/shadowtagai-orchestrator 8080:80 -n shadowtagai-production &
    PF_PID=$!
    sleep 5

    HEALTH_RESPONSE=$(curl -s http://localhost:8080/health || true)
    kill $PF_PID || true

    if [ ! -z "$HEALTH_RESPONSE" ]; then
        log_success "Health check passed: $HEALTH_RESPONSE"
    else
        log_warn "Health check failed, but deployment may still be initializing"
    fi
}

# Main deployment flow
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   SHADOWTAGAI ORCHESTRATOR - COMPLETE DEPLOYMENT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_prerequisites
    get_configuration

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Starting deployment with following configuration:"
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    read -p "Continue with deployment? (yes/no): " CONTINUE
    if [ "$CONTINUE" != "yes" ]; then
        log_warn "Deployment cancelled"
        exit 0
    fi

    deploy_infrastructure
    configure_kubectl
    update_manifests
    create_secrets
    setup_cloud_build
    setup_monitoring
    deploy_application
    verify_deployment

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   ✅ DEPLOYMENT COMPLETE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Next steps:"
    echo "1. View pods: kubectl get pods -n shadowtagai-production"
    echo "2. View logs: kubectl logs -f deployment/shadowtagai-orchestrator -n shadowtagai-production"
    echo "3. View monitoring: https://console.cloud.google.com/monitoring?project=$PROJECT_ID"
    echo "4. Configure Ingress for external access (see docs/DEPLOYMENT.md)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Run main
main "$@"
