#!/bin/bash
set -euo pipefail

################################################################################
# Pnkln GKE Deployment - Master Orchestration Script
################################################################################
# Purpose: Deploy production-ready inference platform on GKE with GPU/TPU
# SLA Target: p99 ≤90ms, p95 ≤50ms, p50 ≤20ms
# Bootstrap: $0K capital, ROI ≥3× (18mo), LTV:CAC ≥4:1 (12mo)
################################################################################

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${PNKLN_PROJECT_ID:-}"
REGION="${PNKLN_REGION:-us-central1}"
ZONE="${PNKLN_ZONE:-us-central1-a}"
CLUSTER_NAME="${PNKLN_CLUSTER:-pnkln-inference}"
WORKBENCH_NAME="${PNKLN_WORKBENCH:-pnkln-dev-workbench}"

# Cost gates
DAILY_DEV_LIMIT=50
DAILY_PROD_LIMIT=500

# GPU configuration
GPU_TYPE="nvidia-l4"
GPU_COUNT_MIN=0
GPU_COUNT_MAX=20

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    command -v gcloud >/dev/null 2>&1 || missing_tools+=("gcloud")
    command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
    command -v terraform >/dev/null 2>&1 || log_warning "terraform not found (optional for IaC deployment)"

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    # Check gcloud authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
        log_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

validate_project() {
    if [ -z "$PROJECT_ID" ]; then
        log_error "PNKLN_PROJECT_ID environment variable not set"
        echo ""
        echo "Set it with: export PNKLN_PROJECT_ID=\"your-project-id\""
        exit 1
    fi

    log_info "Validating GCP project: $PROJECT_ID"

    if ! gcloud projects describe "$PROJECT_ID" &>/dev/null; then
        log_error "Project $PROJECT_ID not found or not accessible"
        exit 1
    fi

    # Set active project
    gcloud config set project "$PROJECT_ID"

    log_success "Project validated: $PROJECT_ID"
}

enable_apis() {
    log_info "Enabling required GCP APIs..."

    local apis=(
        "container.googleapis.com"
        "compute.googleapis.com"
        "aiplatform.googleapis.com"
        "secretmanager.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "notebooks.googleapis.com"
    )

    for api in "${apis[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" || {
            log_error "Failed to enable $api"
            exit 1
        }
    done

    log_success "All required APIs enabled"

    # Wait for API propagation
    log_info "Waiting for API propagation (30s)..."
    sleep 30
}

check_quotas() {
    log_info "Checking GPU quotas..."

    local gpu_quota
    gpu_quota=$(gcloud compute project-info describe --project="$PROJECT_ID" \
        --format="value(quotas.filter(metric:nvidia_l4_gpus).limit)" 2>/dev/null || echo "0")

    if [ "$gpu_quota" -lt "$GPU_COUNT_MAX" ]; then
        log_warning "GPU quota ($gpu_quota) is less than requested max ($GPU_COUNT_MAX)"
        log_warning "Request increase: https://console.cloud.google.com/iam-admin/quotas"
        log_warning "Continuing with available quota..."
    else
        log_success "GPU quota sufficient: $gpu_quota GPUs available"
    fi
}

create_gke_cluster() {
    log_info "Creating GKE Hypercomputer cluster: $CLUSTER_NAME"

    if gcloud container clusters describe "$CLUSTER_NAME" --region="$REGION" &>/dev/null; then
        log_warning "Cluster $CLUSTER_NAME already exists"
        read -p "Delete and recreate? (yes/no): " -r
        if [[ $REPLY =~ ^[Yy]es$ ]]; then
            log_info "Deleting existing cluster..."
            gcloud container clusters delete "$CLUSTER_NAME" --region="$REGION" --quiet
        else
            log_info "Using existing cluster"
            return 0
        fi
    fi

    log_info "Creating cluster (this may take 10-15 minutes)..."

    gcloud container clusters create "$CLUSTER_NAME" \
        --region="$REGION" \
        --release-channel="rapid" \
        --enable-autoscaling \
        --min-nodes=1 \
        --max-nodes=10 \
        --machine-type="n2-standard-16" \
        --num-nodes=1 \
        --disk-type="pd-ssd" \
        --disk-size=100 \
        --enable-autorepair \
        --enable-autoupgrade \
        --enable-ip-alias \
        --enable-stackdriver-kubernetes \
        --enable-managed-prometheus \
        --workload-pool="${PROJECT_ID}.svc.id.goog" \
        --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
        --no-enable-basic-auth \
        --no-issue-client-certificate \
        --metadata=disable-legacy-endpoints=true \
        --enable-shielded-nodes \
        --shielded-secure-boot \
        --shielded-integrity-monitoring \
        --labels="env=production,app=pnkln-inference" || {
        log_error "Failed to create GKE cluster"
        exit 1
    }

    log_success "GKE cluster created successfully"
}

create_gpu_node_pool() {
    log_info "Creating GPU node pool..."

    if gcloud container node-pools describe "gpu-pool" --cluster="$CLUSTER_NAME" --region="$REGION" &>/dev/null; then
        log_warning "GPU node pool already exists"
        return 0
    fi

    gcloud container node-pools create "gpu-pool" \
        --cluster="$CLUSTER_NAME" \
        --region="$REGION" \
        --machine-type="n1-standard-16" \
        --accelerator="type=${GPU_TYPE},count=1" \
        --enable-autoscaling \
        --min-nodes="$GPU_COUNT_MIN" \
        --max-nodes="$GPU_COUNT_MAX" \
        --disk-type="pd-ssd" \
        --disk-size=200 \
        --enable-autorepair \
        --enable-autoupgrade \
        --node-labels="workload=inference,gpu=true" \
        --node-taints="nvidia.com/gpu=present:NoSchedule" \
        --metadata=disable-legacy-endpoints=true \
        --scopes="gke-default,https://www.googleapis.com/auth/cloud-platform" || {
        log_error "Failed to create GPU node pool"
        exit 1
    }

    log_success "GPU node pool created"
}

install_gpu_drivers() {
    log_info "Installing NVIDIA GPU drivers..."

    kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded-latest.yaml || {
        log_error "Failed to install GPU drivers"
        exit 1
    }

    log_success "GPU drivers installed"
}

setup_workload_identity() {
    log_info "Setting up Workload Identity..."

    local ksa="pnkln-inference-sa"
    local gsa="pnkln-inference@${PROJECT_ID}.iam.gserviceaccount.com"

    # Create Google Service Account
    if ! gcloud iam service-accounts describe "$gsa" &>/dev/null; then
        gcloud iam service-accounts create "pnkln-inference" \
            --display-name="Pnkln Inference Service Account" \
            --project="$PROJECT_ID"
    fi

    # Grant permissions
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${gsa}" \
        --role="roles/secretmanager.secretAccessor"

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${gsa}" \
        --role="roles/monitoring.metricWriter"

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${gsa}" \
        --role="roles/logging.logWriter"

    # Create Kubernetes Service Account
    kubectl create namespace pnkln-inference --dry-run=client -o yaml | kubectl apply -f -
    kubectl create serviceaccount "$ksa" -n pnkln-inference --dry-run=client -o yaml | kubectl apply -f -

    # Bind KSA to GSA
    gcloud iam service-accounts add-iam-policy-binding "$gsa" \
        --role="roles/iam.workloadIdentityUser" \
        --member="serviceAccount:${PROJECT_ID}.svc.id.goog[pnkln-inference/${ksa}]"

    kubectl annotate serviceaccount "$ksa" -n pnkln-inference \
        iam.gke.io/gcp-service-account="$gsa" --overwrite

    log_success "Workload Identity configured"
}

create_secrets() {
    log_info "Creating Secret Manager secrets..."

    local secrets=(
        "anthropic-api-key"
        "openai-api-key"
        "xai-api-key"
        "mistral-api-key"
        "google-ai-api-key"
    )

    for secret in "${secrets[@]}"; do
        if ! gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
            echo -n "PLACEHOLDER_${secret^^}_CHANGE_ME" | \
                gcloud secrets create "$secret" \
                    --data-file=- \
                    --replication-policy="automatic" \
                    --project="$PROJECT_ID" || {
                log_warning "Failed to create secret: $secret"
            }
            log_warning "Secret $secret created with PLACEHOLDER - UPDATE IMMEDIATELY"
        else
            log_info "Secret $secret already exists"
        fi
    done

    log_success "Secrets created (remember to update placeholders!)"
}

create_vertex_workbench() {
    log_info "Creating Vertex AI Workbench instance..."

    if gcloud notebooks instances describe "$WORKBENCH_NAME" --location="$ZONE" &>/dev/null; then
        log_warning "Workbench instance $WORKBENCH_NAME already exists"
        return 0
    fi

    gcloud notebooks instances create "$WORKBENCH_NAME" \
        --location="$ZONE" \
        --machine-type="n1-standard-8" \
        --accelerator-type="NVIDIA_TESLA_T4" \
        --accelerator-core-count=1 \
        --install-gpu-driver \
        --disk-size=200 \
        --disk-type=PD_SSD \
        --metadata="proxy-mode=service_account,install-nvidia-driver=True" \
        --boot-disk-size=100 \
        --boot-disk-type=PD_SSD \
        --network="default" \
        --subnet="default" \
        --labels="env=development,app=pnkln" || {
        log_error "Failed to create Workbench instance"
        exit 1
    }

    log_success "Vertex AI Workbench created: $WORKBENCH_NAME"
    log_info "Access at: https://console.cloud.google.com/vertex-ai/workbench/user-managed"
}

configure_kubectl() {
    log_info "Configuring kubectl..."

    gcloud container clusters get-credentials "$CLUSTER_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" || {
        log_error "Failed to configure kubectl"
        exit 1
    }

    log_success "kubectl configured for cluster: $CLUSTER_NAME"
}

deploy_judge() {
    log_info "Deploying Judge 6 inference service..."

    if [ ! -f "$SCRIPT_DIR/judge-deployment.yaml" ]; then
        log_error "judge-deployment.yaml not found in $SCRIPT_DIR"
        exit 1
    fi

    kubectl apply -f "$SCRIPT_DIR/judge-deployment.yaml" || {
        log_error "Failed to deploy Judge 6"
        exit 1
    }

    log_success "Judge 6 deployed successfully"

    log_info "Waiting for deployment to be ready (timeout: 5 minutes)..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/pnkln-judge -n pnkln-inference || {
        log_error "Deployment failed to become ready"
        kubectl get pods -n pnkln-inference
        exit 1
    }

    log_success "Judge 6 is ready"
}

verify_deployment() {
    log_info "Verifying deployment..."

    echo ""
    log_info "Cluster status:"
    gcloud container clusters describe "$CLUSTER_NAME" --region="$REGION" \
        --format="table(name,status,currentNodeCount,location)"

    echo ""
    log_info "Node pools:"
    gcloud container node-pools list --cluster="$CLUSTER_NAME" --region="$REGION" \
        --format="table(name,status,machineType,autoscaling.enabled)"

    echo ""
    log_info "Pods in pnkln-inference namespace:"
    kubectl get pods -n pnkln-inference -o wide

    echo ""
    log_info "Services:"
    kubectl get svc -n pnkln-inference

    log_success "Deployment verification complete"
}

estimate_costs() {
    log_info "Estimating costs..."

    local cpu_cost=0.476  # n2-standard-16 per hour
    local gpu_cost=1.09   # L4 GPU per hour
    local workbench_cost=0.95  # n1-standard-8 + T4 per hour

    local daily_cpu=$( echo "$cpu_cost * 24" | bc )
    local daily_gpu=$( echo "$gpu_cost * 24" | bc )
    local daily_workbench=$( echo "$workbench_cost * 24" | bc )

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ESTIMATED DAILY COSTS (minimum configuration)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "  CPU pool (1 node):      \$%.2f/day\n" "$daily_cpu"
    printf "  GPU pool (0-1 nodes):   \$%.2f/day (when active)\n" "$daily_gpu"
    printf "  Vertex Workbench:       \$%.2f/day\n" "$daily_workbench"
    echo "  ─────────────────────────────────────────────────────"
    printf "  TOTAL (dev):            ~\$%.2f/day\n" "$(echo "$daily_cpu + $daily_workbench" | bc)"
    printf "  TOTAL (prod, 5 GPU):    ~\$%.2f/day\n" "$(echo "$daily_cpu + ($daily_gpu * 5) + $daily_workbench" | bc)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "  Dev limit:              \$%d/day\n" "$DAILY_DEV_LIMIT"
    printf "  Prod limit:             \$%d/day\n" "$DAILY_PROD_LIMIT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    log_warning "Set up billing alerts at: https://console.cloud.google.com/billing"
}

print_next_steps() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  DEPLOYMENT COMPLETE - NEXT STEPS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  [CRITICAL] Update API keys:"
    echo "    echo -n 'sk-ant-...' | gcloud secrets versions add anthropic-api-key --data-file=-"
    echo "    echo -n 'sk-...' | gcloud secrets versions add openai-api-key --data-file=-"
    echo "    echo -n 'xai-...' | gcloud secrets versions add xai-api-key --data-file=-"
    echo ""
    echo "  [VERIFY] Check SLA compliance:"
    echo "    ./monitor-sla.sh --once"
    echo ""
    echo "  [MONITOR] Start continuous SLA monitoring:"
    echo "    ./monitor-sla.sh --continuous"
    echo ""
    echo "  [ACCESS] Vertex AI Workbench:"
    echo "    gcloud notebooks instances describe $WORKBENCH_NAME --location=$ZONE"
    echo ""
    echo "  [COSTS] View billing:"
    echo "    make cost-estimate"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

################################################################################
# Main Execution
################################################################################

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Pnkln GKE Deployment v${VERSION}"
    echo "  Production Inference Platform on GKE Hypercomputer"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_prerequisites
    validate_project
    enable_apis
    check_quotas

    echo ""
    log_info "Starting deployment (estimated time: 30-45 minutes)..."
    echo ""

    create_gke_cluster
    configure_kubectl
    create_gpu_node_pool
    install_gpu_drivers
    setup_workload_identity
    create_secrets
    create_vertex_workbench
    deploy_judge

    verify_deployment
    estimate_costs
    print_next_steps

    echo ""
    log_success "Deployment complete!"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --version, -v  Show version"
        echo ""
        echo "Environment variables:"
        echo "  PNKLN_PROJECT_ID   GCP project ID (required)"
        echo "  PNKLN_REGION       GCP region (default: us-central1)"
        echo "  PNKLN_ZONE         GCP zone (default: us-central1-a)"
        echo "  PNKLN_CLUSTER      Cluster name (default: pnkln-inference)"
        echo "  PNKLN_WORKBENCH    Workbench name (default: pnkln-dev-workbench)"
        exit 0
        ;;
    --version|-v)
        echo "Pnkln GKE Deployment v${VERSION}"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Run '$0 --help' for usage information"
        exit 1
        ;;
esac
