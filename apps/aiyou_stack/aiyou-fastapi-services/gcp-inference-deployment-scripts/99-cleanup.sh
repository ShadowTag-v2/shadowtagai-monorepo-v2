#!/bin/bash
# Cleanup GKE inference deployment
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}=== GKE Inference Cleanup ===${NC}"

# Parse options
FULL_CLEANUP=${1:-"workload"}  # Options: workload, all

cat << 'EOF'

This script will clean up GKE inference resources.

Options:
  workload - Delete only the inference workload (default)
  all      - Delete everything (cluster, buckets, service accounts)

EOF

if [ "$FULL_CLEANUP" = "all" ]; then
    echo -e "${RED}WARNING: This will delete ALL resources including:${NC}"
    echo "  - GKE Cluster"
    echo "  - Cloud Storage buckets"
    echo "  - Service Accounts"
    echo "  - Downloaded models"
    echo ""
    read -p "Are you sure? Type 'DELETE ALL' to confirm: " confirm

    if [ "$confirm" != "DELETE ALL" ]; then
        echo -e "${YELLOW}Cleanup cancelled${NC}"
        exit 0
    fi
fi

# Check environment
if [ -z "${PROJECT_ID:-}" ]; then
    echo -e "${YELLOW}Loading environment from .env.gcp-inference...${NC}"
    if [ -f ".env.gcp-inference" ]; then
        source .env.gcp-inference
    else
        echo -e "${RED}Error: .env.gcp-inference not found${NC}"
        exit 1
    fi
fi

# Load model info if available
if [ -f ".env.model-info" ]; then
    source .env.model-info
fi

echo -e "${GREEN}Project: ${PROJECT_ID}${NC}"

# Delete inference workloads
if [ -n "${HF_MODEL_NAME:-}" ] && [ -n "${ACCELERATOR_TYPE:-}" ]; then
    DEPLOYMENT_NAME="vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}"

    echo -e "\n${YELLOW}=== Deleting Inference Workload ===${NC}"

    if kubectl get deployment "${DEPLOYMENT_NAME}" -n inference-online-gpu &>/dev/null; then
        echo -e "${YELLOW}Deleting deployment: ${DEPLOYMENT_NAME}${NC}"
        kubectl delete deployment "${DEPLOYMENT_NAME}" -n inference-online-gpu --ignore-not-found
    fi

    if kubectl get service "${DEPLOYMENT_NAME}" -n inference-online-gpu &>/dev/null; then
        echo -e "${YELLOW}Deleting service: ${DEPLOYMENT_NAME}${NC}"
        kubectl delete service "${DEPLOYMENT_NAME}" -n inference-online-gpu --ignore-not-found
    fi

    if kubectl get hpa "${DEPLOYMENT_NAME}" -n inference-online-gpu &>/dev/null; then
        echo -e "${YELLOW}Deleting HPA: ${DEPLOYMENT_NAME}${NC}"
        kubectl delete hpa "${DEPLOYMENT_NAME}" -n inference-online-gpu --ignore-not-found
    fi

    echo -e "${GREEN}✓ Workload deleted${NC}"
else
    echo -e "${YELLOW}No specific workload configured, skipping workload deletion${NC}"
fi

# Delete all workloads in namespace
echo -e "\n${YELLOW}Checking for other workloads...${NC}"
kubectl delete deployment,service,hpa --all -n inference-online-gpu --ignore-not-found

if [ "$FULL_CLEANUP" = "all" ]; then
    # Delete namespaces
    echo -e "\n${YELLOW}=== Deleting Namespaces ===${NC}"
    NAMESPACES=("model-download" "inference-online-gpu" "inference-online-tpu" "inference-batch")

    for ns in "${NAMESPACES[@]}"; do
        if kubectl get namespace "$ns" &>/dev/null; then
            echo -e "${YELLOW}Deleting namespace: ${ns}${NC}"
            kubectl delete namespace "$ns" --ignore-not-found
        fi
    done

    # Delete GKE cluster
    if [ -n "${CLUSTER_NAME:-}" ] && [ -n "${REGION:-}" ]; then
        echo -e "\n${YELLOW}=== Deleting GKE Cluster ===${NC}"

        if gcloud container clusters describe "${CLUSTER_NAME}" \
            --region="${REGION}" \
            --project="${PROJECT_ID}" &>/dev/null; then

            echo -e "${RED}Deleting cluster: ${CLUSTER_NAME}${NC}"
            echo -e "${YELLOW}This will take 5-10 minutes...${NC}"

            gcloud container clusters delete "${CLUSTER_NAME}" \
                --region="${REGION}" \
                --project="${PROJECT_ID}" \
                --quiet

            echo -e "${GREEN}✓ Cluster deleted${NC}"
        else
            echo -e "${YELLOW}Cluster not found: ${CLUSTER_NAME}${NC}"
        fi
    fi

    # Delete Cloud Storage bucket
    if [ -n "${MODEL_BUCKET:-}" ]; then
        echo -e "\n${YELLOW}=== Deleting Cloud Storage Bucket ===${NC}"

        if gsutil ls -b "gs://${MODEL_BUCKET}" &>/dev/null; then
            echo -e "${RED}Deleting bucket: ${MODEL_BUCKET}${NC}"
            echo -e "${YELLOW}This will delete all downloaded models!${NC}"

            read -p "Confirm deletion of bucket ${MODEL_BUCKET}? (yes/no): " confirm_bucket
            if [ "$confirm_bucket" = "yes" ]; then
                gsutil -m rm -r "gs://${MODEL_BUCKET}"
                echo -e "${GREEN}✓ Bucket deleted${NC}"
            else
                echo -e "${YELLOW}Bucket deletion skipped${NC}"
            fi
        else
            echo -e "${YELLOW}Bucket not found: ${MODEL_BUCKET}${NC}"
        fi
    fi

    # Delete service accounts
    echo -e "\n${YELLOW}=== Deleting Service Accounts ===${NC}"

    SERVICE_ACCOUNTS=(
        "gke-inference-sa@${PROJECT_ID}.iam.gserviceaccount.com"
        "model-downloader@${PROJECT_ID}.iam.gserviceaccount.com"
    )

    for sa in "${SERVICE_ACCOUNTS[@]}"; do
        if gcloud iam service-accounts describe "$sa" --project="${PROJECT_ID}" &>/dev/null; then
            echo -e "${YELLOW}Deleting service account: ${sa}${NC}"
            gcloud iam service-accounts delete "$sa" \
                --project="${PROJECT_ID}" \
                --quiet
        fi
    done

    # Delete secrets
    echo -e "\n${YELLOW}=== Deleting Secrets ===${NC}"

    if gcloud secrets describe "huggingface-hub-token" --project="${PROJECT_ID}" &>/dev/null; then
        echo -e "${YELLOW}Deleting secret: huggingface-hub-token${NC}"
        gcloud secrets delete "huggingface-hub-token" \
            --project="${PROJECT_ID}" \
            --quiet
    fi

    # Clean local files
    echo -e "\n${YELLOW}=== Cleaning Local Files ===${NC}"

    if [ -f ".env.gcp-inference" ]; then
        echo -e "${YELLOW}Removing .env.gcp-inference${NC}"
        rm -f .env.gcp-inference
    fi

    if [ -f ".env.model-info" ]; then
        echo -e "${YELLOW}Removing .env.model-info${NC}"
        rm -f .env.model-info
    fi

    echo -e "${GREEN}✓ All resources deleted${NC}"

else
    echo -e "\n${YELLOW}Workload cleanup complete${NC}"
    echo -e "${YELLOW}To delete all resources (cluster, buckets, etc.), run:${NC}"
    echo -e "${YELLOW}  ./99-cleanup.sh all${NC}"
fi

echo -e "\n${GREEN}=== Cleanup Summary ===${NC}"

if [ "$FULL_CLEANUP" = "all" ]; then
    cat << EOF
✓ Inference workloads deleted
✓ Namespaces deleted
✓ GKE cluster deleted
✓ Cloud Storage bucket deleted (if confirmed)
✓ Service accounts deleted
✓ Secrets deleted
✓ Local configuration files removed

All GKE inference resources have been cleaned up.
EOF
else
    cat << EOF
✓ Inference workloads deleted
✓ Namespaces preserved
✓ GKE cluster preserved
✓ Cloud Storage bucket preserved
✓ Service accounts preserved

To delete all resources, run: ./99-cleanup.sh all
EOF
fi

echo -e "\n${GREEN}Cleanup complete!${NC}"
