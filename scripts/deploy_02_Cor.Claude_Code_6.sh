#!/bin/bash
set -euo pipefail

# ==============================================================================
# Cor.Claude_Code_6 Kubernetes Deployment Script
# ==============================================================================
# Deploys Cor.Claude_Code_6 multi-layer inference workloads to existing GKE cluster
# ==============================================================================

export PROJECT_ID="${PROJECT_ID:-shadowtagai-core-stack}"
export REGION="${REGION:-us-central1}"
export CLUSTER_NAME="${CLUSTER_NAME:-Cor.Claude_Code_6-inference}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

main() {
  log_info "Deploying Cor.Claude_Code_6 to Kubernetes..."
  log_info "Project: ${PROJECT_ID}"
  log_info "Cluster: ${CLUSTER_NAME}"

  # Get credentials
  log_info "Getting cluster credentials..."
  gcloud container clusters get-credentials "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}"

  # Apply ConfigMaps
  log_info "Applying ConfigMaps..."
  kubectl apply -f k8s/atp519_configmap.yaml

  # Apply deployment
  log_info "Applying deployment..."
  kubectl apply -f k8s/Cor.Claude_Code_6_deployment.yaml

  # Wait for readiness
  log_info "Waiting for deployment to be ready..."
  kubectl wait --for=condition=available \
    --timeout=300s \
    deployment/Cor.Claude_Code_6-inference -n Cor.Claude_Code_6-system || log_warn "Timeout waiting for deployment"

  # Show status
  log_info "\nDeployment Status:"
  kubectl get all -n Cor.Claude_Code_6-system

  log_info "\n✓ Deployment complete"
}

main "$@"
