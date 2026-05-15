#!/bin/bash
# deploy.sh - Full GKE inference deployment orchestrator
# Implements Google Cloud accelerated-platforms reference architecture

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
export PROJECT_ID="${PROJECT_ID:-pnkln-core-stack}"
export REGION="${REGION:-us-central1}"
export CLUSTER_NAME="${CLUSTER_NAME:-pnkln-inference-prod}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "${SCRIPT_DIR}")"
TERRAFORM_DIR="${ROOT_DIR}/terraform"
K8S_DIR="${ROOT_DIR}/k8s"

# Logging
LOG_FILE="${ROOT_DIR}/deployment_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "${LOG_FILE}")
exec 2>&1

echo "════════════════════════════════════════════════════════════════"
echo "  PNKLN CORE STACK™ - GKE INFERENCE DEPLOYMENT"
echo "  Target: p99 ≤90ms | Optimized Cost: \$48K/month"
echo "  Architecture: Google Cloud accelerated-platforms reference"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Deployment log: ${LOG_FILE}"
echo ""

# Run preflight checks
echo -e "${CYAN}▶ Running preflight checks...${NC}"
"${SCRIPT_DIR}/preflight.sh"

# Phase 1: Terraform Infrastructure
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${CYAN}PHASE 1: TERRAFORM INFRASTRUCTURE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd "${TERRAFORM_DIR}"

# Initialize Terraform
echo -e "${BLUE}▶ Initializing Terraform...${NC}"
terraform init

# Plan
echo ""
echo -e "${BLUE}▶ Creating Terraform plan...${NC}"
terraform plan -out=tfplan

# Show cost estimate
echo ""
echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  ESTIMATED MONTHLY COST: \$48,000                             ║${NC}"
echo -e "${YELLOW}║                                                              ║${NC}"
echo -e "${YELLOW}║  Breakdown:                                                  ║${NC}"
echo -e "${YELLOW}║  - GKE Control Plane:        \$500                            ║${NC}"
echo -e "${YELLOW}║  - Judge GPU Pool (L4):      \$6,000 (spot instances)        ║${NC}"
echo -e "${YELLOW}║  - LLM Prefill Pool:         \$4,000 (spot instances)        ║${NC}"
echo -e "${YELLOW}║  - LLM Decode Pool:          \$5,000 (spot instances)        ║${NC}"
echo -e "${YELLOW}║  - Auto-provisioned nodes:   \$8,000                          ║${NC}"
echo -e "${YELLOW}║  - LLM API costs:            \$22,000 (with caching)         ║${NC}"
echo -e "${YELLOW}║  - Inference Gateway:        \$500                            ║${NC}"
echo -e "${YELLOW}║  - Networking/LB:            \$1,500                          ║${NC}"
echo -e "${YELLOW}║  - Storage/Monitoring:       \$500                            ║${NC}"
echo -e "${YELLOW}║                                                              ║${NC}"
echo -e "${YELLOW}║  Performance targets:                                        ║${NC}"
echo -e "${YELLOW}║  - P99 latency: ≤90ms (target: 36ms with optimizations)     ║${NC}"
echo -e "${YELLOW}║  - Throughput: +30% vs baseline                              ║${NC}"
echo -e "${YELLOW}║  - TTFT: 96% improvement for prefix-heavy workloads          ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Confirm deployment
read -p "Deploy infrastructure? (yes/no): " CONFIRM
if [[ "${CONFIRM}" != "yes" ]]; then
    echo -e "${RED}Deployment cancelled.${NC}"
    exit 0
fi

# Apply Terraform
echo ""
echo -e "${BLUE}▶ Applying Terraform configuration...${NC}"
echo -e "${YELLOW}This will take approximately 10-15 minutes...${NC}"
terraform apply tfplan

# Get cluster credentials
echo ""
echo -e "${BLUE}▶ Configuring kubectl access...${NC}"
gcloud container clusters get-credentials "${CLUSTER_NAME}" \
    --region="${REGION}" \
    --project="${PROJECT_ID}"

echo -e "${GREEN}✓ Terraform infrastructure deployed${NC}"

# Phase 2: Kubernetes Deployments
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${CYAN}PHASE 2: KUBERNETES DEPLOYMENTS${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Create namespaces
echo -e "${BLUE}▶ Creating namespaces...${NC}"
kubectl apply -f "${K8S_DIR}/base/namespaces.yaml"
echo -e "${GREEN}✓ Namespaces created${NC}"

# Deploy Inference Gateway
echo ""
echo -e "${BLUE}▶ Deploying GKE Inference Gateway...${NC}"
kubectl apply -f "${K8S_DIR}/base/inference-gateway.yaml"

# Wait for Gateway to be ready
echo -n "Waiting for Gateway to be ready..."
kubectl wait --for=condition=Programmed \
    gateway/llm-inference-gateway \
    -n cognitive-stack-v5 \
    --timeout=300s
echo -e " ${GREEN}✓${NC}"

# Deploy disaggregated serving
echo ""
echo -e "${BLUE}▶ Deploying disaggregated LLM serving (prefill + decode)...${NC}"
kubectl apply -f "${K8S_DIR}/base/llm-disaggregated-serving.yaml"

# Deploy HPA
echo ""
echo -e "${BLUE}▶ Configuring Horizontal Pod Autoscaling...${NC}"
kubectl apply -f "${K8S_DIR}/base/hpa.yaml"
echo -e "${GREEN}✓ HPA configured${NC}"

# Phase 3: Verification
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${CYAN}PHASE 3: DEPLOYMENT VERIFICATION${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Wait for LLM deployments
echo -e "${BLUE}▶ Waiting for LLM prefill deployment...${NC}"
kubectl wait --for=condition=available --timeout=600s \
    deployment/llm-prefill -n cognitive-stack-v5
echo -e "${GREEN}✓ LLM prefill ready${NC}"

echo ""
echo -e "${BLUE}▶ Waiting for LLM decode deployment...${NC}"
kubectl wait --for=condition=available --timeout=600s \
    deployment/llm-decode -n cognitive-stack-v5
echo -e "${GREEN}✓ LLM decode ready${NC}"

# Get service endpoints
echo ""
echo -e "${BLUE}▶ Retrieving service endpoints...${NC}"
echo -n "Waiting for Gateway IP allocation..."
for i in {1..30}; do
    GATEWAY_IP=$(kubectl get gateway llm-inference-gateway -n cognitive-stack-v5 \
        -o jsonpath='{.status.addresses[0].value}' 2>/dev/null || echo "")
    if [[ -n "${GATEWAY_IP}" ]]; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    sleep 10
    echo -n "."
done

if [[ -z "${GATEWAY_IP}" ]]; then
    echo -e " ${YELLOW}⚠${NC}"
    echo "Gateway IP not yet allocated. Check status with:"
    echo "  kubectl get gateway -n cognitive-stack-v5"
else
    echo ""
    echo -e "${GREEN}Gateway IP: ${GATEWAY_IP}${NC}"
fi

# Display cluster info
echo ""
echo -e "${BLUE}▶ Cluster information:${NC}"
kubectl cluster-info

# Display node pools
echo ""
echo -e "${BLUE}▶ Node pools:${NC}"
kubectl get nodes -o wide

# Display deployments
echo ""
echo -e "${BLUE}▶ Deployed workloads:${NC}"
kubectl get deployments -A

# Display HPA status
echo ""
echo -e "${BLUE}▶ HPA status:${NC}"
kubectl get hpa -A

# Final summary
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}  ✓ DEPLOYMENT COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Cluster Details:"
echo "  Name:       ${CLUSTER_NAME}"
echo "  Region:     ${REGION}"
echo "  Project:    ${PROJECT_ID}"
if [[ -n "${GATEWAY_IP}" ]]; then
    echo "  Gateway IP: ${GATEWAY_IP}"
fi
echo ""
echo "Deployed Components:"
echo "  ✓ GKE Inference Gateway (with prefix-aware LB)"
echo "  ✓ Disaggregated LLM Serving (prefill + decode)"
echo "  ✓ Horizontal Pod Autoscaling (custom metrics)"
echo "  ✓ Monitoring & Observability"
echo ""
echo "Namespaces:"
echo "  - ShadowTag-v2jr-governance (Judge 6)"
echo "  - autogen-orchestration (Multi-agent)"
echo "  - cognitive-stack-v5 (LLM routing)"
echo "  - shadowtag-v2 (Watermarking)"
echo ""
echo "Next Steps:"
echo "  1. Verify health: ./scripts/validate.sh"
echo "  2. Deploy Judge 6: kubectl apply -f k8s/base/judge6-deployment.yaml"
echo "  3. Configure DNS: Point api.pnkln.ai to ${GATEWAY_IP}"
echo "  4. Set up SSL certificate"
echo "  5. Run load tests"
echo ""
echo "Monitoring:"
echo "  Logs:       gcloud logging read --project=${PROJECT_ID}"
echo "  Metrics:    https://console.cloud.google.com/monitoring?project=${PROJECT_ID}"
echo "  Dashboards: https://console.cloud.google.com/kubernetes/clusters?project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}Deployment log saved to: ${LOG_FILE}${NC}"
echo ""
