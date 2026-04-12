#!/bin/bash
# PNKLN Core Stack™ - Infrastructure Deployment Script
# AI Operating Posture Framework Implementation
# Version: 1.0

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-pnkln-core-stack}"
REGION="${REGION:-us-central1}"
CLUSTER_NAME="${CLUSTER_NAME:-pnkln-inference-prod}"
TERRAFORM_DIR="$(pwd)/infrastructure/terraform"
K8S_DIR="$(pwd)/kubernetes"

# Functions
log_info() {
    echo -e "${BLUE}▶${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Please install Google Cloud SDK."
        exit 1
    fi
    log_success "gcloud CLI found"

    # Check terraform
    if ! command -v terraform &> /dev/null; then
        log_error "terraform not found. Please install Terraform >= 1.8.0"
        exit 1
    fi

    TERRAFORM_VERSION=$(terraform version -json 2>/dev/null | jq -r '.terraform_version' || echo "0.0.0")
    log_success "Terraform v${TERRAFORM_VERSION} found"

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_warning "kubectl not found. Installing..."
        gcloud components install kubectl gke-gcloud-auth-plugin
    fi
    log_success "kubectl found"

    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
        log_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi
    log_success "Authenticated with gcloud"
}

enable_apis() {
    log_info "Enabling required GCP APIs..."

    gcloud services enable \
        container.googleapis.com \
        compute.googleapis.com \
        aiplatform.googleapis.com \
        artifactregistry.googleapis.com \
        monitoring.googleapis.com \
        logging.googleapis.com \
        storage.googleapis.com \
        networkservices.googleapis.com \
        certificatemanager.googleapis.com \
        --project="${PROJECT_ID}" \
        2>/dev/null || log_warning "Some APIs may already be enabled"

    log_success "APIs enabled"
}

create_tfstate_bucket() {
    log_info "Checking Terraform state bucket..."

    BUCKET_NAME="${PROJECT_ID}-tfstate"

    if gsutil ls "gs://${BUCKET_NAME}" &>/dev/null; then
        log_success "Terraform state bucket already exists"
    else
        log_info "Creating Terraform state bucket..."
        gsutil mb -l "${REGION}" "gs://${BUCKET_NAME}"
        gsutil versioning set on "gs://${BUCKET_NAME}"
        log_success "Terraform state bucket created"
    fi
}

deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."

    cd "${TERRAFORM_DIR}"

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init

    # Validate configuration
    log_info "Validating Terraform configuration..."
    terraform validate

    # Plan deployment
    log_info "Creating Terraform plan..."
    terraform plan -out=tfplan

    # Show plan summary
    echo ""
    log_warning "═══════════════════════════════════════════════"
    log_warning "  TERRAFORM PLAN READY"
    log_warning "  Estimated monthly cost: \$60-65K"
    log_warning "  Review the plan above carefully."
    log_warning "═══════════════════════════════════════════════"
    echo ""

    # Confirm deployment
    read -p "$(echo -e ${YELLOW}❓${NC} Deploy infrastructure? [yes/no]: )" CONFIRM

    if [[ "$CONFIRM" != "yes" ]]; then
        log_warning "Deployment cancelled by user"
        exit 0
    fi

    # Apply Terraform
    log_info "Applying Terraform configuration..."
    terraform apply tfplan

    log_success "Infrastructure deployed successfully"

    cd - > /dev/null
}

configure_kubectl() {
    log_info "Configuring kubectl access..."

    gcloud container clusters get-credentials "${CLUSTER_NAME}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}"

    log_success "kubectl configured"

    # Verify cluster access
    log_info "Verifying cluster access..."
    if kubectl cluster-info &>/dev/null; then
        log_success "Cluster accessible"
        kubectl get nodes
    else
        log_error "Cannot access cluster"
        exit 1
    fi
}

deploy_kubernetes_manifests() {
    log_info "Deploying Kubernetes manifests..."

    # Deploy namespaces
    log_info "Creating namespaces..."
    kubectl apply -f "${K8S_DIR}/base/namespaces.yaml"
    log_success "Namespaces created"

    # Deploy Judge #6
    log_info "Deploying Judge #6 enforcement system..."
    kubectl apply -f "${K8S_DIR}/base/judge6-deployment.yaml"
    log_success "Judge #6 deployment created"

    # Wait for deployments
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=600s \
        deployment/judge6-hybrid -n ShadowTag-v2jr-governance || log_warning "Judge #6 deployment may need more time"

    log_success "Kubernetes manifests deployed"
}

validate_deployment() {
    log_info "Validating deployment..."

    # Check node pools
    log_info "Verifying node pools..."
    EXPECTED_POOLS=("system-pool" "judge-l4-pool" "llm-routing-pool")
    for pool in "${EXPECTED_POOLS[@]}"; do
        if kubectl get nodes -l "cloud.google.com/gke-nodepool=$pool" &>/dev/null; then
            log_success "Node pool: $pool"
        else
            log_warning "Node pool not found: $pool (may be scaled to zero)"
        fi
    done

    # Check namespaces
    log_info "Verifying namespaces..."
    EXPECTED_NS=("ShadowTag-v2jr-governance" "autogen-orchestration" "cognitive-stack-v5" "shadowtag-v2" "monitoring")
    for ns in "${EXPECTED_NS[@]}"; do
        if kubectl get namespace "$ns" &>/dev/null; then
            log_success "Namespace: $ns"
        else
            log_warning "Namespace not found: $ns"
        fi
    done

    # Check storage
    log_info "Verifying storage..."
    if gsutil ls "gs://${PROJECT_ID}-model-weights" &>/dev/null; then
        log_success "Model weights bucket exists"
    fi

    if gcloud artifacts repositories describe pnkln-inference --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
        log_success "Artifact Registry exists"
    fi

    log_success "Validation complete"
}

print_summary() {
    echo ""
    log_success "════════════════════════════════════════════════════════"
    log_success "  DEPLOYMENT COMPLETE"
    log_success "════════════════════════════════════════════════════════"
    echo ""
    echo "  Project:      ${PROJECT_ID}"
    echo "  Region:       ${REGION}"
    echo "  Cluster:      ${CLUSTER_NAME}"
    echo ""
    echo "  Next steps:"
    echo "  1. Review deployed resources in GCP Console"
    echo "  2. Deploy application workloads to namespaces"
    echo "  3. Configure monitoring dashboards"
    echo "  4. Set up CI/CD pipelines"
    echo ""
    echo "  Useful commands:"
    echo "    kubectl get nodes"
    echo "    kubectl get pods --all-namespaces"
    echo "    kubectl get svc --all-namespaces"
    echo ""
    log_success "════════════════════════════════════════════════════════"
}

# Main execution
main() {
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "  PNKLN CORE STACK™ - DEPLOYMENT SCRIPT"
    echo "  AI Operating Posture Framework Implementation"
    echo "════════════════════════════════════════════════════════"
    echo ""

    check_prerequisites
    enable_apis
    create_tfstate_bucket
    deploy_infrastructure
    configure_kubectl
    deploy_kubernetes_manifests
    validate_deployment
    print_summary
}

# Run main function
main "$@"
