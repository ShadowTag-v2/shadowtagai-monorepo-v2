#!/bin/bash
#==============================================================================
# PNKLN Multi-Agent Deployment Script
# Target: Vertex AI Workbench (GCP)
# Integration: rust_scriptbots/Bevy Engine
# Governance: ShadowTag-v2JR Framework
#==============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_REGION="${DEPLOYMENT_REGION:-us-central1}"
WORKBENCH_INSTANCE_NAME="${WORKBENCH_INSTANCE_NAME:-pnkln-agents-workbench}"
MACHINE_TYPE="${MACHINE_TYPE:-n1-standard-4}"
BOOT_DISK_SIZE="${BOOT_DISK_SIZE:-100GB}"
AGENT_BUCKET_NAME="${AGENT_BUCKET_NAME:-${GCP_PROJECT_ID}-pnkln-agents}"

#==============================================================================
# Helper Functions
#==============================================================================

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

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    # Check if GCP_PROJECT_ID is set
    if [ -z "${GCP_PROJECT_ID:-}" ]; then
        log_error "GCP_PROJECT_ID environment variable not set"
        echo "Usage: export GCP_PROJECT_ID=\"your-project-id\""
        exit 1
    fi

    # Set project
    gcloud config set project "$GCP_PROJECT_ID" --quiet

    log_success "Prerequisites check passed"
}

enable_apis() {
    log_info "Enabling required GCP APIs..."

    local apis=(
        "notebooks.googleapis.com"
        "compute.googleapis.com"
        "storage.googleapis.com"
        "cloudbuild.googleapis.com"
        "aiplatform.googleapis.com"
    )

    for api in "${apis[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable "$api" --project="$GCP_PROJECT_ID" --quiet
    done

    log_success "All APIs enabled"
}

create_gcs_bucket() {
    log_info "Creating GCS bucket for Agent Mail..."

    # Check if bucket exists
    if gsutil ls -b "gs://${AGENT_BUCKET_NAME}" &> /dev/null; then
        log_warning "Bucket gs://${AGENT_BUCKET_NAME} already exists, skipping..."
    else
        gsutil mb -p "$GCP_PROJECT_ID" -l "$DEPLOYMENT_REGION" "gs://${AGENT_BUCKET_NAME}"
        log_success "Created bucket: gs://${AGENT_BUCKET_NAME}"
    fi

    # Create subdirectories
    log_info "Setting up Agent Mail directory structure..."
    echo "" | gsutil cp - "gs://${AGENT_BUCKET_NAME}/agent-mail/.keep"
    echo "" | gsutil cp - "gs://${AGENT_BUCKET_NAME}/checkpoints/.keep"
    echo "" | gsutil cp - "gs://${AGENT_BUCKET_NAME}/coverage-reports/.keep"

    log_success "Agent Mail bucket configured"
}

deploy_workbench_instance() {
    log_info "Deploying Vertex AI Workbench instance..."

    # Check if instance exists
    if gcloud notebooks instances describe "$WORKBENCH_INSTANCE_NAME" \
        --location="$DEPLOYMENT_REGION" \
        --project="$GCP_PROJECT_ID" &> /dev/null; then
        log_warning "Workbench instance '$WORKBENCH_INSTANCE_NAME' already exists"
        log_info "To redeploy, first delete: gcloud notebooks instances delete $WORKBENCH_INSTANCE_NAME --location=$DEPLOYMENT_REGION"
        return 0
    fi

    log_info "Creating new Workbench instance (this may take 5-10 minutes)..."

    gcloud notebooks instances create "$WORKBENCH_INSTANCE_NAME" \
        --location="$DEPLOYMENT_REGION" \
        --machine-type="$MACHINE_TYPE" \
        --vm-image-project=deeplearning-platform-release \
        --vm-image-family=common-cpu \
        --boot-disk-size="$BOOT_DISK_SIZE" \
        --boot-disk-type=PD_STANDARD \
        --metadata="proxy-mode=service_account,startup-script=#!/bin/bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source \$HOME/.cargo/env

# Install Bevy dependencies
apt-get update
apt-get install -y pkg-config libx11-dev libasound2-dev libudev-dev

# Clone rust_scriptbots (optional - can be done manually)
# git clone https://github.com/YOUR_ORG/rust_scriptbots.git /home/jupyter/rust_scriptbots

# Install Python dependencies
pip install --upgrade pip
pip install claude-agent-sdk anthropic google-cloud-storage

echo 'Startup script completed' > /tmp/startup-complete.txt
" \
        --project="$GCP_PROJECT_ID" \
        --quiet || {
            log_error "Failed to create Workbench instance"
            exit 1
        }

    log_success "Workbench instance '$WORKBENCH_INSTANCE_NAME' created"
}

upload_artifacts() {
    log_info "Uploading deployment artifacts to GCS..."

    # Upload notebook and documentation
    local artifacts=(
        "COR_MULTI_AGENT_TEMPLATE.ipynb"
        "PREFLIGHT_CHECKLIST.md"
        "QUICKSTART.md"
        "AGENTS.md"
        "ShadowTag-v2JR_DOCTRINE.md"
        "PLAN_TO_INTEGRATE_BEVY_ENGINE.md"
    )

    for artifact in "${artifacts[@]}"; do
        if [ -f "$SCRIPT_DIR/$artifact" ]; then
            gsutil cp "$SCRIPT_DIR/$artifact" "gs://${AGENT_BUCKET_NAME}/setup/"
            log_info "Uploaded $artifact"
        else
            log_warning "Artifact $artifact not found, skipping..."
        fi
    done

    log_success "Artifacts uploaded to gs://${AGENT_BUCKET_NAME}/setup/"
}

generate_agent_documentation() {
    log_info "Generating agent documentation..."

    # These files should already exist, but verify
    local required_docs=(
        "AGENTS.md"
        "ShadowTag-v2JR_DOCTRINE.md"
        "PLAN_TO_INTEGRATE_BEVY_ENGINE.md"
    )

    for doc in "${required_docs[@]}"; do
        if [ ! -f "$SCRIPT_DIR/$doc" ]; then
            log_warning "$doc not found - should be auto-generated"
        fi
    done
}

print_access_instructions() {
    log_success "==================================================================="
    log_success "Deployment Complete!"
    log_success "==================================================================="
    echo ""
    log_info "Next Steps:"
    echo ""
    echo "1. Access Workbench:"
    echo "   gcloud notebooks instances describe $WORKBENCH_INSTANCE_NAME \\"
    echo "     --location=$DEPLOYMENT_REGION \\"
    echo "     --format='value(proxyUri)'"
    echo ""
    echo "2. Or open directly:"
    echo "   https://console.cloud.google.com/vertex-ai/workbench/instances?project=$GCP_PROJECT_ID"
    echo ""
    echo "3. Download artifacts from GCS:"
    echo "   gsutil -m cp -r gs://${AGENT_BUCKET_NAME}/setup/ ~/workbench-setup/"
    echo ""
    echo "4. Open COR_MULTI_AGENT_TEMPLATE.ipynb in JupyterLab"
    echo ""
    echo "5. Clone rust_scriptbots repository:"
    echo "   git clone <rust_scriptbots_repo_url>"
    echo ""
    echo "6. Edit notebook Cell 2 - Set PROJECT_ID to: $GCP_PROJECT_ID"
    echo ""
    echo "7. Run All Cells to activate agents"
    echo ""
    log_success "==================================================================="
    echo ""
    log_info "Resource Details:"
    echo "  - Project ID: $GCP_PROJECT_ID"
    echo "  - Region: $DEPLOYMENT_REGION"
    echo "  - Workbench Instance: $WORKBENCH_INSTANCE_NAME"
    echo "  - Agent Mail Bucket: gs://${AGENT_BUCKET_NAME}"
    echo "  - Machine Type: $MACHINE_TYPE"
    echo ""
}

#==============================================================================
# Main Execution
#==============================================================================

main() {
    log_info "Starting PNKLN Multi-Agent Deployment..."
    log_info "Target Project: ${GCP_PROJECT_ID:-NOT_SET}"
    echo ""

    check_prerequisites
    enable_apis
    create_gcs_bucket
    deploy_workbench_instance
    upload_artifacts
    generate_agent_documentation
    print_access_instructions

    log_success "Deployment pipeline completed successfully!"
}

# Run main function
main "$@"
