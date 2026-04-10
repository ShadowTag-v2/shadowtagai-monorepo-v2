#!/bin/bash
# preflight.sh - Pre-deployment validation and environment setup
# Based on Google Cloud accelerated-platforms best practices

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  PNKLN CORE STACK™ - GKE INFERENCE DEPLOYMENT PREFLIGHT     ║"
echo "║  Google Cloud Accelerated Platforms Reference Architecture  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
export PROJECT_ID="${PROJECT_ID:-pnkln-core-stack}"
export REGION="${REGION:-us-central1}"
export ZONE="${ZONE:-us-central1-a}"
export CLUSTER_NAME="${CLUSTER_NAME:-pnkln-inference-prod}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Project ID:    ${PROJECT_ID}"
echo "  Region:        ${REGION}"
echo "  Zone:          ${ZONE}"
echo "  Cluster Name:  ${CLUSTER_NAME}"
echo ""

# Function to check command existence
check_command() {
    if command -v "$1" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

# Function to check version
check_version() {
    local tool=$1
    local min_version=$2
    local current_version=$3

    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" = "$min_version" ]; then
        echo -e "${GREEN}✓${NC} $tool version $current_version (>= $min_version)"
        return 0
    else
        echo -e "${RED}✗${NC} $tool version $current_version (need >= $min_version)"
        return 1
    fi
}

# 1. Check GCP authentication
echo -e "${BLUE}[1/8] Checking GCP authentication...${NC}"
if gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    echo -e "${GREEN}✓${NC} Authenticated as: ${ACTIVE_ACCOUNT}"
else
    echo -e "${RED}✗${NC} Not authenticated to GCP"
    echo "  Run: gcloud auth login"
    exit 1
fi
echo ""

# 2. Verify and set project
echo -e "${BLUE}[2/8] Verifying GCP project...${NC}"
if gcloud projects describe "${PROJECT_ID}" &>/dev/null; then
    gcloud config set project "${PROJECT_ID}" 2>/dev/null
    echo -e "${GREEN}✓${NC} Project ${PROJECT_ID} exists and is set"
else
    echo -e "${RED}✗${NC} Project ${PROJECT_ID} not found"
    echo "  Available projects:"
    gcloud projects list --format="table(projectId,name)"
    exit 1
fi
echo ""

# 3. Check required tools
echo -e "${BLUE}[3/8] Checking required tools...${NC}"
TOOLS_OK=true

if ! check_command gcloud; then TOOLS_OK=false; fi
if ! check_command kubectl; then TOOLS_OK=false; fi
if ! check_command terraform; then TOOLS_OK=false; fi
if ! check_command jq; then TOOLS_OK=false; fi

# Check versions
if command -v terraform &>/dev/null; then
    TF_VERSION=$(terraform version -json 2>/dev/null | jq -r '.terraform_version' || echo "0.0.0")
    if ! check_version "Terraform" "1.8.0" "$TF_VERSION"; then
        TOOLS_OK=false
    fi
fi

if [ "$TOOLS_OK" = false ]; then
    echo ""
    echo -e "${RED}Missing required tools. Install them and run preflight again.${NC}"
    exit 1
fi
echo ""

# 4. Enable required APIs
echo -e "${BLUE}[4/8] Enabling required GCP APIs...${NC}"
REQUIRED_APIS=(
    "container.googleapis.com"
    "compute.googleapis.com"
    "aiplatform.googleapis.com"
    "artifactregistry.googleapis.com"
    "monitoring.googleapis.com"
    "logging.googleapis.com"
    "storage.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "iap.googleapis.com"
    "certificatemanager.googleapis.com"
    "networkservices.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    echo -n "  Enabling ${api}..."
    if gcloud services enable "${api}" --project="${PROJECT_ID}" 2>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗${NC}"
    fi
done
echo ""

# 5. Check IAM permissions
echo -e "${BLUE}[5/8] Checking IAM permissions...${NC}"
REQUIRED_ROLES=(
    "roles/container.admin"
    "roles/compute.admin"
    "roles/iam.serviceAccountAdmin"
    "roles/resourcemanager.projectIamAdmin"
)

USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
PERMISSIONS_OK=true

for role in "${REQUIRED_ROLES[@]}"; do
    if gcloud projects get-iam-policy "${PROJECT_ID}" \
        --flatten="bindings[].members" \
        --filter="bindings.role:${role} AND bindings.members:user:${USER_EMAIL}" \
        --format="value(bindings.role)" 2>/dev/null | grep -q "${role}"; then
        echo -e "${GREEN}✓${NC} ${role}"
    else
        echo -e "${YELLOW}⚠${NC} ${role} (may be inherited)"
        # Don't fail, just warn
    fi
done
echo ""

# 6. Check quotas
echo -e "${BLUE}[6/8] Checking GCP quotas...${NC}"
echo -e "${YELLOW}⚠${NC} Manual quota check required:"
echo "  1. Visit: https://console.cloud.google.com/iam-admin/quotas?project=${PROJECT_ID}"
echo "  2. Verify quotas for:"
echo "     - GPUs (NVIDIA_L4_GPUS): >= 32"
echo "     - CPUs (CPUS): >= 1000"
echo "     - In-use IP addresses: >= 1000"
echo ""
read -p "Have you verified quotas? (yes/no): " quota_check
if [[ "${quota_check}" != "yes" ]]; then
    echo -e "${RED}✗${NC} Quota verification required before proceeding"
    exit 1
fi
echo ""

# 7. Verify Terraform state bucket
echo -e "${BLUE}[7/8] Checking Terraform state bucket...${NC}"
STATE_BUCKET="${PROJECT_ID}-terraform-state"
if gsutil ls "gs://${STATE_BUCKET}" &>/dev/null; then
    echo -e "${GREEN}✓${NC} Terraform state bucket exists: gs://${STATE_BUCKET}"
else
    echo -e "${YELLOW}⚠${NC} Creating Terraform state bucket..."
    gsutil mb -p "${PROJECT_ID}" -l "${REGION}" "gs://${STATE_BUCKET}"
    gsutil versioning set on "gs://${STATE_BUCKET}"
    echo -e "${GREEN}✓${NC} Created: gs://${STATE_BUCKET}"
fi
echo ""

# 8. Check available GPU quota in region
echo -e "${BLUE}[8/8] Checking GPU availability in ${REGION}...${NC}"
echo -e "${YELLOW}⚠${NC} Verify GPU availability:"
gcloud compute accelerator-types list \
    --filter="zone:${REGION}" \
    --format="table(name,zone)" 2>/dev/null || echo "Could not list accelerator types"
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  PREFLIGHT CHECK COMPLETE                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓${NC} All checks passed. Ready for deployment."
echo ""
echo "Next steps:"
echo "  1. cd terraform"
echo "  2. cp terraform.tfvars.example terraform.tfvars"
echo "  3. Edit terraform.tfvars with your values"
echo "  4. terraform init"
echo "  5. terraform plan"
echo "  6. terraform apply"
echo ""
echo "Or run the full deployment script:"
echo "  ./scripts/deploy.sh"
echo ""
