#!/bin/bash
set -euo pipefail

################################################################################
# Pnkln SLA Monitor - Continuous Monitoring with Kill-Switch
################################################################################
# Purpose: Monitor Judge #6 p99/p95/p50 latencies with automatic kill-switch
# SLA Target: p99 ≤90ms, p95 ≤50ms, p50 ≤20ms
# Kill-Switch: Automatic shutdown on SLA breach + cost overrun
################################################################################

VERSION="1.0.0"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
NAMESPACE="${PNKLN_NAMESPACE:-pnkln-inference}"
SERVICE="${PNKLN_SERVICE:-pnkln-judge}"
CHECK_INTERVAL="${PNKLN_CHECK_INTERVAL:-60}"

# SLA targets (milliseconds)
TARGET_P99=90
TARGET_P95=50
TARGET_P50=20

# Kill-switch thresholds
BREACH_THRESHOLD=3  # Number of consecutive breaches before kill-switch
COST_DAILY_LIMIT=500  # Daily cost limit in USD

# State
BREACH_COUNT=0
LAST_CHECK_TIME=$(date +%s)

################################################################################
# Helper Functions
################################################################################

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

log_critical() {
    echo -e "${RED}[CRITICAL]${NC} $1"
}

check_kubectl() {
    if ! command -v kubectl &>/dev/null; then
        log_error "kubectl not found. Install from: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi

    if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
        log_error "Namespace $NAMESPACE not found"
        exit 1
    fi
}

get_metrics() {
    local endpoint="http://localhost:8001/api/v1/namespaces/${NAMESPACE}/services/${SERVICE}:9090/proxy/metrics"

    # Start kubectl port-forward in background if not already running
    if ! pgrep -f "kubectl port-forward.*${SERVICE}" &>/dev/null; then
        kubectl port-forward -n "$NAMESPACE" "svc/$SERVICE" 8001:9090 >/dev/null 2>&1 &
        sleep 2
    fi

    # Fetch metrics
    local metrics
    metrics=$(curl -s "$endpoint" 2>/dev/null || echo "")

    if [ -z "$metrics" ]; then
        log_error "Failed to fetch metrics from $endpoint"
        return 1
    fi

    echo "$metrics"
}

parse_histogram_metric() {
    local metrics="$1"
    local metric_name="$2"
    local quantile="$3"

    # Parse Prometheus histogram quantile
    # Format: metric_name{quantile="0.99"} value
    local value
    value=$(echo "$metrics" | grep "${metric_name}{" | grep "quantile=\"${quantile}\"" | awk '{print $2}' | head -1)

    if [ -z "$value" ] || [ "$value" = "NaN" ]; then
        echo "0"
    else
        # Convert to milliseconds if in seconds
        if (( $(echo "$value < 1" | bc -l) )); then
            value=$(echo "$value * 1000" | bc -l)
        fi
        printf "%.2f" "$value"
    fi
}

get_latency_metrics() {
    local metrics
    metrics=$(get_metrics)

    if [ -z "$metrics" ]; then
        return 1
    fi

    # Parse latency percentiles from http_request_duration_seconds histogram
    local p99 p95 p50

    p99=$(parse_histogram_metric "$metrics" "http_request_duration_seconds" "0.99")
    p95=$(parse_histogram_metric "$metrics" "http_request_duration_seconds" "0.95")
    p50=$(parse_histogram_metric "$metrics" "http_request_duration_seconds" "0.5")

    echo "$p99 $p95 $p50"
}

get_request_metrics() {
    local metrics
    metrics=$(get_metrics)

    if [ -z "$metrics" ]; then
        return 1
    fi

    # Parse request count and error rate
    local total_requests errors success_rate

    total_requests=$(echo "$metrics" | grep "^http_requests_total" | grep -v "#" | awk '{sum+=$2} END {print sum+0}')
    errors=$(echo "$metrics" | grep "^http_requests_total" | grep "status=\"5" | awk '{sum+=$2} END {print sum+0}')

    if [ "$total_requests" -gt 0 ]; then
        success_rate=$(echo "scale=2; (($total_requests - $errors) / $total_requests) * 100" | bc)
    else
        success_rate="100.00"
    fi

    echo "$total_requests $errors $success_rate"
}

get_pod_metrics() {
    local cpu_usage memory_usage pod_count

    # Get pod count
    pod_count=$(kubectl get pods -n "$NAMESPACE" -l "app=pnkln-judge" --field-selector=status.phase=Running -o json | jq '.items | length')

    # Get resource usage
    local metrics_output
    metrics_output=$(kubectl top pods -n "$NAMESPACE" -l "app=pnkln-judge" 2>/dev/null || echo "")

    if [ -n "$metrics_output" ]; then
        cpu_usage=$(echo "$metrics_output" | tail -n +2 | awk '{sum+=$2} END {print sum+0}')
        memory_usage=$(echo "$metrics_output" | tail -n +2 | awk '{sum+=$3} END {print sum+0}')
    else
        cpu_usage="0"
        memory_usage="0"
    fi

    echo "$pod_count $cpu_usage $memory_usage"
}

check_sla_compliance() {
    local p99=$1
    local p95=$2
    local p50=$3

    local compliant=true
    local violations=()

    # Check each percentile
    if (( $(echo "$p99 > $TARGET_P99" | bc -l) )); then
        violations+=("p99: ${p99}ms > ${TARGET_P99}ms")
        compliant=false
    fi

    if (( $(echo "$p95 > $TARGET_P95" | bc -l) )); then
        violations+=("p95: ${p95}ms > ${TARGET_P95}ms")
        compliant=false
    fi

    if (( $(echo "$p50 > $TARGET_P50" | bc -l) )); then
        violations+=("p50: ${p50}ms > ${TARGET_P50}ms")
        compliant=false
    fi

    if [ "$compliant" = false ]; then
        echo "BREACH: ${violations[*]}"
        return 1
    else
        echo "COMPLIANT"
        return 0
    fi
}

estimate_daily_cost() {
    local pod_count=$1

    # Cost estimates (per hour)
    local cpu_node_cost=0.476  # n2-standard-16
    local gpu_node_cost=1.09   # L4 GPU

    # Assume 1 CPU node always running, GPU nodes scale with pods
    local gpu_nodes=$(( (pod_count + 1) / 2 ))  # 2 pods per GPU node

    local hourly_cost=$(echo "scale=2; $cpu_node_cost + ($gpu_node_cost * $gpu_nodes)" | bc)
    local daily_cost=$(echo "scale=2; $hourly_cost * 24" | bc)

    echo "$daily_cost"
}

kill_switch() {
    local reason="$1"

    log_critical "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_critical "  KILL-SWITCH ACTIVATED"
    log_critical "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_critical "Reason: $reason"
    log_critical "Time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    log_critical ""

    # Scale down deployment to 0
    log_critical "Scaling down deployment to 0 replicas..."
    kubectl scale deployment "$SERVICE" -n "$NAMESPACE" --replicas=0 || {
        log_error "Failed to scale down deployment"
    }

    # Send alert (placeholder - implement actual alerting)
    log_critical "Sending alerts..."
    # TODO: Implement Slack/PagerDuty/Email alerts

    # Log to file
    local log_file="/tmp/pnkln-killswitch-$(date +%Y%m%d-%H%M%S).log"
    {
        echo "KILL-SWITCH ACTIVATED"
        echo "Reason: $reason"
        echo "Time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
        echo "Namespace: $NAMESPACE"
        echo "Service: $SERVICE"
        kubectl get pods -n "$NAMESPACE" -o wide
    } > "$log_file"

    log_critical "Kill-switch log saved to: $log_file"
    log_critical "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    exit 1
}

display_status() {
    local p99=$1
    local p95=$2
    local p50=$3
    local total_requests=$4
    local errors=$5
    local success_rate=$6
    local pod_count=$7
    local cpu_usage=$8
    local memory_usage=$9
    local daily_cost=${10}
    local sla_status=${11}

    clear

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Pnkln SLA Monitor v${VERSION}"
    echo "  Judge #6 Performance Dashboard"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # SLA Status
    if [[ "$sla_status" == "COMPLIANT" ]]; then
        echo -e "  SLA Status: ${GREEN}✓ COMPLIANT${NC}"
    else
        echo -e "  SLA Status: ${RED}✗ BREACH${NC} ($sla_status)"
    fi

    echo "  Last Check: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "  Breach Count: $BREACH_COUNT / $BREACH_THRESHOLD"
    echo ""

    # Latency metrics
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  LATENCY METRICS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # p99
    if (( $(echo "$p99 <= $TARGET_P99" | bc -l) )); then
        printf "  p99: ${GREEN}%.2f ms${NC} (target: ≤%d ms)\n" "$p99" "$TARGET_P99"
    else
        printf "  p99: ${RED}%.2f ms${NC} (target: ≤%d ms) ${RED}✗${NC}\n" "$p99" "$TARGET_P99"
    fi

    # p95
    if (( $(echo "$p95 <= $TARGET_P95" | bc -l) )); then
        printf "  p95: ${GREEN}%.2f ms${NC} (target: ≤%d ms)\n" "$p95" "$TARGET_P95"
    else
        printf "  p95: ${RED}%.2f ms${NC} (target: ≤%d ms) ${RED}✗${NC}\n" "$p95" "$TARGET_P95"
    fi

    # p50
    if (( $(echo "$p50 <= $TARGET_P50" | bc -l) )); then
        printf "  p50: ${GREEN}%.2f ms${NC} (target: ≤%d ms)\n" "$p50" "$TARGET_P50"
    else
        printf "  p50: ${RED}%.2f ms${NC} (target: ≤%d ms) ${RED}✗${NC}\n" "$p50" "$TARGET_P50"
    fi

    echo ""

    # Request metrics
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  REQUEST METRICS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "  Total Requests: %d\n" "$total_requests"
    printf "  Errors: %d\n" "$errors"
    printf "  Success Rate: %.2f%%\n" "$success_rate"
    echo ""

    # Resource metrics
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  RESOURCE METRICS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "  Running Pods: %d\n" "$pod_count"
    printf "  CPU Usage: %sm\n" "$cpu_usage"
    printf "  Memory Usage: %sMi\n" "$memory_usage"
    echo ""

    # Cost metrics
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  COST METRICS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "  Estimated Daily Cost: \$%.2f\n" "$daily_cost"
    printf "  Daily Limit: \$%d\n" "$COST_DAILY_LIMIT"

    if (( $(echo "$daily_cost > $COST_DAILY_LIMIT" | bc -l) )); then
        echo -e "  ${RED}WARNING: Cost exceeds daily limit!${NC}"
    fi

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

monitor_once() {
    log_info "Running single SLA check..."

    # Get metrics
    local latency_metrics request_metrics pod_metrics

    latency_metrics=$(get_latency_metrics)
    read -r p99 p95 p50 <<< "$latency_metrics"

    request_metrics=$(get_request_metrics)
    read -r total_requests errors success_rate <<< "$request_metrics"

    pod_metrics=$(get_pod_metrics)
    read -r pod_count cpu_usage memory_usage <<< "$pod_metrics"

    # Estimate costs
    local daily_cost
    daily_cost=$(estimate_daily_cost "$pod_count")

    # Check SLA compliance
    local sla_status
    sla_status=$(check_sla_compliance "$p99" "$p95" "$p50")

    # Display status
    display_status "$p99" "$p95" "$p50" "$total_requests" "$errors" "$success_rate" \
        "$pod_count" "$cpu_usage" "$memory_usage" "$daily_cost" "$sla_status"

    if [[ "$sla_status" != "COMPLIANT" ]]; then
        log_warning "SLA breach detected: $sla_status"
        return 1
    fi

    log_success "SLA check passed"
    return 0
}

monitor_continuous() {
    log_info "Starting continuous SLA monitoring (interval: ${CHECK_INTERVAL}s)"
    log_info "Press Ctrl+C to stop"
    echo ""

    while true; do
        # Get metrics
        local latency_metrics request_metrics pod_metrics

        latency_metrics=$(get_latency_metrics)
        read -r p99 p95 p50 <<< "$latency_metrics"

        request_metrics=$(get_request_metrics)
        read -r total_requests errors success_rate <<< "$request_metrics"

        pod_metrics=$(get_pod_metrics)
        read -r pod_count cpu_usage memory_usage <<< "$pod_metrics"

        # Estimate costs
        local daily_cost
        daily_cost=$(estimate_daily_cost "$pod_count")

        # Check cost overrun
        if (( $(echo "$daily_cost > $COST_DAILY_LIMIT" | bc -l) )); then
            kill_switch "Cost overrun: \$${daily_cost}/day > \$${COST_DAILY_LIMIT}/day"
        fi

        # Check SLA compliance
        local sla_status
        sla_status=$(check_sla_compliance "$p99" "$p95" "$p50")

        if [[ "$sla_status" != "COMPLIANT" ]]; then
            BREACH_COUNT=$((BREACH_COUNT + 1))

            if [ "$BREACH_COUNT" -ge "$BREACH_THRESHOLD" ]; then
                kill_switch "SLA breach threshold exceeded: $BREACH_COUNT consecutive breaches"
            fi
        else
            BREACH_COUNT=0
        fi

        # Display status
        display_status "$p99" "$p95" "$p50" "$total_requests" "$errors" "$success_rate" \
            "$pod_count" "$cpu_usage" "$memory_usage" "$daily_cost" "$sla_status"

        # Wait for next check
        sleep "$CHECK_INTERVAL"
    done
}

################################################################################
# Main Execution
################################################################################

main() {
    check_kubectl

    case "${1:-}" in
        --once|-o)
            monitor_once
            ;;
        --continuous|-c)
            monitor_continuous
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --once, -o         Run single SLA check"
            echo "  --continuous, -c   Run continuous monitoring (default)"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  PNKLN_NAMESPACE        Kubernetes namespace (default: pnkln-inference)"
            echo "  PNKLN_SERVICE          Service name (default: pnkln-judge)"
            echo "  PNKLN_CHECK_INTERVAL   Check interval in seconds (default: 60)"
            exit 0
            ;;
        "")
            monitor_continuous
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Run '$0 --help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"
