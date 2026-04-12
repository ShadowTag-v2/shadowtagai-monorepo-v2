#!/bin/bash
# Monitor inference deployment
# Based on: GoogleCloudPlatform/accelerated-platforms inference-ref-arch

set -euo pipefail

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Monitor Inference Deployment ===${NC}"

# Check required environment variables
if [ -z "${HF_MODEL_NAME:-}" ] || [ -z "${ACCELERATOR_TYPE:-}" ]; then
    echo -e "${RED}Error: Environment not configured.${NC}"
    echo -e "${YELLOW}Run: source .env.gcp-inference && source .env.model-info${NC}"
    exit 1
fi

DEPLOYMENT_NAME="vllm-${ACCELERATOR_TYPE}-${HF_MODEL_NAME}"
NAMESPACE="inference-online-gpu"

# Function to display header
show_header() {
    clear
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       GKE Inference Deployment Monitor                         ║${NC}"
    echo -e "${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║ Deployment: ${DEPLOYMENT_NAME}${NC}"
    echo -e "${GREEN}║ Namespace:  ${NAMESPACE}${NC}"
    echo -e "${GREEN}║ Updated:    $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to show deployment status
show_deployment_status() {
    echo -e "${BLUE}=== Deployment Status ===${NC}"
    kubectl get deployment "${DEPLOYMENT_NAME}" -n "${NAMESPACE}" 2>/dev/null || \
        echo -e "${RED}Deployment not found${NC}"
    echo ""
}

# Function to show pod status
show_pod_status() {
    echo -e "${BLUE}=== Pod Status ===${NC}"
    kubectl get pods -n "${NAMESPACE}" -l "model=${HF_MODEL_NAME}" \
        -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.phase,\
READY:.status.conditions[?\(@.type==\'Ready\'\)].status,\
RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp 2>/dev/null || \
        echo -e "${YELLOW}No pods found${NC}"
    echo ""
}

# Function to show resource usage
show_resource_usage() {
    echo -e "${BLUE}=== Resource Usage ===${NC}"

    # Get pod metrics
    kubectl top pods -n "${NAMESPACE}" -l "model=${HF_MODEL_NAME}" 2>/dev/null || \
        echo -e "${YELLOW}Metrics not available (metrics-server may not be installed)${NC}"
    echo ""
}

# Function to show HPA status
show_hpa_status() {
    echo -e "${BLUE}=== Horizontal Pod Autoscaler ===${NC}"
    kubectl get hpa "${DEPLOYMENT_NAME}" -n "${NAMESPACE}" 2>/dev/null || \
        echo -e "${YELLOW}HPA not found${NC}"
    echo ""
}

# Function to show service endpoints
show_service_status() {
    echo -e "${BLUE}=== Service & Endpoints ===${NC}"
    kubectl get svc,endpoints -n "${NAMESPACE}" -l "model=${HF_MODEL_NAME}" 2>/dev/null
    echo ""
}

# Function to show recent events
show_recent_events() {
    echo -e "${BLUE}=== Recent Events ===${NC}"
    kubectl get events -n "${NAMESPACE}" \
        --sort-by='.lastTimestamp' \
        --field-selector involvedObject.name="${DEPLOYMENT_NAME}" \
        2>/dev/null | tail -5
    echo ""
}

# Function to show recent logs
show_recent_logs() {
    echo -e "${BLUE}=== Recent Logs (last 10 lines) ===${NC}"

    POD_NAME=$(kubectl get pod -n "${NAMESPACE}" \
        -l "app=vllm,model=${HF_MODEL_NAME}" \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -n "$POD_NAME" ]; then
        kubectl logs -n "${NAMESPACE}" "${POD_NAME}" --tail=10 2>/dev/null || \
            echo -e "${YELLOW}Logs not available${NC}"
    else
        echo -e "${YELLOW}No running pods found${NC}"
    fi
    echo ""
}

# Function to show GPU utilization (if available)
show_gpu_stats() {
    echo -e "${BLUE}=== GPU Utilization ===${NC}"

    POD_NAME=$(kubectl get pod -n "${NAMESPACE}" \
        -l "app=vllm,model=${HF_MODEL_NAME}" \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -n "$POD_NAME" ]; then
        GPU_STATS=$(kubectl exec -n "${NAMESPACE}" "${POD_NAME}" -- \
            nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu \
            --format=csv,noheader,nounits 2>/dev/null || echo "")

        if [ -n "$GPU_STATS" ]; then
            echo "GPU | Name | Util% | Mem Used (MB) | Mem Total (MB) | Temp (C)"
            echo "----+------+-------+---------------+----------------+---------"
            echo "$GPU_STATS" | awk -F',' '{printf "%-3s | %-15s | %5s | %13s | %14s | %7s\n", $1, $2, $3, $4, $5, $6}'
        else
            echo -e "${YELLOW}GPU stats not available${NC}"
        fi
    else
        echo -e "${YELLOW}No running pods found${NC}"
    fi
    echo ""
}

# Function to show inference stats
show_inference_stats() {
    echo -e "${BLUE}=== Inference Statistics ===${NC}"

    # Try to get Prometheus metrics if available
    POD_NAME=$(kubectl get pod -n "${NAMESPACE}" \
        -l "app=vllm,model=${HF_MODEL_NAME}" \
        -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

    if [ -n "$POD_NAME" ]; then
        # Port forward to metrics endpoint
        kubectl port-forward -n "${NAMESPACE}" "${POD_NAME}" 8001:8000 > /dev/null 2>&1 &
        PF_PID=$!
        sleep 2

        # Try to fetch metrics
        METRICS=$(curl -s http://localhost:8001/metrics 2>/dev/null | \
            grep -E "vllm_" | head -10 || echo "")

        kill -9 ${PF_PID} 2>/dev/null || true

        if [ -n "$METRICS" ]; then
            echo "$METRICS"
        else
            echo -e "${YELLOW}Inference metrics not available${NC}"
        fi
    else
        echo -e "${YELLOW}No running pods found${NC}"
    fi
    echo ""
}

# Main monitoring loop or single run
MODE=${1:-"watch"}  # Options: watch, once

if [ "$MODE" = "watch" ]; then
    echo -e "${YELLOW}Starting continuous monitoring (press Ctrl+C to exit)...${NC}"
    sleep 2

    while true; do
        show_header
        show_deployment_status
        show_pod_status
        show_resource_usage
        show_hpa_status
        show_service_status
        show_gpu_stats
        show_recent_logs

        echo -e "${YELLOW}Refreshing in 10 seconds... (Ctrl+C to exit)${NC}"
        sleep 10
    done
else
    # Single run mode
    show_header
    show_deployment_status
    show_pod_status
    show_resource_usage
    show_hpa_status
    show_service_status
    show_gpu_stats
    show_recent_events
    show_recent_logs
    show_inference_stats
fi

echo -e "\n${GREEN}Monitoring complete!${NC}"
