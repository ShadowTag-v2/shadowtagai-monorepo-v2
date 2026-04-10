#!/bin/bash
# Setup GKE infrastructure for inference workloads
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Setting Up GKE Infrastructure ===${NC}"

# Check required environment variables
REQUIRED_VARS=("PROJECT_ID" "REGION" "CLUSTER_NAME")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo -e "${RED}Error: ${var} not set. Run: source .env.gcp-inference${NC}"
        exit 1
    fi
done

# Set defaults
CLUSTER_MODE=${CLUSTER_MODE:-autopilot}
ZONE=${ZONE:-${REGION}-a}
MODEL_BUCKET=${MODEL_BUCKET:-${PROJECT_ID}-inference-models}

echo -e "${YELLOW}Configuration:${NC}"
echo "  Project:      ${PROJECT_ID}"
echo "  Region:       ${REGION}"
echo "  Zone:         ${ZONE}"
echo "  Cluster:      ${CLUSTER_NAME}"
echo "  Mode:         ${CLUSTER_MODE}"
echo "  Model Bucket: ${MODEL_BUCKET}"

# Create GCS bucket for models
echo -e "\n${GREEN}=== Creating Cloud Storage Bucket ===${NC}"

if gsutil ls -b "gs://${MODEL_BUCKET}" &>/dev/null; then
    echo -e "${YELLOW}Bucket already exists: ${MODEL_BUCKET}${NC}"
else
    echo -e "${GREEN}Creating bucket: ${MODEL_BUCKET}${NC}"
    gsutil mb -p "${PROJECT_ID}" -l "${REGION}" -b on "gs://${MODEL_BUCKET}"

    # Enable versioning
    gsutil versioning set on "gs://${MODEL_BUCKET}"

    # Set lifecycle to delete old versions after 30 days
    cat > /tmp/lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 3,
          "daysSinceNoncurrentTime": 30
        }
      }
    ]
  }
}
EOF
    gsutil lifecycle set /tmp/lifecycle.json "gs://${MODEL_BUCKET}"
    rm /tmp/lifecycle.json
fi

# Create GKE cluster
echo -e "\n${GREEN}=== Creating GKE Cluster ===${NC}"

if gcloud container clusters describe "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Cluster already exists: ${CLUSTER_NAME}${NC}"
    echo -e "${YELLOW}Fetching credentials...${NC}"
    gcloud container clusters get-credentials "${CLUSTER_NAME}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}"
else
    if [ "$CLUSTER_MODE" = "autopilot" ]; then
        echo -e "${GREEN}Creating Autopilot cluster (recommended)...${NC}"
        echo -e "${YELLOW}This will take 5-10 minutes...${NC}"

        gcloud container clusters create-auto "${CLUSTER_NAME}" \
            --region="${REGION}" \
            --project="${PROJECT_ID}" \
            --release-channel=rapid \
            --enable-autoscaling \
            --enable-autorepair \
            --enable-autoupgrade \
            --enable-managed-prometheus \
            --enable-cloud-logging \
            --enable-cloud-monitoring \
            --workload-pool="${PROJECT_ID}.svc.id.goog" \
            --async

        echo -e "${YELLOW}Waiting for cluster creation...${NC}"
        gcloud container operations wait \
            --region="${REGION}" \
            --project="${PROJECT_ID}" \
            $(gcloud container operations list \
                --region="${REGION}" \
                --project="${PROJECT_ID}" \
                --filter="name:operation-*" \
                --format="value(name)" | head -1)

    else
        echo -e "${GREEN}Creating Standard cluster...${NC}"
        echo -e "${YELLOW}This will take 5-10 minutes...${NC}"

        # Get service account email
        GKE_SA_EMAIL="gke-inference-sa@${PROJECT_ID}.iam.gserviceaccount.com"

        gcloud container clusters create "${CLUSTER_NAME}" \
            --region="${REGION}" \
            --project="${PROJECT_ID}" \
            --release-channel=rapid \
            --enable-autoscaling \
            --min-nodes=1 \
            --max-nodes=10 \
            --enable-autorepair \
            --enable-autoupgrade \
            --enable-ip-alias \
            --enable-managed-prometheus \
            --enable-cloud-logging \
            --enable-cloud-monitoring \
            --workload-pool="${PROJECT_ID}.svc.id.goog" \
            --addons=GcsFuseCsiDriver \
            --machine-type=n1-standard-4 \
            --service-account="${GKE_SA_EMAIL}" \
            --async

        echo -e "${YELLOW}Waiting for cluster creation...${NC}"
        gcloud container operations wait \
            --region="${REGION}" \
            --project="${PROJECT_ID}" \
            $(gcloud container operations list \
                --region="${REGION}" \
                --project="${PROJECT_ID}" \
                --filter="name:operation-*" \
                --format="value(name)" | head -1)
    fi

    # Get cluster credentials
    echo -e "${GREEN}Fetching cluster credentials...${NC}"
    gcloud container clusters get-credentials "${CLUSTER_NAME}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}"
fi

# Verify cluster access
echo -e "\n${GREEN}=== Verifying Cluster Access ===${NC}"
kubectl cluster-info
kubectl get nodes

# Create namespaces
echo -e "\n${GREEN}=== Creating Kubernetes Namespaces ===${NC}"

NAMESPACES=(
    "model-download:Model download jobs"
    "inference-online-gpu:Online GPU inference workloads"
    "inference-online-tpu:Online TPU inference workloads"
    "inference-batch:Batch inference workloads"
)

for ns_entry in "${NAMESPACES[@]}"; do
    IFS=':' read -r ns_name ns_desc <<< "$ns_entry"

    if kubectl get namespace "$ns_name" &>/dev/null; then
        echo -e "${YELLOW}Namespace already exists: ${ns_name}${NC}"
    else
        echo -e "${GREEN}Creating namespace: ${ns_name} (${ns_desc})${NC}"
        kubectl create namespace "$ns_name"
        kubectl label namespace "$ns_name" \
            purpose=inference \
            managed-by=gke-inference-deployment
    fi
done

# Setup Workload Identity for model downloads
echo -e "\n${GREEN}=== Configuring Workload Identity ===${NC}"

MODEL_DOWNLOAD_KSA="model-downloader"
MODEL_DOWNLOAD_GSA="model-downloader@${PROJECT_ID}.iam.gserviceaccount.com"

# Create Google Service Account
if gcloud iam service-accounts describe "${MODEL_DOWNLOAD_GSA}" \
    --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}Service account already exists: ${MODEL_DOWNLOAD_GSA}${NC}"
else
    echo -e "${GREEN}Creating service account: ${MODEL_DOWNLOAD_GSA}${NC}"
    gcloud iam service-accounts create "model-downloader" \
        --display-name="Model Downloader Service Account" \
        --project="${PROJECT_ID}"
fi

# Grant storage permissions
echo -e "${GREEN}Granting storage permissions...${NC}"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${MODEL_DOWNLOAD_GSA}" \
    --role="roles/storage.objectAdmin" \
    --condition=None

# Create Kubernetes Service Account
kubectl create serviceaccount "${MODEL_DOWNLOAD_KSA}" \
    -n model-download \
    --dry-run=client -o yaml | kubectl apply -f -

# Bind KSA to GSA
kubectl annotate serviceaccount "${MODEL_DOWNLOAD_KSA}" \
    -n model-download \
    iam.gke.io/gcp-service-account="${MODEL_DOWNLOAD_GSA}" \
    --overwrite

# Allow KSA to impersonate GSA
gcloud iam service-accounts add-iam-policy-binding "${MODEL_DOWNLOAD_GSA}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:${PROJECT_ID}.svc.id.goog[model-download/${MODEL_DOWNLOAD_KSA}]" \
    --project="${PROJECT_ID}"

echo -e "\n${GREEN}Infrastructure setup complete!${NC}"
echo -e "${YELLOW}Cluster info:${NC}"
kubectl cluster-info

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Configure Hugging Face credentials: ./03-setup-huggingface.sh"
echo -e "  2. Download a model: ./04-download-model.sh"
echo -e "  3. Deploy inference workload: ./05-deploy-vllm-inference.sh"
