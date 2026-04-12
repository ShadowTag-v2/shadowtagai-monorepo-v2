#!/bin/bash
# Pnkln GKE Inference Validation Sprint - Infrastructure Bootstrap
# Purpose: Deploy GKE Autopilot cluster with GPU support for Judge #6 validation
# Target SLA: p99 ≤ 90ms for 3-layer hybrid enforcement
# Budget: $5K cloud spend cap for 2-week validation sprint

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID="${GCP_PROJECT_ID:-pnkln-validation}"
REGION="${GCP_REGION:-us-central1}"
CLUSTER_NAME="${CLUSTER_NAME:-pnkln-core-stack}"
NETWORK_NAME="pnkln-vpc"
SUBNET_NAME="pnkln-subnet"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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

    # Check gcloud installation
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    # Check kubectl installation
    if ! command -v kubectl &> /dev/null; then
        log_warn "kubectl not found. Installing..."
        gcloud components install kubectl
    fi

    # Verify authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        log_error "Not authenticated. Run: gcloud auth login"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

set_project() {
    log_info "Setting GCP project to: ${PROJECT_ID}"
    gcloud config set project "${PROJECT_ID}"

    # Verify project exists
    if ! gcloud projects describe "${PROJECT_ID}" &> /dev/null; then
        log_error "Project ${PROJECT_ID} does not exist or you lack access"
        exit 1
    fi
}

enable_apis() {
    log_info "Enabling required GCP APIs..."

    local apis=(
        "container.googleapis.com"
        "aiplatform.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
        "compute.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "serviceusage.googleapis.com"
        "cloudbilling.googleapis.com"
    )

    for api in "${apis[@]}"; do
        log_info "Enabling ${api}..."
        gcloud services enable "${api}" --project="${PROJECT_ID}"
    done

    log_info "All APIs enabled successfully"
}

create_network() {
    log_info "Creating VPC network: ${NETWORK_NAME}"

    # Check if network already exists
    if gcloud compute networks describe "${NETWORK_NAME}" --project="${PROJECT_ID}" &> /dev/null; then
        log_warn "Network ${NETWORK_NAME} already exists, skipping creation"
        return 0
    fi

    # Create VPC network
    gcloud compute networks create "${NETWORK_NAME}" \
        --project="${PROJECT_ID}" \
        --subnet-mode=custom \
        --bgp-routing-mode=regional

    # Create subnet with secondary ranges for pods and services
    gcloud compute networks subnets create "${SUBNET_NAME}" \
        --project="${PROJECT_ID}" \
        --network="${NETWORK_NAME}" \
        --region="${REGION}" \
        --range=10.0.0.0/24 \
        --secondary-range pods=10.1.0.0/16,services=10.2.0.0/20 \
        --enable-private-ip-google-access

    log_info "Network created successfully"
}

create_gke_cluster() {
    log_info "Creating GKE Autopilot cluster: ${CLUSTER_NAME}"

    # Check if cluster already exists
    if gcloud container clusters describe "${CLUSTER_NAME}" --region="${REGION}" --project="${PROJECT_ID}" &> /dev/null; then
        log_warn "Cluster ${CLUSTER_NAME} already exists, skipping creation"
        return 0
    fi

    # Create GKE Autopilot cluster with GPU support
    gcloud container clusters create-auto "${CLUSTER_NAME}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --network="${NETWORK_NAME}" \
        --subnetwork="${SUBNET_NAME}" \
        --cluster-secondary-range-name=pods \
        --services-secondary-range-name=services \
        --release-channel=rapid \
        --enable-autoscaling \
        --min-nodes=3 \
        --max-nodes=10 \
        --enable-managed-prometheus \
        --enable-cloud-logging \
        --enable-cloud-monitoring \
        --addons=HttpLoadBalancing,HorizontalPodAutoscaling \
        --workload-pool="${PROJECT_ID}.svc.id.goog" \
        --enable-shielded-nodes \
        --shielded-secure-boot \
        --shielded-integrity-monitoring

    log_info "GKE Autopilot cluster created successfully"
}

configure_kubectl() {
    log_info "Configuring kubectl credentials..."

    gcloud container clusters get-credentials "${CLUSTER_NAME}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}"

    # Verify connection
    if kubectl cluster-info &> /dev/null; then
        log_info "kubectl configured successfully"
        kubectl cluster-info
    else
        log_error "Failed to configure kubectl"
        exit 1
    fi
}

create_namespaces() {
    log_info "Creating Kubernetes namespaces..."

    local namespaces=("pnkln-core" "pnkln-monitoring" "pnkln-workload")

    for ns in "${namespaces[@]}"; do
        if kubectl get namespace "${ns}" &> /dev/null; then
            log_warn "Namespace ${ns} already exists"
        else
            kubectl create namespace "${ns}"
            log_info "Created namespace: ${ns}"
        fi
    done
}

setup_workload_identity() {
    log_info "Setting up Workload Identity for Vertex AI access..."

    local ksa_name="pnkln-judge-sa"
    local gsa_name="pnkln-judge@${PROJECT_ID}.iam.gserviceaccount.com"
    local namespace="pnkln-core"

    # Create Google Service Account if it doesn't exist
    if ! gcloud iam service-accounts describe "${gsa_name}" --project="${PROJECT_ID}" &> /dev/null; then
        gcloud iam service-accounts create pnkln-judge \
            --display-name="Pnkln Judge Service Account" \
            --project="${PROJECT_ID}"

        # Grant Vertex AI User role
        gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
            --member="serviceAccount:${gsa_name}" \
            --role="roles/aiplatform.user"

        # Grant Monitoring Metric Writer role
        gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
            --member="serviceAccount:${gsa_name}" \
            --role="roles/monitoring.metricWriter"
    fi

    # Create Kubernetes Service Account
    kubectl create serviceaccount "${ksa_name}" \
        --namespace="${namespace}" \
        2>/dev/null || log_warn "KSA ${ksa_name} already exists"

    # Bind KSA to GSA
    gcloud iam service-accounts add-iam-policy-binding "${gsa_name}" \
        --role="roles/iam.workloadIdentityUser" \
        --member="serviceAccount:${PROJECT_ID}.svc.id.goog[${namespace}/${ksa_name}]" \
        --project="${PROJECT_ID}"

    # Annotate KSA
    kubectl annotate serviceaccount "${ksa_name}" \
        --namespace="${namespace}" \
        iam.gke.io/gcp-service-account="${gsa_name}" \
        --overwrite

    log_info "Workload Identity configured successfully"
}

deploy_gpu_operator() {
    log_info "Installing NVIDIA GPU Operator..."

    # Add NVIDIA Helm repo
    helm repo add nvidia https://helm.ngc.nvidia.com/nvidia 2>/dev/null || true
    helm repo update

    # Install GPU Operator
    helm upgrade --install gpu-operator nvidia/gpu-operator \
        --namespace gpu-operator \
        --create-namespace \
        --set driver.enabled=true \
        --wait

    log_info "GPU Operator installed successfully"
}

create_vertex_ai_workbench() {
    log_info "Creating Vertex AI Workbench instance for ops..."

    local instance_name="pnkln-ops-workbench"

    # Check if instance already exists
    if gcloud notebooks instances describe "${instance_name}" \
        --location="${REGION}" \
        --project="${PROJECT_ID}" &> /dev/null; then
        log_warn "Workbench instance ${instance_name} already exists"
        return 0
    fi

    gcloud notebooks instances create "${instance_name}" \
        --location="${REGION}" \
        --project="${PROJECT_ID}" \
        --machine-type=n1-standard-4 \
        --accelerator-type=NVIDIA_TESLA_T4 \
        --accelerator-core-count=1 \
        --install-gpu-driver \
        --network="${NETWORK_NAME}" \
        --subnet="${SUBNET_NAME}" \
        --async

    log_info "Vertex AI Workbench instance creation initiated"
}

print_summary() {
    log_info "============================================"
    log_info "GKE INFRASTRUCTURE BOOTSTRAP COMPLETE"
    log_info "============================================"
    echo ""
    log_info "Project ID: ${PROJECT_ID}"
    log_info "Region: ${REGION}"
    log_info "Cluster Name: ${CLUSTER_NAME}"
    log_info "Network: ${NETWORK_NAME}"
    echo ""
    log_info "Next Steps:"
    echo "  1. Deploy Judge #6 components: kubectl apply -f k8s/judge/"
    echo "  2. Deploy monitoring: kubectl apply -f k8s/monitoring/"
    echo "  3. Run validation workload: python src/workload-generator/synthetic_workload.py"
    echo "  4. Monitor SLA compliance: scripts/monitor-sla.sh"
    echo ""
    log_info "Cost Monitoring:"
    echo "  - Budget Alert: \$5,000 (2-week sprint cap)"
    echo "  - Track spend: scripts/cost-tracker.sh"
    echo ""
    log_warn "KILL SWITCH: If p99 > 90ms after 1 week, abort and pivot to ground-up architecture"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    log_info "Starting Pnkln GKE Infrastructure Bootstrap..."
    log_info "Target: Validation Sprint for Judge #6 (p99 ≤ 90ms SLA)"
    echo ""

    check_prerequisites
    set_project
    enable_apis
    create_network
    create_gke_cluster
    configure_kubectl
    create_namespaces
    setup_workload_identity

    # Optional: GPU operator for non-Autopilot GPU node pools
    # Autopilot manages GPU drivers automatically, but keeping this for reference
    # deploy_gpu_operator

    create_vertex_ai_workbench

    print_summary

    log_info "Bootstrap completed successfully! 🚀"
}

# Run main function
main "$@"
