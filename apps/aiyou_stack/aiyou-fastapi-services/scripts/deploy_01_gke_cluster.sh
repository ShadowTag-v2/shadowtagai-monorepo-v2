#!/bin/bash
set -euo pipefail

# ==============================================================================
# GKE Standard Cluster Deployment with GPU Support
# ==============================================================================
#
# CRITICAL FIX: Changed from Autopilot to Standard GKE
# Reason: Autopilot does not support manually managed GPU node pools
#
# This script creates:
# 1. GKE Standard cluster with private nodes and Workload Identity
# 2. GPU node pool with NVIDIA L4 accelerators
# 3. Configures docker authentication for GCR
#
# Prerequisites:
# - gcloud CLI installed and authenticated
# - Project with billing enabled
# - Required APIs enabled (see enable_apis function)
# ==============================================================================

# Configuration
export PROJECT_ID="${PROJECT_ID:-shadowtagai-core-stack}"
export CLUSTER_NAME="${CLUSTER_NAME:-Claude_Code_6-inference}"
export REGION="${REGION:-us-central1}"
export NETWORK="${NETWORK:-default}"
export SUBNETWORK="${SUBNETWORK:-default}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Enable required APIs
enable_apis() {
  log_info "Enabling required GCP APIs..."

  local apis=(
    "container.googleapis.com"
    "compute.googleapis.com"
    "aiplatform.googleapis.com"
    "artifactregistry.googleapis.com"
    "cloudkms.googleapis.com"
    "secretmanager.googleapis.com"
    "monitoring.googleapis.com"
    "logging.googleapis.com"
    "binaryauthorization.googleapis.com"
  )

  for api in "${apis[@]}"; do
    log_info "Enabling ${api}..."
    gcloud services enable "${api}" \
      --project="${PROJECT_ID}" || log_warn "Failed to enable ${api} (may already be enabled)"
  done
}

# Create GKE Standard cluster
create_cluster() {
  log_info "Creating GKE Standard cluster: ${CLUSTER_NAME}"
  log_info "Region: ${REGION}"
  log_info "Project: ${PROJECT_ID}"

  # Check if cluster already exists
  if gcloud container clusters describe "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    log_warn "Cluster ${CLUSTER_NAME} already exists. Skipping creation."
    return 0
  fi

  gcloud container clusters create "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --network="${NETWORK}" \
    --subnetwork="${SUBNETWORK}" \
    --enable-ip-alias \
    --enable-private-nodes \
    --enable-private-endpoint \
    --master-ipv4-cidr="172.16.0.0/28" \
    --cluster-version="latest" \
    --release-channel="rapid" \
    --enable-shielded-nodes \
    --shielded-secure-boot \
    --shielded-integrity-monitoring \
    --enable-autorepair \
    --enable-autoupgrade \
    --workload-pool="${PROJECT_ID}.svc.id.goog" \
    --enable-stackdriver-kubernetes \
    --logging=SYSTEM,WORKLOAD \
    --monitoring=SYSTEM \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
    --machine-type="n2-standard-4" \
    --num-nodes=1 \
    --min-nodes=1 \
    --max-nodes=5 \
    --enable-autoscaling \
    --disk-type="pd-standard" \
    --disk-size="100" \
    --metadata disable-legacy-endpoints=true \
    --max-pods-per-node=110 \
    --default-max-pods-per-node=110 \
    --enable-network-policy \
    --binauthz-evaluation-mode=PROJECT_SINGLETON_POLICY_ENFORCE

  log_info "Cluster ${CLUSTER_NAME} created successfully"
}

# Create GPU node pool
create_gpu_node_pool() {
  log_info "Creating GPU node pool: judge-gpu-pool"

  # Check if node pool already exists
  if gcloud container node-pools describe "judge-gpu-pool" \
    --cluster="${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    log_warn "GPU node pool already exists. Skipping creation."
    return 0
  fi

  gcloud container node-pools create "judge-gpu-pool" \
    --cluster="${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --machine-type="g2-standard-8" \
    --accelerator="type=nvidia-l4,count=1" \
    --num-nodes=0 \
    --min-nodes=0 \
    --max-nodes=3 \
    --enable-autoscaling \
    --enable-autorepair \
    --enable-autoupgrade \
    --spot \
    --disk-type="pd-balanced" \
    --disk-size="200" \
    --metadata="disable-legacy-endpoints=true" \
    --scopes="https://www.googleapis.com/auth/cloud-platform" \
    --enable-autoprovisioning \
    --node-labels="workload=gpu-inference,accelerator=nvidia-l4" \
    --node-taints="nvidia.com/gpu=present:NoSchedule"

  log_info "GPU node pool created successfully"

  # Install GPU drivers
  log_info "Installing NVIDIA GPU drivers..."
  kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded-latest.yaml || log_warn "GPU driver installation may have failed"
}

# Get cluster credentials
get_credentials() {
  log_info "Getting cluster credentials..."
  gcloud container clusters get-credentials "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}"

  log_info "Current context:"
  kubectl config current-context
}

# Configure Docker authentication for GCR/Artifact Registry
configure_docker_auth() {
  log_info "Configuring Docker authentication for GCR..."

  # Configure docker-credential-gcr
  gcloud auth configure-docker --quiet || log_warn "Docker auth configuration may have failed"

  # Also configure for Artifact Registry
  gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet || log_warn "Artifact Registry docker auth may have failed"

  log_info "Docker authentication configured"
}

# Create namespaces and basic setup
setup_cluster() {
  log_info "Setting up cluster namespaces and basic resources..."

  # Create namespaces
  kubectl create namespace Claude_Code_6-system --dry-run=client -o yaml | kubectl apply -f -
  kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

  # Label namespaces
  kubectl label namespace Claude_Code_6-system name=Claude_Code_6-system --overwrite
  kubectl label namespace monitoring name=monitoring --overwrite

  log_info "Cluster setup complete"
}

# Main execution
main() {
  log_info "Starting GKE cluster deployment..."
  log_info "====================================="

  # Validate required tools
  command -v gcloud >/dev/null 2>&1 || { log_error "gcloud CLI is required but not installed. Aborting."; exit 1; }
  command -v kubectl >/dev/null 2>&1 || { log_error "kubectl is required but not installed. Aborting."; exit 1; }

  # Set project
  log_info "Setting project to: ${PROJECT_ID}"
  gcloud config set project "${PROJECT_ID}"

  # Execute deployment steps
  enable_apis
  create_cluster
  get_credentials
  create_gpu_node_pool
  configure_docker_auth
  setup_cluster

  log_info "====================================="
  log_info "GKE cluster deployment completed successfully!"
  log_info ""
  log_info "Next steps:"
  log_info "1. Build and push container images: ./scripts/master_deploy.sh build"
  log_info "2. Deploy Claude_Code_6 workloads: ./scripts/deploy_02_Claude_Code_6.sh"
  log_info "3. Verify GPU nodes: kubectl get nodes -l accelerator=nvidia-l4"
  log_info ""
  log_info "Cluster info:"
  kubectl cluster-info
}

main "$@"
