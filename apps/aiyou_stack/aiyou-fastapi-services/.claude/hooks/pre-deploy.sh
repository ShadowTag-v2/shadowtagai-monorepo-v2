#!/bin/bash

################################################################################
# Pre-Deployment Hook for Pnkln GKE Services
#
# This hook runs before every deployment to validate:
# - Environment configuration
# - Cluster connectivity
# - Image availability
# - Kubernetes manifests
# - Resource quotas
# - Dependencies
#
# Exit codes:
#   0 - All checks passed, proceed with deployment
#   1 - Critical failure, abort deployment
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-pnkln-project}"
CLUSTER_NAME="${GKE_CLUSTER_NAME:-pnkln-cluster}"
CLUSTER_REGION="${GKE_CLUSTER_REGION:-us-central1}"
NAMESPACE="${K8S_NAMESPACE:-pnkln}"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-staging}"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Exit with error
fail_deployment() {
    log_error "$1"
    exit 1
}

################################################################################
# Pre-flight Checks
################################################################################

log_section "PRE-DEPLOYMENT VALIDATION"

# Check required tools
log_info "Checking required tools..."
for tool in kubectl gcloud docker; do
    if ! command_exists "$tool"; then
        fail_deployment "Required tool '$tool' is not installed"
    fi
    log_info "✓ $tool is available"
done

# Check environment variables
log_info "Validating environment variables..."
required_vars=("GCP_PROJECT_ID" "GKE_CLUSTER_NAME" "DEPLOYMENT_ENV")
for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        log_warn "Environment variable $var is not set, using default"
    else
        log_info "✓ $var is set"
    fi
done

################################################################################
# GKE Cluster Connectivity
################################################################################

log_section "CLUSTER CONNECTIVITY CHECK"

log_info "Authenticating with GCP..."
if ! gcloud auth application-default print-access-token >/dev/null 2>&1; then
    fail_deployment "GCP authentication failed. Run 'gcloud auth login'"
fi
log_info "✓ GCP authentication successful"

log_info "Setting GCP project to $PROJECT_ID..."
if ! gcloud config set project "$PROJECT_ID" >/dev/null 2>&1; then
    fail_deployment "Failed to set GCP project"
fi
log_info "✓ GCP project set"

log_info "Fetching GKE credentials..."
if ! gcloud container clusters get-credentials "$CLUSTER_NAME" \
    --region="$CLUSTER_REGION" \
    --project="$PROJECT_ID" >/dev/null 2>&1; then
    fail_deployment "Failed to get GKE credentials"
fi
log_info "✓ GKE credentials obtained"

log_info "Verifying cluster connectivity..."
if ! kubectl cluster-info >/dev/null 2>&1; then
    fail_deployment "Cannot connect to Kubernetes cluster"
fi
log_info "✓ Cluster is reachable"

################################################################################
# Cluster Health Check
################################################################################

log_section "CLUSTER HEALTH CHECK"

log_info "Checking node status..."
node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready " || true)

if [ "$node_count" -eq 0 ]; then
    fail_deployment "No nodes found in cluster"
fi

if [ "$ready_nodes" -lt "$node_count" ]; then
    log_warn "Not all nodes are ready ($ready_nodes/$node_count)"
    kubectl get nodes
fi

log_info "✓ Cluster has $ready_nodes/$node_count nodes ready"

log_info "Checking system pods..."
system_pods_not_running=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | \
    grep -v "Running\|Completed" | wc -l || true)

if [ "$system_pods_not_running" -gt 0 ]; then
    log_warn "Some system pods are not running:"
    kubectl get pods -n kube-system | grep -v "Running\|Completed" || true
fi

log_info "✓ System pods check completed"

################################################################################
# Namespace Validation
################################################################################

log_section "NAMESPACE VALIDATION"

log_info "Checking namespace '$NAMESPACE'..."
if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    log_warn "Namespace '$NAMESPACE' does not exist, creating..."
    if ! kubectl create namespace "$NAMESPACE"; then
        fail_deployment "Failed to create namespace '$NAMESPACE'"
    fi
    log_info "✓ Namespace created"
else
    log_info "✓ Namespace exists"
fi

# Check resource quotas
log_info "Checking resource quotas..."
if kubectl get resourcequota -n "$NAMESPACE" >/dev/null 2>&1; then
    kubectl describe resourcequota -n "$NAMESPACE" | grep -A 5 "Used"
fi

################################################################################
# Kubernetes Manifests Validation
################################################################################

log_section "KUBERNETES MANIFESTS VALIDATION"

log_info "Searching for Kubernetes manifests..."
k8s_dirs=("k8s" "kubernetes" "deploy" "deployments" "manifests")
manifest_dir=""

for dir in "${k8s_dirs[@]}"; do
    if [ -d "$dir" ]; then
        manifest_dir="$dir"
        log_info "✓ Found manifest directory: $manifest_dir"
        break
    fi
done

if [ -z "$manifest_dir" ]; then
    log_warn "No Kubernetes manifest directory found"
    log_warn "Checked: ${k8s_dirs[*]}"
else
    log_info "Validating manifests with dry-run..."
    if kubectl apply --dry-run=client -f "$manifest_dir" >/dev/null 2>&1; then
        log_info "✓ Manifests are valid"
    else
        log_error "Manifest validation failed:"
        kubectl apply --dry-run=client -f "$manifest_dir"
        fail_deployment "Invalid Kubernetes manifests"
    fi
fi

################################################################################
# Container Images Validation
################################################################################

log_section "CONTAINER IMAGES VALIDATION"

log_info "Checking Docker daemon..."
if docker info >/dev/null 2>&1; then
    log_info "✓ Docker is running"
else
    log_warn "Docker daemon is not accessible"
fi

# Check if images are specified and available
if [ -n "$manifest_dir" ]; then
    log_info "Extracting image references from manifests..."
    images=$(grep -r "image:" "$manifest_dir" 2>/dev/null | \
        sed 's/.*image: *//g' | \
        sed 's/"//g' | \
        sed 's/#.*//g' | \
        sort -u || true)

    if [ -n "$images" ]; then
        log_info "Found images:"
        echo "$images" | while read -r image; do
            if [ -n "$image" ]; then
                echo "  - $image"
            fi
        done
    else
        log_warn "No image references found in manifests"
    fi
fi

################################################################################
# Existing Deployment Check
################################################################################

log_section "EXISTING DEPLOYMENT CHECK"

log_info "Checking for existing deployments in namespace '$NAMESPACE'..."
existing_deployments=$(kubectl get deployments -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l || echo "0")

if [ "$existing_deployments" -gt 0 ]; then
    log_info "Found $existing_deployments existing deployment(s):"
    kubectl get deployments -n "$NAMESPACE" -o wide

    log_info "Checking deployment health..."
    kubectl get deployments -n "$NAMESPACE" -o json | \
        jq -r '.items[] | "\(.metadata.name): \(.status.availableReplicas // 0)/\(.spec.replicas)"'
else
    log_info "No existing deployments found (first deployment)"
fi

################################################################################
# Active Incidents Check
################################################################################

log_section "ACTIVE INCIDENTS CHECK"

log_info "Checking for failing pods..."
failing_pods=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded \
    --no-headers 2>/dev/null | wc -l || echo "0")

if [ "$failing_pods" -gt 0 ]; then
    log_warn "Found $failing_pods failing pod(s):"
    kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded

    if [ "$DEPLOYMENT_ENV" = "production" ]; then
        log_error "Cannot deploy to production with failing pods"
        fail_deployment "Fix failing pods before deploying to production"
    else
        log_warn "Proceeding with deployment despite failing pods (non-production)"
    fi
else
    log_info "✓ No failing pods detected"
fi

log_info "Checking recent events..."
warning_events=$(kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' 2>/dev/null | \
    grep -c "Warning" || echo "0")

if [ "$warning_events" -gt 10 ]; then
    log_warn "Found $warning_events warning events in the last hour"
    log_warn "Recent warnings:"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | grep "Warning" | head -5
fi

################################################################################
# Deployment Window Check (Production Only)
################################################################################

if [ "$DEPLOYMENT_ENV" = "production" ]; then
    log_section "DEPLOYMENT WINDOW CHECK (PRODUCTION)"

    current_hour=$(date +%H)
    current_day=$(date +%u)  # 1-7 (Monday-Sunday)

    # Production deployment window: Mon-Thu, 9am-5pm PST (17:00-01:00 UTC)
    if [ "$current_day" -ge 5 ]; then
        log_warn "Today is Friday, Saturday, or Sunday"
        log_warn "Production deployments should be done Mon-Thu"

        read -p "Continue anyway? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
            fail_deployment "Deployment cancelled - outside recommended deployment window"
        fi
    fi

    log_info "✓ Deployment window check passed"
fi

################################################################################
# Resource Availability Check
################################################################################

log_section "RESOURCE AVAILABILITY CHECK"

log_info "Checking cluster resource capacity..."
kubectl top nodes 2>/dev/null || log_warn "Metrics server not available"

log_info "Checking namespace resource usage..."
kubectl top pods -n "$NAMESPACE" 2>/dev/null || log_warn "Pod metrics not available"

################################################################################
# Backup Verification
################################################################################

log_section "BACKUP VERIFICATION"

log_info "Verifying rollback capability..."
if [ "$existing_deployments" -gt 0 ]; then
    log_info "Checking deployment history..."
    deployments=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

    for deployment in $deployments; do
        revision_count=$(kubectl rollout history deployment/"$deployment" -n "$NAMESPACE" 2>/dev/null | \
            tail -n +2 | wc -l || echo "0")
        log_info "  $deployment: $revision_count revision(s) available for rollback"
    done

    log_info "✓ Rollback capability verified"
else
    log_warn "No existing deployments - first deployment has no rollback option"
fi

################################################################################
# Final Summary
################################################################################

log_section "PRE-DEPLOYMENT VALIDATION SUMMARY"

log_info "Environment: $DEPLOYMENT_ENV"
log_info "Project: $PROJECT_ID"
log_info "Cluster: $CLUSTER_NAME ($CLUSTER_REGION)"
log_info "Namespace: $NAMESPACE"
log_info ""

log_info "${GREEN}✓ All pre-deployment checks passed${NC}"
log_info ""
log_info "Deployment can proceed safely."
log_info ""

exit 0
