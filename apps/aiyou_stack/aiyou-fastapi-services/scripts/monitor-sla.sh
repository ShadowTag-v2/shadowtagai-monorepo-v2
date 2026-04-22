#!/bin/bash
# Pnkln Judge 6 - Real-time SLA Monitor
# Purpose: Monitor p99 latency and alert on SLA breaches

set -euo pipefail

NAMESPACE="pnkln-core"
SLA_P99_MS=90
SLA_P95_MS=60
SLA_P50_MS=30
PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus-server.pnkln-monitoring.svc.cluster.local:9090}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_metric() {
    echo -e "${BLUE}[METRIC]${NC} $1"
}

query_prometheus() {
    local query="$1"
    local result=$(curl -s "${PROMETHEUS_URL}/api/v1/query" \
        --data-urlencode "query=${query}" | jq -r '.data.result[0].value[1] // "null"')
    echo "$result"
}

log_info "========================================"
log_info "JUDGE #6 SLA MONITOR"
log_info "========================================"
log_info "Prometheus: ${PROMETHEUS_URL}"
log_info "Namespace: ${NAMESPACE}"
log_info "SLA Targets: p99≤${SLA_P99_MS}ms, p95≤${SLA_P95_MS}ms, p50≤${SLA_P50_MS}ms"
log_info "========================================"
echo ""

# Query current latency percentiles
log_info "Fetching current latency metrics..."

P99_QUERY="histogram_quantile(0.99, sum(rate(judge_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[1m])) by (le)) * 1000"
P95_QUERY="histogram_quantile(0.95, sum(rate(judge_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[1m])) by (le)) * 1000"
P50_QUERY="histogram_quantile(0.50, sum(rate(judge_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[1m])) by (le)) * 1000"

P99=$(query_prometheus "$P99_QUERY")
P95=$(query_prometheus "$P95_QUERY")
P50=$(query_prometheus "$P50_QUERY")

# Request rate
RPS_QUERY="sum(rate(judge_request_total{namespace=\"${NAMESPACE}\"}[1m]))"
RPS=$(query_prometheus "$RPS_QUERY")

# Error rate
ERROR_RATE_QUERY="sum(rate(judge_request_errors_total{namespace=\"${NAMESPACE}\"}[5m])) / sum(rate(judge_request_total{namespace=\"${NAMESPACE}\"}[5m])) * 100"
ERROR_RATE=$(query_prometheus "$ERROR_RATE_QUERY")

# GPU utilization
GPU_UTIL_QUERY="avg(nvidia_gpu_duty_cycle{namespace=\"${NAMESPACE}\"})"
GPU_UTIL=$(query_prometheus "$GPU_UTIL_QUERY")

# Active replicas
REPLICAS=$(kubectl get deployment judge-6-hybrid -n ${NAMESPACE} -o jsonpath='{.status.availableReplicas}' 2>/dev/null || echo "0")

# Display metrics
log_info "Current Metrics:"
echo ""

# Latency
if [ "$P99" != "null" ]; then
    P99_INT=$(printf "%.0f" "$P99")
    if [ "$P99_INT" -le "$SLA_P99_MS" ]; then
        log_metric "✓ p99: ${P99_INT}ms (SLA: ≤${SLA_P99_MS}ms)"
    else
        log_error "✗ p99: ${P99_INT}ms (SLA: ≤${SLA_P99_MS}ms) - BREACH!"
    fi
else
    log_warn "p99: No data available"
fi

if [ "$P95" != "null" ]; then
    P95_INT=$(printf "%.0f" "$P95")
    if [ "$P95_INT" -le "$SLA_P95_MS" ]; then
        log_metric "✓ p95: ${P95_INT}ms (SLA: ≤${SLA_P95_MS}ms)"
    else
        log_warn "⚠ p95: ${P95_INT}ms (SLA: ≤${SLA_P95_MS}ms) - WARNING"
    fi
else
    log_warn "p95: No data available"
fi

if [ "$P50" != "null" ]; then
    P50_INT=$(printf "%.0f" "$P50")
    if [ "$P50_INT" -le "$SLA_P50_MS" ]; then
        log_metric "✓ p50: ${P50_INT}ms (SLA: ≤${SLA_P50_MS}ms)"
    else
        log_warn "⚠ p50: ${P50_INT}ms (SLA: ≤${SLA_P50_MS}ms) - WARNING"
    fi
else
    log_warn "p50: No data available"
fi

echo ""

# Request rate
if [ "$RPS" != "null" ]; then
    RPS_FORMATTED=$(printf "%.2f" "$RPS")
    log_metric "Request Rate: ${RPS_FORMATTED} req/s"
else
    log_warn "Request Rate: No data"
fi

# Error rate
if [ "$ERROR_RATE" != "null" ] && [ "$ERROR_RATE" != "NaN" ]; then
    ERROR_RATE_FORMATTED=$(printf "%.2f" "$ERROR_RATE")
    if (( $(echo "$ERROR_RATE_FORMATTED > 5.0" | bc -l) )); then
        log_error "Error Rate: ${ERROR_RATE_FORMATTED}% - HIGH!"
    else
        log_metric "Error Rate: ${ERROR_RATE_FORMATTED}%"
    fi
else
    log_metric "Error Rate: 0.00%"
fi

# GPU utilization
if [ "$GPU_UTIL" != "null" ]; then
    GPU_UTIL_FORMATTED=$(printf "%.1f" "$GPU_UTIL")
    log_metric "GPU Utilization: ${GPU_UTIL_FORMATTED}%"
else
    log_warn "GPU Utilization: No data"
fi

# Replicas
log_metric "Active Replicas: ${REPLICAS}"

echo ""
log_info "========================================"

# Layer breakdown
log_info "Layer Latency Breakdown (p99):"
GEMINI_P99_QUERY="histogram_quantile(0.99, sum(rate(judge_layer_duration_seconds_bucket{layer=\"gemini\"}[1m])) by (le)) * 1000"
PYTORCH_P99_QUERY="histogram_quantile(0.99, sum(rate(judge_layer_duration_seconds_bucket{layer=\"pytorch\"}[1m])) by (le)) * 1000"
RULES_P99_QUERY="histogram_quantile(0.99, sum(rate(judge_layer_duration_seconds_bucket{layer=\"rules\"}[1m])) by (le)) * 1000"

GEMINI_P99=$(query_prometheus "$GEMINI_P99_QUERY")
PYTORCH_P99=$(query_prometheus "$PYTORCH_P99_QUERY")
RULES_P99=$(query_prometheus "$RULES_P99_QUERY")

if [ "$GEMINI_P99" != "null" ]; then
    log_metric "  Gemini (L1): $(printf "%.1f" "$GEMINI_P99")ms"
fi

if [ "$PYTORCH_P99" != "null" ]; then
    log_metric "  PyTorch (L2): $(printf "%.1f" "$PYTORCH_P99")ms"
fi

if [ "$RULES_P99" != "null" ]; then
    log_metric "  Rules (L3): $(printf "%.1f" "$RULES_P99")ms"
fi

echo ""
log_info "========================================"

# SLA verdict
if [ "$P99" != "null" ]; then
    P99_INT=$(printf "%.0f" "$P99")
    if [ "$P99_INT" -le "$SLA_P99_MS" ]; then
        log_info "✓ SLA COMPLIANT"
        exit 0
    else
        log_error "✗ SLA BREACH - KILL SWITCH CONDITION MET"
        log_error "Recommendation: Abort validation sprint, pivot to ground-up architecture"
        exit 1
    fi
else
    log_warn "Insufficient data for SLA assessment"
    exit 2
fi
