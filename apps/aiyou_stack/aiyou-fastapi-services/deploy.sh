#!/bin/bash
################################################################################
# PNKLN GKE Inference Deployment - Master Orchestrator
# With JR (Joe Rogan) Validation Gates
#
# Purpose: Deploy production-grade LLM inference infrastructure on GKE
# Bootstrap discipline: ROI ≥3×, Cost ≤$65K/mo, LTV:CAC ≥4:1
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PROJECT_ID:-}"
REGION="${REGION:-us-central1}"
CLUSTER_NAME="${CLUSTER_NAME:-pnkln-inference-prod}"
MONTHLY_BUDGET_USD=65000

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi

    # Check terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform not found. Install: https://www.terraform.io/downloads"
        exit 1
    fi

    # Check PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        log_error "PROJECT_ID not set. Usage: PROJECT_ID=your-project-id ./deploy.sh"
        exit 1
    fi

    log_info "Prerequisites check passed ✓"
}

jr_validation_gate_1_purpose() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "JR VALIDATION GATE #1: PURPOSE"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo ""
    echo "Question: Does this deployment advance Pnkln revenue + defensible moat?"
    echo ""
    echo "Expected impact:"
    echo "  • Revenue: \$9.6M ARR in 18 months (Sales, Call Intel, Deal Intel, Negotiation)"
    echo "  • Moat: Google Hypercomputer lock-in (18-month lead time for competitors)"
    echo "  • Regulatory: EU AI Act compliance (Judge #6 ATP 5-19)"
    echo "  • Vendor independence: Multi-LLM strategy (40/35/15/5/5)"
    echo ""
    read -p "Proceed with deployment? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Deployment cancelled by user (JR Gate #1: PURPOSE)"
        exit 1
    fi

    log_info "JR Gate #1: PURPOSE - PASSED ✓"
}

jr_validation_gate_2_reasons() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "JR VALIDATION GATE #2: REASONS"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo ""
    echo "Bootstrap discipline check:"
    echo "  ✓ Vendor independence (avoid OpenAI/Anthropic lock-in)"
    echo "  ✓ EU AI Act timing (compliance deadline Dec 2025)"
    echo "  ✓ Google Hypercomputer access (competitive advantage)"
    echo "  ✓ Cost control: \$65K/mo ceiling with autoscaling"
    echo ""
    echo "Risk assessment: RA-2 (MEDIUM)"
    echo "  • Known: GKE reliability (99.95% SLA)"
    echo "  • Unknown: Judge #6 latency under production load"
    echo "  • Mitigation: Parallel validation + Layer 1 fast path"
    echo ""
    read -p "Accept risk level? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Deployment cancelled by user (JR Gate #2: REASONS)"
        exit 1
    fi

    log_info "JR Gate #2: REASONS - PASSED ✓"
}

jr_validation_gate_3_brakes() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "JR VALIDATION GATE #3: BRAKES"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo ""
    echo "ROI gates enforced:"
    echo "  • Month 3:  ARR ≥\$1M, LTV:CAC ≥2:1"
    echo "  • Month 6:  ARR ≥\$3M, LTV:CAC ≥4:1"
    echo "  • Month 12: ARR ≥\$6M, LTV:CAC ≥4:1, Churn <10%"
    echo "  • Month 18: ARR ≥\$9.6M, ROI ≥3×"
    echo ""
    echo "Kill-switch conditions:"
    echo "  1. LTV:CAC <4:1 after 12 months → Immediate shutdown"
    echo "  2. Monthly cost >\$65K for 2 consecutive months → Review"
    echo "  3. p99 latency >90ms for 7 days → Rollback"
    echo "  4. Judge #6 coverage <98% for 3 days → Audit"
    echo ""
    echo "Budget alerts configured at: 50%, 75%, 90%, 100%"
    echo ""
    read -p "Confirm ROI gates and kill-switch? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Deployment cancelled by user (JR Gate #3: BRAKES)"
        exit 1
    fi

    log_info "JR Gate #3: BRAKES - PASSED ✓"
}

check_gpu_quota() {
    log_info "Checking GPU quota (NVIDIA L4)..."

    # Check if quota is sufficient (need 20 L4 GPUs minimum)
    QUOTA_CHECK=$(gcloud compute project-info describe \
        --project="$PROJECT_ID" \
        --format="value(quotas.filter(metric=NVIDIA_L4_GPUS).limit)" \
        2>/dev/null || echo "0")

    if [ "$QUOTA_CHECK" -lt 20 ]; then
        log_warn "GPU quota insufficient: Current=$QUOTA_CHECK, Required=20"
        log_warn "Request quota increase:"
        log_warn "  gcloud compute project-info describe --project=$PROJECT_ID"
        log_warn "  https://console.cloud.google.com/iam-admin/quotas?project=$PROJECT_ID"
        echo ""
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_info "GPU quota check passed: $QUOTA_CHECK L4 GPUs available ✓"
    fi
}

deploy_terraform() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "DEPLOYING TERRAFORM INFRASTRUCTURE"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    cd terraform

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init

    # Plan
    log_info "Planning infrastructure..."
    terraform plan \
        -var="project_id=$PROJECT_ID" \
        -var="region=$REGION" \
        -var="cluster_name=$CLUSTER_NAME" \
        -out=tfplan

    # Apply
    log_info "Applying infrastructure..."
    terraform apply tfplan

    cd ..
    log_info "Terraform deployment complete ✓"
}

configure_kubectl() {
    log_info "Configuring kubectl..."

    gcloud container clusters get-credentials "$CLUSTER_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID"

    log_info "kubectl configured ✓"
}

deploy_kubernetes() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "DEPLOYING KUBERNETES MANIFESTS"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Replace PROJECT_ID placeholders
    log_info "Replacing PROJECT_ID placeholders..."
    find k8s -type f -name "*.yaml" -exec sed -i "s/\${PROJECT_ID}/$PROJECT_ID/g" {} +

    # Deploy namespaces and base resources
    log_info "Deploying namespaces..."
    kubectl apply -f k8s/base/

    # Deploy Judge #6
    log_info "Deploying Judge #6 (3 layers + webhook)..."
    kubectl apply -f k8s/judge-6/

    # Deploy LLM Router
    log_info "Deploying LLM Router..."
    kubectl apply -f k8s/llm-router/

    # Deploy Inference Gateway + vLLM
    log_info "Deploying Inference Gateway + vLLM..."
    kubectl apply -f k8s/inference-gateway/

    # Deploy Monitoring
    log_info "Deploying monitoring stack..."
    kubectl apply -f k8s/monitoring/

    log_info "Kubernetes deployment complete ✓"
}

verify_deployment() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "VERIFYING DEPLOYMENT"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check nodes
    log_info "Checking nodes..."
    kubectl get nodes

    # Check pods in governance namespace
    log_info "Checking Judge #6 pods..."
    kubectl get pods -n ShadowTag-v2jr-governance

    # Check pods in inference namespace
    log_info "Checking LLM Router pods..."
    kubectl get pods -n llm-inference

    # Check monitoring
    log_info "Checking monitoring pods..."
    kubectl get pods -n monitoring

    log_info "Verification complete ✓"
}

print_next_steps() {
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "DEPLOYMENT SUCCESSFUL!"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Access Grafana dashboards:"
    echo "   kubectl port-forward -n monitoring svc/grafana 3000:80"
    echo "   http://localhost:3000 (admin/changeme-in-production)"
    echo ""
    echo "2. Configure API keys in Secret Manager:"
    echo "   - Anthropic API key"
    echo "   - OpenAI API key"
    echo "   - xAI API key"
    echo ""
    echo "3. Fine-tune Gemini on PRB corpus (Vertex AI)"
    echo ""
    echo "4. Build and push container images:"
    echo "   - gcr.io/$PROJECT_ID/judge-gemini:latest"
    echo "   - gcr.io/$PROJECT_ID/judge-pytorch:latest"
    echo "   - gcr.io/$PROJECT_ID/judge-rules-adapter:latest"
    echo "   - gcr.io/$PROJECT_ID/judge-webhook:latest"
    echo "   - gcr.io/$PROJECT_ID/llm-router:latest"
    echo ""
    echo "5. Load test Judge #6 (validate p99 <90ms):"
    echo "   kubectl run -it --rm load-test --image=williamyeh/wrk --restart=Never -- ..."
    echo ""
    echo "6. Monitor ROI gates (Month 3/6/12):"
    echo "   See docs/EXECUTIVE_SUMMARY.md for details"
    echo ""
    echo "Monthly cost target: \$${MONTHLY_BUDGET_USD}"
    echo "ROI target: ≥3× in 18 months"
    echo "SLA targets: p99 ≤90ms, 99.95% availability, 98% Judge #6 coverage"
    echo ""
}

# Main execution
main() {
    log_info "Starting PNKLN GKE Inference Deployment"
    echo ""

    check_prerequisites
    jr_validation_gate_1_purpose
    jr_validation_gate_2_reasons
    jr_validation_gate_3_brakes
    check_gpu_quota

    deploy_terraform
    configure_kubectl
    deploy_kubernetes
    verify_deployment

    print_next_steps
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-id=*)
            PROJECT_ID="${1#*=}"
            shift
            ;;
        --region=*)
            REGION="${1#*=}"
            shift
            ;;
        --cluster-name=*)
            CLUSTER_NAME="${1#*=}"
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Usage: $0 --project-id=PROJECT_ID [--region=REGION] [--cluster-name=NAME]"
            exit 1
            ;;
    esac
done

main
