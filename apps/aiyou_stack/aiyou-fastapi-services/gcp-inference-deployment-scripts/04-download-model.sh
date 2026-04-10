#!/bin/bash
# Download models from Hugging Face to Google Cloud Storage
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Model Download Script ===${NC}"

# Check required environment variables
REQUIRED_VARS=("PROJECT_ID" "MODEL_BUCKET")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo -e "${RED}Error: ${var} not set. Run: source .env.gcp-inference${NC}"
        exit 1
    fi
done

# Model selection
if [ -z "${HF_MODEL_ID:-}" ]; then
    echo -e "${YELLOW}Select a model to download:${NC}\n"

    echo -e "${BLUE}LLM Models (vLLM):${NC}"
    echo "  1) google/gemma-3-1b-it"
    echo "  2) google/gemma-3-4b-it"
    echo "  3) google/gemma-3-27b-it (requires L4/H100/H200)"
    echo "  4) meta-llama/Llama-3.3-70B-Instruct (requires H100/H200)"
    echo "  5) meta-llama/Llama-4-Scout-17B-16E-Instruct (requires H100/H200)"
    echo "  6) Qwen/Qwen3-32b"
    echo ""
    echo -e "${BLUE}Diffusion Models:${NC}"
    echo "  7) black-forest-labs/FLUX.1-schnell"
    echo ""
    echo "  8) Custom model ID"
    echo ""

    read -p "Enter choice (1-8): " choice

    case $choice in
        1) HF_MODEL_ID="google/gemma-3-1b-it" ;;
        2) HF_MODEL_ID="google/gemma-3-4b-it" ;;
        3) HF_MODEL_ID="google/gemma-3-27b-it" ;;
        4) HF_MODEL_ID="meta-llama/Llama-3.3-70B-Instruct" ;;
        5) HF_MODEL_ID="meta-llama/Llama-4-Scout-17B-16E-Instruct" ;;
        6) HF_MODEL_ID="Qwen/Qwen3-32b" ;;
        7) HF_MODEL_ID="black-forest-labs/FLUX.1-schnell" ;;
        8)
            read -p "Enter Hugging Face model ID (e.g., org/model-name): " HF_MODEL_ID
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
fi

echo -e "\n${GREEN}Downloading model: ${HF_MODEL_ID}${NC}"

# Generate model hash for job naming
HF_MODEL_ID_HASH=$(echo -n "${HF_MODEL_ID}" | md5sum | cut -d' ' -f1 | cut -c1-8)
HF_MODEL_NAME=$(echo "${HF_MODEL_ID}" | sed 's/.*\///g' | tr '[:upper:]' '[:lower:]' | tr '.' '-')

export HF_MODEL_ID HF_MODEL_ID_HASH HF_MODEL_NAME

echo "  Model ID:   ${HF_MODEL_ID}"
echo "  Model Hash: ${HF_MODEL_ID_HASH}"
echo "  Model Name: ${HF_MODEL_NAME}"
echo "  Bucket:     gs://${MODEL_BUCKET}"

# Create model download job manifest
MANIFEST_DIR="/tmp/model-download-${HF_MODEL_ID_HASH}"
mkdir -p "${MANIFEST_DIR}"

cat > "${MANIFEST_DIR}/kustomization.yaml" << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: model-download

resources:
  - job.yaml

configMapGenerator:
  - name: model-download-config
    literals:
      - MODEL_ID=${HF_MODEL_ID}
      - BUCKET_NAME=${MODEL_BUCKET}
EOF

cat > "${MANIFEST_DIR}/job.yaml" << 'JOBEOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: ${HF_MODEL_ID_HASH}-hf-model-to-gcs
  namespace: model-download
  labels:
    app: model-download
    model: ${HF_MODEL_NAME}
spec:
  backoffLimit: 2
  ttlSecondsAfterFinished: 3600
  template:
    metadata:
      labels:
        app: model-download
        model: ${HF_MODEL_NAME}
    spec:
      serviceAccountName: model-downloader
      restartPolicy: OnFailure
      containers:
      - name: model-downloader
        image: python:3.11-slim
        command: ["/bin/bash", "-c"]
        args:
          - |
            set -euxo pipefail

            echo "=== Installing dependencies ==="
            pip install --no-cache-dir huggingface-hub[cli] google-cloud-storage

            echo "=== Authenticating with Hugging Face ==="
            # Option 1: Use Secret Manager (preferred)
            if command -v gcloud &> /dev/null; then
              HF_TOKEN=$(gcloud secrets versions access latest \
                --secret=huggingface-hub-token \
                --project=${PROJECT_ID} 2>/dev/null || echo "")
            fi

            # Option 2: Use Kubernetes secret (fallback)
            if [ -z "$HF_TOKEN" ] && [ -f /secrets/hf-token/token ]; then
              HF_TOKEN=$(cat /secrets/hf-token/token)
            fi

            if [ -z "$HF_TOKEN" ]; then
              echo "ERROR: No Hugging Face token found"
              exit 1
            fi

            export HF_TOKEN

            echo "=== Downloading model: ${HF_MODEL_ID} ==="
            huggingface-cli download "${HF_MODEL_ID}" \
              --local-dir "/tmp/models/${HF_MODEL_ID}" \
              --local-dir-use-symlinks False

            echo "=== Uploading to GCS: gs://${MODEL_BUCKET}/${HF_MODEL_ID}/ ==="
            pip install --no-cache-dir gcsfs

            python3 << 'PYEOF'
import os
import gcsfs

model_id = "${HF_MODEL_ID}"
bucket = "${MODEL_BUCKET}"
local_dir = f"/tmp/models/{model_id}"
gcs_path = f"gs://{bucket}/{model_id}"

print(f"Uploading from {local_dir} to {gcs_path}")

fs = gcsfs.GCSFileSystem(project="${PROJECT_ID}")

# Upload all files
for root, dirs, files in os.walk(local_dir):
    for file in files:
        local_file = os.path.join(root, file)
        rel_path = os.path.relpath(local_file, local_dir)
        gcs_file = f"{bucket}/{model_id}/{rel_path}"

        print(f"Uploading: {rel_path}")
        fs.put(local_file, gcs_file)

print("Upload complete!")
PYEOF

            echo "=== Model download complete ==="
            gsutil ls -lh "gs://${MODEL_BUCKET}/${HF_MODEL_ID}/"
        env:
        - name: HF_MODEL_ID
          value: "${HF_MODEL_ID}"
        - name: MODEL_BUCKET
          value: "${MODEL_BUCKET}"
        - name: PROJECT_ID
          value: "${PROJECT_ID}"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        volumeMounts:
        - name: hf-token
          mountPath: /secrets/hf-token
          readOnly: true
      volumes:
      - name: hf-token
        secret:
          secretName: huggingface-token
          optional: true
JOBEOF

# Substitute environment variables
envsubst < "${MANIFEST_DIR}/kustomization.yaml" > "${MANIFEST_DIR}/kustomization.yaml.tmp"
mv "${MANIFEST_DIR}/kustomization.yaml.tmp" "${MANIFEST_DIR}/kustomization.yaml"

envsubst < "${MANIFEST_DIR}/job.yaml" > "${MANIFEST_DIR}/job.yaml.tmp"
mv "${MANIFEST_DIR}/job.yaml.tmp" "${MANIFEST_DIR}/job.yaml"

# Deploy the job
echo -e "\n${GREEN}Deploying download job...${NC}"
kubectl apply -k "${MANIFEST_DIR}"

# Wait for job to start
echo -e "${YELLOW}Waiting for job to start...${NC}"
sleep 5

# Watch job progress
JOB_NAME="${HF_MODEL_ID_HASH}-hf-model-to-gcs"

echo -e "\n${GREEN}Monitoring job: ${JOB_NAME}${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop watching (job will continue running)${NC}\n"

# Function to check job status
check_job_status() {
    kubectl get job "${JOB_NAME}" -n model-download \
        -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}' 2>/dev/null
}

# Watch loop
while true; do
    clear
    echo -e "${GREEN}=== Job Status ===${NC}"
    kubectl get job "${JOB_NAME}" -n model-download 2>/dev/null || break

    echo -e "\n${GREEN}=== Job Logs (last 20 lines) ===${NC}"
    kubectl logs -n model-download "job/${JOB_NAME}" \
        --all-containers --tail=20 2>/dev/null || echo "Waiting for pod to start..."

    # Check if complete
    if [ "$(check_job_status)" = "True" ]; then
        echo -e "\n${GREEN}✓ Job completed successfully!${NC}"
        break
    fi

    # Check if failed
    FAILED=$(kubectl get job "${JOB_NAME}" -n model-download \
        -o jsonpath='{.status.conditions[?(@.type=="Failed")].status}' 2>/dev/null)
    if [ "$FAILED" = "True" ]; then
        echo -e "\n${RED}✗ Job failed!${NC}"
        kubectl describe job "${JOB_NAME}" -n model-download
        exit 1
    fi

    sleep 5
done

# Verify model in GCS
echo -e "\n${GREEN}=== Verifying model in Cloud Storage ===${NC}"
gsutil ls -lh "gs://${MODEL_BUCKET}/${HF_MODEL_ID}/" | head -20

# Cleanup job
echo -e "\n${YELLOW}Cleaning up job...${NC}"
kubectl delete job "${JOB_NAME}" -n model-download --ignore-not-found

echo -e "\n${GREEN}Model download complete!${NC}"
echo -e "${YELLOW}Model location: gs://${MODEL_BUCKET}/${HF_MODEL_ID}/${NC}"

# Save model info for next steps
cat > .env.model-info << MODELEOF
# Model Download Info
# Generated: $(date)
export HF_MODEL_ID="${HF_MODEL_ID}"
export HF_MODEL_NAME="${HF_MODEL_NAME}"
export HF_MODEL_ID_HASH="${HF_MODEL_ID_HASH}"
export MODEL_GCS_PATH="gs://${MODEL_BUCKET}/${HF_MODEL_ID}"
MODELEOF

echo -e "${GREEN}Model info saved to: .env.model-info${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Source model info: source .env.model-info"
echo -e "  2. Deploy inference: ./05-deploy-vllm-inference.sh"
