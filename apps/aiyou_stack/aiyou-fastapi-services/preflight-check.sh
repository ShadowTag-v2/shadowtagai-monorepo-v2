#!/bin/bash
# preflight-check.sh - Pre-deployment validation for Judge 6 GKE platform
# Run this before executing pnkln-gke-deploy.sh to catch issues early

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Tracking
ERRORS=0
WARNINGS=0
CHECKS_PASSED=0
CHECKS_TOTAL=0

# Configuration
MIN_L4_GPU_QUOTA=20
MIN_N1_STANDARD_16_QUOTA=20
MIN_CPU_QUOTA=100
MIN_DISK_GB_QUOTA=2000
REQUIRED_APIS=(
    "container.googleapis.com"
    "compute.googleapis.com"
    "artifactregistry.googleapis.com"
    "secretmanager.googleapis.com"
    "cloudkms.googleapis.com"
    "logging.googleapis.com"
    "monitoring.googleapis.com"
    "aiplatform.googleapis.com"
    "notebooks.googleapis.com"
)

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"
}

print_check() {
    echo -e "${YELLOW}[CHECK]${NC} $1"
    ((CHECKS_TOTAL++))
}

print_pass() {
    echo -e "${GREEN}  ✓${NC} $1"
    ((CHECKS_PASSED++))
}

print_warn() {
    echo -e "${YELLOW}  ⚠${NC} $1"
    ((WARNINGS++))
}

print_fail() {
    echo -e "${RED}  ✗${NC} $1"
    ((ERRORS++))
}

print_info() {
    echo -e "    ℹ $1"
}

# Banner
clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   PNKLN JUDGE #6 - PRE-FLIGHT VALIDATION                         ║
║   GKE Inference Platform Deployment Readiness                     ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF

# START CHECKS
print_header "1. ENVIRONMENT & PREREQUISITES"

# Check: gcloud installed
print_check "Google Cloud SDK (gcloud) installed"
if command -v gcloud &> /dev/null; then
    VERSION=$(gcloud version --format="value(core)" 2>/dev/null || echo "unknown")
    print_pass "gcloud installed (version: $VERSION)"
else
    print_fail "gcloud not found"
    print_info "Install from: https://cloud.google.com/sdk/docs/install"
fi

# Check: kubectl installed
print_check "Kubernetes CLI (kubectl) installed"
if command -v kubectl &> /dev/null; then
    VERSION=$(kubectl version --client --short 2>/dev/null | grep -oP 'v\d+\.\d+\.\d+' || echo "unknown")
    print_pass "kubectl installed (version: $VERSION)"
else
    print_fail "kubectl not found"
    print_info "Install: gcloud components install kubectl"
fi

# Check: terraform installed (optional but recommended)
print_check "Terraform installed (optional)"
if command -v terraform &> /dev/null; then
    VERSION=$(terraform version -json 2>/dev/null | grep -oP '"terraform_version":"\K[^"]+' || echo "unknown")
    print_pass "terraform installed (version: $VERSION)"
else
    print_warn "terraform not found (optional for IaC deployment)"
    print_info "Install from: https://www.terraform.io/downloads"
fi

# Check: jq installed
print_check "JSON processor (jq) installed"
if command -v jq &> /dev/null; then
    print_pass "jq installed"
else
    print_warn "jq not found (recommended for JSON parsing)"
    print_info "Install: apt-get install jq (Debian/Ubuntu) or brew install jq (macOS)"
fi

# Check: Environment variables
print_check "Environment variables configured"
if [[ -n "${PNKLN_PROJECT_ID:-}" ]]; then
    print_pass "PNKLN_PROJECT_ID set: $PNKLN_PROJECT_ID"
    PROJECT_ID="$PNKLN_PROJECT_ID"
elif [[ -n "${PROJECT_ID:-}" ]]; then
    print_pass "PROJECT_ID set: $PROJECT_ID"
else
    print_fail "PROJECT_ID not set"
    print_info "Set with: export PNKLN_PROJECT_ID='your-project-id'"
    PROJECT_ID=""
fi

# If no project ID, can't continue with GCP-specific checks
if [[ -z "$PROJECT_ID" ]]; then
    print_fail "Cannot continue without PROJECT_ID - skipping GCP checks"
    echo -e "\n${RED}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}CRITICAL: Set PROJECT_ID and re-run this script${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════════${NC}"
    exit 1
fi

print_header "2. GCP AUTHENTICATION & PROJECT"

# Check: gcloud authenticated
print_check "gcloud authentication"
if gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)
    print_pass "Authenticated as: $ACCOUNT"
else
    print_fail "Not authenticated to gcloud"
    print_info "Run: gcloud auth login"
fi

# Check: Application Default Credentials
print_check "Application Default Credentials (ADC)"
if gcloud auth application-default print-access-token &> /dev/null; then
    print_pass "ADC configured"
else
    print_warn "ADC not configured"
    print_info "Run: gcloud auth application-default login"
fi

# Check: Project exists and is accessible
print_check "Project '$PROJECT_ID' exists and is accessible"
if gcloud projects describe "$PROJECT_ID" &> /dev/null; then
    PROJECT_NAME=$(gcloud projects describe "$PROJECT_ID" --format="value(name)")
    PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
    print_pass "Project accessible: $PROJECT_NAME (number: $PROJECT_NUMBER)"
else
    print_fail "Cannot access project '$PROJECT_ID'"
    print_info "Check project ID or permissions"
fi

# Check: Default project set
print_check "Default project configuration"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [[ "$CURRENT_PROJECT" == "$PROJECT_ID" ]]; then
    print_pass "Default project set correctly"
else
    print_warn "Default project is '$CURRENT_PROJECT', not '$PROJECT_ID'"
    print_info "Run: gcloud config set project $PROJECT_ID"
fi

# Check: Billing account active
print_check "Billing account linked and active"
if gcloud beta billing projects describe "$PROJECT_ID" --format="value(billingEnabled)" 2>/dev/null | grep -q "True"; then
    BILLING_ACCOUNT=$(gcloud beta billing projects describe "$PROJECT_ID" --format="value(billingAccountName)" 2>/dev/null || echo "unknown")
    print_pass "Billing enabled (account: $BILLING_ACCOUNT)"
else
    print_fail "Billing not enabled for project"
    print_info "Link billing: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
fi

print_header "3. GCP APIS ENABLED"

for API in "${REQUIRED_APIS[@]}"; do
    print_check "API: $API"
    if gcloud services list --enabled --project="$PROJECT_ID" 2>/dev/null | grep -q "$API"; then
        print_pass "$API enabled"
    else
        print_fail "$API not enabled"
        print_info "Enable with: gcloud services enable $API --project=$PROJECT_ID"
    fi
done

print_header "4. COMPUTE QUOTAS & LIMITS"

# Helper function to get quota
get_quota() {
    local METRIC=$1
    local REGION=${2:-}

    if [[ -n "$REGION" ]]; then
        gcloud compute regions describe "$REGION" \
            --project="$PROJECT_ID" \
            --format="value(quotas.filter(metric=$METRIC).limit)" 2>/dev/null | head -1
    else
        gcloud compute project-info describe \
            --project="$PROJECT_ID" \
            --format="value(quotas.filter(metric=$METRIC).limit)" 2>/dev/null | head -1
    fi
}

REGION="${REGION:-us-central1}"

# Check: L4 GPU quota
print_check "NVIDIA L4 GPU quota (need: $MIN_L4_GPU_QUOTA)"
L4_QUOTA=$(get_quota "NVIDIA_L4_GPUS" "$REGION" || echo "0")
if [[ "$L4_QUOTA" -ge "$MIN_L4_GPU_QUOTA" ]]; then
    print_pass "L4 GPU quota: $L4_QUOTA (sufficient)"
else
    print_warn "L4 GPU quota: $L4_QUOTA (need $MIN_L4_GPU_QUOTA)"
    print_info "Request increase: https://console.cloud.google.com/iam-admin/quotas?project=$PROJECT_ID"
    print_info "Search for: 'NVIDIA L4 GPUs' in region $REGION"
fi

# Check: n1-standard-16 quota
print_check "n1-standard-16 instance quota (need: $MIN_N1_STANDARD_16_QUOTA)"
N1_QUOTA=$(get_quota "N1_CPUS" "$REGION" || echo "0")
if [[ "$N1_QUOTA" -ge "$((MIN_N1_STANDARD_16_QUOTA * 16))" ]]; then
    INSTANCES=$((N1_QUOTA / 16))
    print_pass "N1 CPU quota: $N1_QUOTA (supports $INSTANCES instances)"
else
    print_warn "N1 CPU quota: $N1_QUOTA (need $((MIN_N1_STANDARD_16_QUOTA * 16)) for $MIN_N1_STANDARD_16_QUOTA instances)"
    print_info "Request increase for N1_CPUS in region $REGION"
fi

# Check: Total CPU quota
print_check "Total CPU quota (need: $MIN_CPU_QUOTA)"
CPU_QUOTA=$(get_quota "CPUS" "$REGION" || echo "0")
if [[ "$CPU_QUOTA" -ge "$MIN_CPU_QUOTA" ]]; then
    print_pass "CPU quota: $CPU_QUOTA (sufficient)"
else
    print_warn "CPU quota: $CPU_QUOTA (need $MIN_CPU_QUOTA)"
fi

# Check: Disk quota
print_check "Persistent disk quota (need: ${MIN_DISK_GB_QUOTA}GB)"
DISK_QUOTA=$(get_quota "SSD_TOTAL_GB" "$REGION" || echo "0")
if [[ "$DISK_QUOTA" -ge "$MIN_DISK_GB_QUOTA" ]]; then
    print_pass "SSD disk quota: ${DISK_QUOTA}GB (sufficient)"
else
    print_warn "SSD disk quota: ${DISK_QUOTA}GB (need ${MIN_DISK_GB_QUOTA}GB)"
fi

# Check: In-use IP addresses
print_check "In-use IP addresses quota"
IP_QUOTA=$(get_quota "IN_USE_ADDRESSES" "$REGION" || echo "0")
IP_LIMIT=$(gcloud compute regions describe "$REGION" --project="$PROJECT_ID" --format="value(quotas.filter(metric=IN_USE_ADDRESSES).limit)" 2>/dev/null | head -1 || echo "unknown")
print_pass "IP addresses: $IP_QUOTA used (limit: $IP_LIMIT)"

print_header "5. IAM PERMISSIONS"

# Check: Required roles
print_check "IAM roles for current user"
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)

# Check if user has necessary permissions (simplified check)
if gcloud projects get-iam-policy "$PROJECT_ID" --flatten="bindings[].members" --filter="bindings.members:$ACCOUNT" --format="value(bindings.role)" 2>/dev/null | grep -qE "(roles/owner|roles/editor|roles/container.admin)"; then
    ROLES=$(gcloud projects get-iam-policy "$PROJECT_ID" --flatten="bindings[].members" --filter="bindings.members:$ACCOUNT" --format="value(bindings.role)" 2>/dev/null | tr '\n' ', ')
    print_pass "User has sufficient roles: $ROLES"
else
    print_warn "User may lack sufficient permissions"
    print_info "Required roles: roles/container.admin, roles/compute.admin, roles/iam.serviceAccountAdmin"
fi

print_header "6. NETWORKING"

# Check: Default VPC exists
print_check "Default VPC network"
if gcloud compute networks describe default --project="$PROJECT_ID" &> /dev/null; then
    print_pass "Default VPC exists"
else
    print_warn "Default VPC not found"
    print_info "Create with: gcloud compute networks create default --subnet-mode=auto"
fi

# Check: Firewall rules
print_check "Firewall rules for GKE"
FIREWALL_COUNT=$(gcloud compute firewall-rules list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l)
if [[ "$FIREWALL_COUNT" -gt 0 ]]; then
    print_pass "Firewall rules configured ($FIREWALL_COUNT rules)"
else
    print_warn "No firewall rules found"
fi

# Check: Internet connectivity
print_check "Internet connectivity (gcr.io)"
if timeout 5 curl -s -o /dev/null -w "%{http_code}" https://gcr.io 2>/dev/null | grep -q "200\|302\|301"; then
    print_pass "Can reach gcr.io (container registry)"
else
    print_warn "Cannot reach gcr.io - check network/firewall"
fi

print_header "7. EXISTING RESOURCES"

# Check: Existing GKE clusters
print_check "Existing GKE clusters in project"
CLUSTER_COUNT=$(gcloud container clusters list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l)
if [[ "$CLUSTER_COUNT" -eq 0 ]]; then
    print_pass "No existing clusters (clean slate)"
else
    CLUSTERS=$(gcloud container clusters list --project="$PROJECT_ID" --format="value(name,location)" 2>/dev/null | tr '\n' ', ')
    print_warn "Found $CLUSTER_COUNT existing cluster(s): $CLUSTERS"
    print_info "Deployment will create new cluster or update existing"
fi

# Check: Artifact Registry repositories
print_check "Artifact Registry repositories"
REPO_COUNT=$(gcloud artifacts repositories list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l)
if [[ "$REPO_COUNT" -gt 0 ]]; then
    print_pass "Found $REPO_COUNT existing repository(ies)"
else
    print_info "No repositories found - will be created during deployment"
fi

# Check: Secret Manager secrets
print_check "Secret Manager secrets"
SECRET_COUNT=$(gcloud secrets list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l)
if [[ "$SECRET_COUNT" -gt 0 ]]; then
    print_pass "Found $SECRET_COUNT existing secret(s)"
else
    print_warn "No secrets found - you'll need to add API keys after deployment"
    print_info "Required secrets: anthropic-api-key, openai-api-key, xai-api-key, mistral-api-key"
fi

print_header "8. COST ESTIMATION"

# Rough cost estimation
print_check "Deployment cost estimation"
cat << 'EOF'
  Estimated daily costs:

  DEVELOPMENT (minimal):
    • 1 CPU node (e2-standard-4)              ~$5/day
    • 0-1 GPU node (L4, spot)                 ~$5-12/day
    • Artifact Registry + Storage             ~$2/day
    • Cloud Monitoring                        ~$1/day
    ─────────────────────────────────────────────────
    TOTAL DEV:                                ~$13-20/day

  PRODUCTION (full scale):
    • 3-10 CPU nodes (n2-standard-16)         ~$100-350/day
    • 5-20 GPU nodes (L4, spot)               ~$60-240/day
    • LLM API calls (varies by usage)         ~$50-200/day
    • Vertex AI Workbench                     ~$20/day
    • Storage + Registry + Monitoring         ~$10/day
    ─────────────────────────────────────────────────
    TOTAL PROD:                               ~$240-820/day

  ⚠️  Ensure billing alerts are configured for $500/day threshold
EOF
print_pass "Cost estimates provided above"

print_header "9. DEPLOYMENT FILES"

# Check: Required deployment files exist
FILES_TO_CHECK=(
    "pnkln-gke-deploy.sh"
    "judge-deployment.yaml"
    "monitor-sla.sh"
    "Makefile"
)

for FILE in "${FILES_TO_CHECK[@]}"; do
    print_check "File: $FILE"
    if [[ -f "$FILE" ]]; then
        SIZE=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE" 2>/dev/null || echo "unknown")
        print_pass "$FILE exists (size: $SIZE bytes)"
    else
        print_fail "$FILE not found"
        print_info "Ensure you're running this from the project root directory"
    fi
done

# Check: Terraform files (optional)
if [[ -d "terraform" ]]; then
    print_check "Terraform infrastructure files"
    if [[ -f "terraform/main.tf" ]]; then
        print_pass "Terraform configuration found"
    else
        print_warn "terraform/ directory exists but main.tf not found"
    fi
fi

print_header "10. SECURITY VALIDATION"

# Check: Service account key files (should NOT exist in repo)
print_check "No service account keys in repository"
if find . -name "*.json" -type f 2>/dev/null | grep -qE "(key|credential|service-account)"; then
    print_warn "Found JSON files that may contain credentials"
    print_info "Ensure no service account keys are committed to git"
else
    print_pass "No credential files found in repository"
fi

# Check: .gitignore exists
print_check ".gitignore file configured"
if [[ -f ".gitignore" ]]; then
    if grep -q "*.json" .gitignore && grep -q "*.key" .gitignore; then
        print_pass ".gitignore configured to exclude sensitive files"
    else
        print_warn ".gitignore may not exclude all sensitive files"
        print_info "Add: *.json, *.key, .env, credentials/"
    fi
else
    print_warn ".gitignore not found"
fi

# SUMMARY
print_header "PRE-FLIGHT VALIDATION SUMMARY"

echo -e "${BLUE}Total Checks:${NC}    $CHECKS_TOTAL"
echo -e "${GREEN}Passed:${NC}         $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC}       $WARNINGS"
echo -e "${RED}Errors:${NC}         $ERRORS"
echo ""

if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    cat << EOF
${GREEN}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT                    ║
║                                                                   ║
║   Next steps:                                                     ║
║   1. ./pnkln-gke-deploy.sh                                       ║
║   2. Update API keys in Secret Manager                           ║
║   3. kubectl apply -f judge-deployment.yaml                      ║
║   4. ./monitor-sla.sh --continuous                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝${NC}
EOF
    exit 0
elif [[ $ERRORS -eq 0 ]]; then
    cat << EOF
${YELLOW}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ⚠️  DEPLOYMENT POSSIBLE WITH WARNINGS                          ║
║                                                                   ║
║   $WARNINGS warning(s) found - review above and proceed with     ║
║   caution. Warnings may cause sub-optimal configuration or       ║
║   reduced functionality.                                          ║
║                                                                   ║
║   To proceed: ./pnkln-gke-deploy.sh                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝${NC}
EOF
    exit 0
else
    cat << EOF
${RED}╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ❌ DEPLOYMENT BLOCKED - CRITICAL ERRORS FOUND                  ║
║                                                                   ║
║   $ERRORS error(s) and $WARNINGS warning(s) found.                           ║
║   Review the failed checks above and resolve all errors          ║
║   before proceeding with deployment.                              ║
║                                                                   ║
║   Common fixes:                                                   ║
║   • Enable required APIs                                          ║
║   • Link billing account                                          ║
║   • Request quota increases                                       ║
║   • Set PROJECT_ID environment variable                           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝${NC}
EOF
    exit 1
fi
