#!/bin/bash
# GKE Inference Deployment - Environment Setup
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch
# Generated: 2025-11-08

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== GKE Inference Environment Setup ===${NC}"

# Required environment variables
cat << 'EOF'
This script sets up the environment for deploying AI inference workloads on GKE.

Prerequisites:
1. Google Cloud Project with billing enabled
2. Sufficient GPU/TPU quota in target region
3. gcloud CLI installed and authenticated
4. kubectl installed
5. terraform >= 1.0 installed
6. Hugging Face account with model access

EOF

# Parse command-line arguments
EXPORT_MODE=${1:-"prompt"}  # Options: prompt, export, check

# Function to prompt for variable
prompt_var() {
    local var_name=$1
    local var_description=$2
    local default_value=${3:-""}

    if [ -n "$default_value" ]; then
        read -p "Enter $var_description [$default_value]: " value
        value=${value:-$default_value}
    else
        read -p "Enter $var_description: " value
    fi

    echo "$value"
}

# Check mode - verify all required variables are set
if [ "$EXPORT_MODE" = "check" ]; then
    echo -e "${YELLOW}Checking environment variables...${NC}"
    MISSING_VARS=()

    [ -z "${PROJECT_ID:-}" ] && MISSING_VARS+=("PROJECT_ID")
    [ -z "${REGION:-}" ] && MISSING_VARS+=("REGION")
    [ -z "${CLUSTER_NAME:-}" ] && MISSING_VARS+=("CLUSTER_NAME")
    [ -z "${HF_TOKEN:-}" ] && MISSING_VARS+=("HF_TOKEN")

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo -e "${RED}Missing required variables: ${MISSING_VARS[*]}${NC}"
        exit 1
    else
        echo -e "${GREEN}All required variables are set!${NC}"
        exit 0
    fi
fi

# Prompt mode - interactive setup
if [ "$EXPORT_MODE" = "prompt" ]; then
    echo -e "${YELLOW}=== Interactive Environment Setup ===${NC}"

    # GCP Project Configuration
    echo -e "\n${GREEN}1. GCP Project Configuration${NC}"
    PROJECT_ID=$(prompt_var "PROJECT_ID" "GCP Project ID" "${PROJECT_ID:-}")
    REGION=$(prompt_var "REGION" "GCP Region (e.g., us-central1)" "${REGION:-us-central1}")
    ZONE=$(prompt_var "ZONE" "GCP Zone (e.g., us-central1-a)" "${ZONE:-${REGION}-a}")

    # GKE Cluster Configuration
    echo -e "\n${GREEN}2. GKE Cluster Configuration${NC}"
    CLUSTER_NAME=$(prompt_var "CLUSTER_NAME" "GKE Cluster Name" "${CLUSTER_NAME:-gke-inference-cluster}")
    CLUSTER_MODE=$(prompt_var "CLUSTER_MODE" "Cluster Mode (autopilot/standard)" "${CLUSTER_MODE:-autopilot}")

    # Model Configuration
    echo -e "\n${GREEN}3. Model Configuration${NC}"
    HF_TOKEN=$(prompt_var "HF_TOKEN" "Hugging Face Access Token" "${HF_TOKEN:-}")

    # Storage Configuration
    echo -e "\n${GREEN}4. Storage Configuration${NC}"
    MODEL_BUCKET=$(prompt_var "MODEL_BUCKET" "GCS Bucket for Models" "${MODEL_BUCKET:-${PROJECT_ID}-inference-models}")

    # Network Configuration
    echo -e "\n${GREEN}5. Network Configuration${NC}"
    NETWORK_NAME=$(prompt_var "NETWORK_NAME" "VPC Network Name" "${NETWORK_NAME:-default}")
    SUBNET_NAME=$(prompt_var "SUBNET_NAME" "Subnet Name" "${SUBNET_NAME:-default}")

    # Save to .env file
    ENV_FILE=".env.gcp-inference"
    echo -e "\n${YELLOW}Saving configuration to ${ENV_FILE}...${NC}"

    cat > "$ENV_FILE" << ENVEOF
# GKE Inference Deployment Configuration
# Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

# GCP Project Configuration
export PROJECT_ID="${PROJECT_ID}"
export REGION="${REGION}"
export ZONE="${ZONE}"

# GKE Cluster Configuration
export CLUSTER_NAME="${CLUSTER_NAME}"
export CLUSTER_MODE="${CLUSTER_MODE}"

# Model Configuration
export HF_TOKEN="${HF_TOKEN}"

# Storage Configuration
export MODEL_BUCKET="${MODEL_BUCKET}"

# Network Configuration
export NETWORK_NAME="${NETWORK_NAME}"
export SUBNET_NAME="${SUBNET_NAME}"

# Derived Variables
export ACP_REPO_DIR="/home/user/gcp-inference-repos/accelerated-platforms"
export KUBECONFIG="\${HOME}/.kube/config"

# Kubernetes Namespaces
export huggingface_hub_downloader_kubernetes_namespace_name="model-download"
export ira_online_gpu_kubernetes_namespace_name="inference-online-gpu"
export ira_online_tpu_kubernetes_namespace_name="inference-online-tpu"

# Google Cloud Services
export GCS_FUSE_ENABLED="true"
export MANAGED_PROMETHEUS_ENABLED="true"

# Accelerator Configuration (set per deployment)
# export ACCELERATOR_TYPE="l4"  # Options: l4, h100, h200
# export HF_MODEL_ID="google/gemma-3-27b-it"
ENVEOF

    echo -e "${GREEN}Configuration saved to ${ENV_FILE}${NC}"
    echo -e "${YELLOW}To load this configuration, run: source ${ENV_FILE}${NC}"

    # Verify gcloud configuration
    echo -e "\n${GREEN}6. Verifying gcloud configuration...${NC}"
    gcloud config set project "${PROJECT_ID}" 2>/dev/null || true

    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
        echo -e "${RED}Warning: gcloud project mismatch. Setting to ${PROJECT_ID}${NC}"
        gcloud config set project "${PROJECT_ID}"
    fi

    echo -e "${GREEN}Current gcloud project: $(gcloud config get-value project)${NC}"

fi

# Export mode - source the .env file
if [ "$EXPORT_MODE" = "export" ]; then
    ENV_FILE=".env.gcp-inference"
    if [ -f "$ENV_FILE" ]; then
        echo -e "${GREEN}Loading configuration from ${ENV_FILE}...${NC}"
        source "$ENV_FILE"
        echo -e "${GREEN}Environment variables loaded!${NC}"
    else
        echo -e "${RED}Error: ${ENV_FILE} not found. Run with 'prompt' mode first.${NC}"
        exit 1
    fi
fi

# Display current configuration
echo -e "\n${GREEN}=== Current Configuration ===${NC}"
cat << EOF
PROJECT_ID:     ${PROJECT_ID:-<not set>}
REGION:         ${REGION:-<not set>}
ZONE:           ${ZONE:-<not set>}
CLUSTER_NAME:   ${CLUSTER_NAME:-<not set>}
CLUSTER_MODE:   ${CLUSTER_MODE:-<not set>}
MODEL_BUCKET:   ${MODEL_BUCKET:-<not set>}
HF_TOKEN:       ${HF_TOKEN:+<set>}${HF_TOKEN:-<not set>}
EOF

echo -e "\n${GREEN}Environment setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Review and customize .env.gcp-inference file"
echo -e "  2. Run: source .env.gcp-inference"
echo -e "  3. Run: ./01-enable-gcp-services.sh"
