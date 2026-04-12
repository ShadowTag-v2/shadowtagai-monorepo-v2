#!/bin/bash
# Test deployed inference workload
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Test Inference Workload ===${NC}"

# Check required environment variables
REQUIRED_VARS=("HF_MODEL_ID" "HF_MODEL_NAME" "ACCELERATOR_TYPE")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo -e "${RED}Error: ${var} not set.${NC}"
        echo -e "${YELLOW}Run: source .env.gcp-inference && source .env.model-info${NC}"
        exit 1
    fi
done

DEPLOYMENT_NAME="vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}"
NAMESPACE="inference-online-gpu"

# Check if deployment exists
echo -e "${YELLOW}Checking deployment status...${NC}"
if ! kubectl get deployment "${DEPLOYMENT_NAME}" -n "${NAMESPACE}" &>/dev/null; then
    echo -e "${RED}Error: Deployment not found: ${DEPLOYMENT_NAME}${NC}"
    exit 1
fi

# Check pod status
POD_STATUS=$(kubectl get deployment "${DEPLOYMENT_NAME}" -n "${NAMESPACE}" \
    -o jsonpath='{.status.conditions[?(@.type=="Available")].status}')

if [ "$POD_STATUS" != "True" ]; then
    echo -e "${RED}Deployment not ready yet. Current status:${NC}"
    kubectl get deployment "${DEPLOYMENT_NAME}" -n "${NAMESPACE}"
    exit 1
fi

echo -e "${GREEN}✓ Deployment is ready${NC}"

# Setup port forwarding
echo -e "\n${YELLOW}Setting up port forwarding...${NC}"

# Kill any existing port forwards
pkill -f "port-forward.*${DEPLOYMENT_NAME}" || true
sleep 2

# Start port forward in background
kubectl port-forward -n "${NAMESPACE}" \
    "svc/${DEPLOYMENT_NAME}" 8000:8000 > /dev/null 2>&1 &
PF_PID=$!

# Wait for port forward to be ready
echo -e "${YELLOW}Waiting for port forward to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health &>/dev/null; then
        echo -e "${GREEN}✓ Port forward ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Port forward failed to start${NC}"
        kill -9 ${PF_PID} 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Test 1: Health check
echo -e "\n${BLUE}=== Test 1: Health Check ===${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "Response: ${HEALTH_RESPONSE}"

if echo "${HEALTH_RESPONSE}" | grep -q "ok\|healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi

# Test 2: List models
echo -e "\n${BLUE}=== Test 2: List Models ===${NC}"
MODELS_RESPONSE=$(curl -s http://localhost:8000/v1/models)
echo "${MODELS_RESPONSE}" | jq '.' 2>/dev/null || echo "${MODELS_RESPONSE}"

if echo "${MODELS_RESPONSE}" | grep -q "${HF_MODEL_ID}"; then
    echo -e "${GREEN}✓ Model loaded successfully${NC}"
else
    echo -e "${YELLOW}! Model may not be fully loaded${NC}"
fi

# Test 3: Simple completion
echo -e "\n${BLUE}=== Test 3: Chat Completion ===${NC}"

PROMPT="Why is the sky blue?"
echo -e "${YELLOW}Prompt: ${PROMPT}${NC}"

COMPLETION_REQUEST=$(cat <<JSONEOF
{
  "model": "/gcs/${HF_MODEL_ID}",
  "messages": [
    {
      "role": "user",
      "content": "${PROMPT}"
    }
  ],
  "max_tokens": 200,
  "temperature": 0.7
}
JSONEOF
)

echo -e "${YELLOW}Sending request...${NC}"
COMPLETION_RESPONSE=$(curl -s -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "${COMPLETION_REQUEST}")

echo -e "${GREEN}Response:${NC}"
echo "${COMPLETION_RESPONSE}" | jq '.' 2>/dev/null || echo "${COMPLETION_RESPONSE}"

# Extract and display the completion
COMPLETION_TEXT=$(echo "${COMPLETION_RESPONSE}" | \
    jq -r '.choices[0].message.content' 2>/dev/null || echo "")

if [ -n "$COMPLETION_TEXT" ] && [ "$COMPLETION_TEXT" != "null" ]; then
    echo -e "\n${GREEN}Generated text:${NC}"
    echo -e "${BLUE}${COMPLETION_TEXT}${NC}"
    echo -e "\n${GREEN}✓ Completion test passed${NC}"
else
    echo -e "${RED}✗ Completion test failed${NC}"
    echo "Full response: ${COMPLETION_RESPONSE}"
fi

# Test 4: Performance test
echo -e "\n${BLUE}=== Test 4: Performance Test ===${NC}"

echo -e "${YELLOW}Sending 5 concurrent requests...${NC}"

# Create temp directory for results
PERF_DIR="/tmp/inference-perf-test-$$"
mkdir -p "${PERF_DIR}"

# Send 5 concurrent requests
for i in {1..5}; do
    (
        START_TIME=$(date +%s.%N)
        curl -s -X POST http://localhost:8000/v1/chat/completions \
            -H "Content-Type: application/json" \
            -d '{
              "model": "/gcs/'"${HF_MODEL_ID}"'",
              "messages": [{"role": "user", "content": "Count to 10"}],
              "max_tokens": 50
            }' > "${PERF_DIR}/response_${i}.json"
        END_TIME=$(date +%s.%N)
        DURATION=$(echo "$END_TIME - $START_TIME" | bc)
        echo "$DURATION" > "${PERF_DIR}/duration_${i}.txt"
    ) &
done

# Wait for all requests to complete
wait

# Calculate statistics
TOTAL_TIME=0
COUNT=0

echo -e "\n${YELLOW}Results:${NC}"
for i in {1..5}; do
    if [ -f "${PERF_DIR}/duration_${i}.txt" ]; then
        DURATION=$(cat "${PERF_DIR}/duration_${i}.txt")
        echo "  Request $i: ${DURATION}s"
        TOTAL_TIME=$(echo "$TOTAL_TIME + $DURATION" | bc)
        COUNT=$((COUNT + 1))
    fi
done

if [ $COUNT -gt 0 ]; then
    AVG_TIME=$(echo "scale=2; $TOTAL_TIME / $COUNT" | bc)
    echo -e "${GREEN}Average latency: ${AVG_TIME}s${NC}"
    echo -e "${GREEN}✓ Performance test completed${NC}"
fi

# Cleanup
rm -rf "${PERF_DIR}"

# Test 5: GPU utilization
echo -e "\n${BLUE}=== Test 5: GPU Utilization ===${NC}"

POD_NAME=$(kubectl get pod -n "${NAMESPACE}" \
    -l "app=vllm,model=${HF_MODEL_NAME}" \
    -o jsonpath='{.items[0].metadata.name}')

if [ -n "$POD_NAME" ]; then
    echo -e "${YELLOW}Pod: ${POD_NAME}${NC}"

    # Try to get GPU stats (may not work in all environments)
    echo -e "${YELLOW}Attempting to get GPU stats...${NC}"
    kubectl exec -n "${NAMESPACE}" "${POD_NAME}" -- nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader 2>/dev/null || \
        echo -e "${YELLOW}GPU stats not available (this is normal for some cluster configurations)${NC}"
fi

# Cleanup port forward
echo -e "\n${YELLOW}Cleaning up port forward...${NC}"
kill -9 ${PF_PID} 2>/dev/null || true

echo -e "\n${GREEN}=== Test Summary ===${NC}"
echo -e "${GREEN}✓ All tests completed${NC}"
echo -e ""
echo -e "${YELLOW}Deployment info:${NC}"
kubectl get deployment,pod,svc -n "${NAMESPACE}" -l "model=${HF_MODEL_NAME}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  - View logs: kubectl logs -n ${NAMESPACE} -l model=${HF_MODEL_NAME} --tail=100"
echo -e "  - Monitor metrics: ./07-monitor-deployment.sh"
echo -e "  - Scale deployment: kubectl scale deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE} --replicas=3"
echo -e "  - Delete deployment: ./99-cleanup.sh"
