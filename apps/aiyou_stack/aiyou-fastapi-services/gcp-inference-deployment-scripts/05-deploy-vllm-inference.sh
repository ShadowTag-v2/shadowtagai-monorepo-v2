#!/bin/bash
# Deploy vLLM inference workload on GKE
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Deploy vLLM Inference Workload ===${NC}"

# Check required environment variables
REQUIRED_VARS=("PROJECT_ID" "MODEL_BUCKET" "HF_MODEL_ID" "HF_MODEL_NAME")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo -e "${RED}Error: ${var} not set.${NC}"
        echo -e "${YELLOW}Run: source .env.gcp-inference && source .env.model-info${NC}"
        exit 1
    fi
done

# Select accelerator type
if [ -z "${ACCELERATOR_TYPE:-}" ]; then
    echo -e "${YELLOW}Select GPU accelerator type:${NC}\n"

    # Model compatibility matrix
    echo -e "${BLUE}Model: ${HF_MODEL_NAME}${NC}\n"

    echo "  1) NVIDIA L4 (g2-standard-96, 8 GPUs)"
    echo "     - Cost-effective for smaller models"
    echo "     - Compatible: gemma-3-1b/4b/27b, gpt-oss-20b, qwen3-32b"
    echo ""
    echo "  2) NVIDIA H100 (a3-highgpu-1g, scalable)"
    echo "     - High performance for all models"
    echo "     - Compatible: all models"
    echo ""
    echo "  3) NVIDIA H200 (a3-ultragpu-8g)"
    echo "     - Maximum memory for largest models"
    echo "     - Compatible: all models, best for 70B+"
    echo ""

    read -p "Enter choice (1-3): " accel_choice

    case $accel_choice in
        1) ACCELERATOR_TYPE="l4" ;;
        2) ACCELERATOR_TYPE="h100" ;;
        3) ACCELERATOR_TYPE="h200" ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
fi

export ACCELERATOR_TYPE

# Set GPU count and machine type based on accelerator and model
case "${ACCELERATOR_TYPE}" in
    "l4")
        MACHINE_TYPE="g2-standard-96"
        GPU_COUNT="8"
        GPU_TYPE="nvidia-l4"
        ;;
    "h100")
        # Determine GPU count based on model size
        if [[ "${HF_MODEL_NAME}" == *"70b"* ]]; then
            MACHINE_TYPE="a3-highgpu-4g"
            GPU_COUNT="4"
        elif [[ "${HF_MODEL_NAME}" == *"scout"* ]] || [[ "${HF_MODEL_NAME}" == *"16e"* ]]; then
            MACHINE_TYPE="a3-highgpu-8g"
            GPU_COUNT="8"
        else
            MACHINE_TYPE="a3-highgpu-1g"
            GPU_COUNT="1"
        fi
        GPU_TYPE="nvidia-h100-80gb"
        ;;
    "h200")
        MACHINE_TYPE="a3-ultragpu-8g"
        if [[ "${HF_MODEL_NAME}" == *"70b"* ]]; then
            GPU_COUNT="4"
        elif [[ "${HF_MODEL_NAME}" == *"scout"* ]] || [[ "${HF_MODEL_NAME}" == *"16e"* ]]; then
            GPU_COUNT="8"
        else
            GPU_COUNT="1"
        fi
        GPU_TYPE="nvidia-h200-141gb"
        ;;
esac

echo -e "\n${GREEN}Configuration:${NC}"
echo "  Model:        ${HF_MODEL_ID}"
echo "  Model Name:   ${HF_MODEL_NAME}"
echo "  Accelerator:  ${ACCELERATOR_TYPE}"
echo "  Machine Type: ${MACHINE_TYPE}"
echo "  GPU Count:    ${GPU_COUNT}"
echo "  GPU Type:     ${GPU_TYPE}"

# Create deployment manifests
MANIFEST_DIR="/tmp/vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}"
mkdir -p "${MANIFEST_DIR}"

# Create kustomization
cat > "${MANIFEST_DIR}/kustomization.yaml" << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: inference-online-gpu

resources:
  - deployment.yaml
  - service.yaml
  - hpa.yaml

configMapGenerator:
  - name: vllm-config
    literals:
      - MODEL_ID=${HF_MODEL_ID}
      - ACCELERATOR_TYPE=${ACCELERATOR_TYPE}
EOF

# Create deployment
cat > "${MANIFEST_DIR}/deployment.yaml" << 'DEPEOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}
  namespace: inference-online-gpu
  labels:
    app: vllm
    model: ${HF_MODEL_NAME}
    accelerator: ${ACCELERATOR_TYPE}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm
      model: ${HF_MODEL_NAME}
      accelerator: ${ACCELERATOR_TYPE}
  template:
    metadata:
      labels:
        app: vllm
        model: ${HF_MODEL_NAME}
        accelerator: ${ACCELERATOR_TYPE}
    spec:
      terminationGracePeriodSeconds: 120
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        command: ["python3", "-m", "vllm.entrypoints.openai.api_server"]
        args:
          - --model=/gcs/${HF_MODEL_ID}
          - --served-model-name=${HF_MODEL_ID}
          - --port=8000
          - --host=0.0.0.0
          - --tensor-parallel-size=${GPU_COUNT}
          - --max-model-len=4096
          - --trust-remote-code
          - --enable-auto-tool-choice
          - --tool-call-parser=hermes
        env:
        - name: HF_HOME
          value: /tmp/hf_home
        - name: TRANSFORMERS_CACHE
          value: /tmp/transformers_cache
        - name: NCCL_DEBUG
          value: INFO
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 300
          periodSeconds: 30
          timeoutSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
        resources:
          requests:
            memory: "80Gi"
            cpu: "20"
            nvidia.com/gpu: "${GPU_COUNT}"
          limits:
            nvidia.com/gpu: "${GPU_COUNT}"
        volumeMounts:
        - name: gcs-fuse-models
          mountPath: /gcs
          readOnly: true
        - name: dshm
          mountPath: /dev/shm
      nodeSelector:
        cloud.google.com/gke-accelerator: ${GPU_TYPE}
      volumes:
      - name: gcs-fuse-models
        csi:
          driver: gcsfuse.csi.storage.gke.io
          volumeAttributes:
            bucketName: ${MODEL_BUCKET}
            mountOptions: "implicit-dirs,max-conns-per-host=100"
            fileCacheCapacity: "100Gi"
            fileCacheForRangeRead: "true"
            metadataStatCacheCapacity: "50000"
            metadataTypeCacheCapacity: "10000"
      - name: dshm
        emptyDir:
          medium: Memory
          sizeLimit: "40Gi"
DEPEOF

# Create service
cat > "${MANIFEST_DIR}/service.yaml" << 'SVCEOF'
apiVersion: v1
kind: Service
metadata:
  name: vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}
  namespace: inference-online-gpu
  labels:
    app: vllm
    model: ${HF_MODEL_NAME}
    accelerator: ${ACCELERATOR_TYPE}
spec:
  type: ClusterIP
  selector:
    app: vllm
    model: ${HF_MODEL_NAME}
    accelerator: ${ACCELERATOR_TYPE}
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
SVCEOF

# Create HPA
cat > "${MANIFEST_DIR}/hpa.yaml" << 'HPAEOF'
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}
  namespace: inference-online-gpu
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 120
      policies:
      - type: Pods
        value: 1
        periodSeconds: 180
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 300
HPAEOF

# Substitute environment variables in all files
for file in "${MANIFEST_DIR}"/*.yaml; do
    envsubst < "$file" > "${file}.tmp"
    mv "${file}.tmp" "$file"
done

# Apply manifests
echo -e "\n${GREEN}Deploying vLLM inference workload...${NC}"
kubectl apply -k "${MANIFEST_DIR}"

DEPLOYMENT_NAME="vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}"

echo -e "\n${YELLOW}Waiting for deployment to be ready...${NC}"
echo -e "${YELLOW}This may take 5-15 minutes for model loading...${NC}\n"

# Watch deployment
kubectl rollout status deployment/"${DEPLOYMENT_NAME}" \
    -n inference-online-gpu \
    --timeout=30m

echo -e "\n${GREEN}Deployment ready!${NC}"

# Show status
kubectl get deployment,pod,svc,hpa -n inference-online-gpu \
    -l model="${HF_MODEL_NAME}"

echo -e "\n${GREEN}vLLM inference workload deployed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Test inference: ./06-test-inference.sh"
echo -e "  2. View logs: kubectl logs -n inference-online-gpu -l model=${HF_MODEL_NAME} --tail=50"
echo -e "  3. Port forward: kubectl port-forward -n inference-online-gpu svc/${DEPLOYMENT_NAME} 8000:8000"
