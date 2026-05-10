#!/bin/bash

################################################################################
# Post-Deployment Hook for Pnkln GKE Services
#
# This hook runs after deployment to validate:
# - Deployment rollout status
# - Pod health and readiness
# - Service availability
# - Health endpoint responses
# - Log analysis for errors
# - Performance metrics
#
# Exit codes:
#   0 - Deployment successful and validated
#   1 - Deployment failed validation
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-pnkln-project}"
CLUSTER_NAME="${GKE_CLUSTER_NAME:-pnkln-cluster}"
CLUSTER_REGION="${GKE_CLUSTER_REGION:-us-central1}"
NAMESPACE="${K8S_NAMESPACE:-pnkln}"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-staging}"
VALIDATION_TIMEOUT="${VALIDATION_TIMEOUT:-300}"  # 5 minutes

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
}

# Fail validation
fail_validation() {
    log_error "$1"
    log_error "Deployment validation failed!"
    log_error ""
    log_error "Recommended action: Review logs and consider rollback"
    log_error "  kubectl rollout undo deployment/[service-name] -n $NAMESPACE"
    exit 1
}

################################################################################
# Post-Deployment Validation
################################################################################

log_section "POST-DEPLOYMENT VALIDATION"
log_info "Starting post-deployment validation..."
log_info "Environment: $DEPLOYMENT_ENV"
log_info "Namespace: $NAMESPACE"
log_info "Validation timeout: ${VALIDATION_TIMEOUT}s"
echo ""

################################################################################
# Deployment Rollout Status
################################################################################

log_section "DEPLOYMENT ROLLOUT STATUS"

log_info "Fetching deployments in namespace '$NAMESPACE'..."
deployments=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

if [ -z "$deployments" ]; then
    fail_validation "No deployments found in namespace '$NAMESPACE'"
fi

log_info "Found deployments: $deployments"
echo ""

# Check rollout status for each deployment
for deployment in $deployments; do
    log_info "Checking rollout status for '$deployment'..."

    if timeout "$VALIDATION_TIMEOUT" kubectl rollout status deployment/"$deployment" -n "$NAMESPACE"; then
        log_info "✓ Deployment '$deployment' rolled out successfully"
    else
        fail_validation "Deployment '$deployment' failed to roll out within ${VALIDATION_TIMEOUT}s"
    fi
done

echo ""

################################################################################
# Pod Health Check
################################################################################

log_section "POD HEALTH CHECK"

log_info "Checking pod status..."
kubectl get pods -n "$NAMESPACE" -o wide

echo ""

# Count pods by status
total_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | wc -l)
running_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c "Running" || echo "0")
pending_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c "Pending" || echo "0")
failed_pods=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -cE "Error|CrashLoopBackOff|ImagePullBackOff" || echo "0")

log_info "Pod Status Summary:"
log_info "  Total: $total_pods"
log_info "  Running: $running_pods"
log_info "  Pending: $pending_pods"
log_info "  Failed: $failed_pods"

if [ "$failed_pods" -gt 0 ]; then
    log_error "Found $failed_pods failed pod(s):"
    kubectl get pods -n "$NAMESPACE" | grep -E "Error|CrashLoopBackOff|ImagePullBackOff"
    fail_validation "Pods are in failed state"
fi

if [ "$pending_pods" -gt 0 ]; then
    log_warn "Found $pending_pods pending pod(s)"
    log_warn "This may indicate resource constraints"
fi

log_info "✓ All pods are healthy"
echo ""

# Check container readiness
log_info "Checking container readiness..."
not_ready=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | \
    awk '{print $2}' | grep -c "0/" || echo "0")

if [ "$not_ready" -gt 0 ]; then
    log_warn "Some containers are not ready:"
    kubectl get pods -n "$NAMESPACE" | awk '$2 ~ /0\//  {print $0}'

    # Wait a bit for containers to become ready
    log_info "Waiting 30s for containers to become ready..."
    sleep 30

    not_ready=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | \
        awk '{print $2}' | grep -c "0/" || echo "0")

    if [ "$not_ready" -gt 0 ]; then
        fail_validation "Containers failed to become ready"
    fi
fi

log_info "✓ All containers are ready"
echo ""

################################################################################
# Service Availability Check
################################################################################

log_section "SERVICE AVAILABILITY CHECK"

log_info "Checking services..."
kubectl get services -n "$NAMESPACE"

echo ""

services=$(kubectl get services -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

if [ -z "$services" ]; then
    log_warn "No services found in namespace '$NAMESPACE'"
else
    log_info "Found services: $services"

    for service in $services; do
        endpoints=$(kubectl get endpoints "$service" -n "$NAMESPACE" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || echo "")

        if [ -z "$endpoints" ]; then
            log_warn "Service '$service' has no endpoints"
        else
            endpoint_count=$(echo "$endpoints" | wc -w)
            log_info "✓ Service '$service' has $endpoint_count endpoint(s)"
        fi
    done
fi

echo ""

################################################################################
# Health Endpoint Validation
################################################################################

log_section "HEALTH ENDPOINT VALIDATION"

log_info "Testing health endpoints..."

# Get all pods with their IPs
pod_data=$(kubectl get pods -n "$NAMESPACE" -o json 2>/dev/null)

if [ -z "$pod_data" ]; then
    log_warn "Could not retrieve pod data"
else
    # Extract pod names
    pod_names=$(echo "$pod_data" | jq -r '.items[].metadata.name' 2>/dev/null || echo "")

    if [ -n "$pod_names" ]; then
        for pod in $pod_names; do
            # Check if pod is running
            pod_status=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")

            if [ "$pod_status" = "Running" ]; then
                log_info "Testing health endpoint for pod '$pod'..."

                # Try common health endpoints
                for path in "/health" "/healthz" "/ready" "/readyz"; do
                    if kubectl exec -n "$NAMESPACE" "$pod" -- curl -sf "http://localhost:8000$path" >/dev/null 2>&1; then
                        log_info "  ✓ $path endpoint is healthy"
                        break
                    fi
                done
            fi
        done
    fi
fi

echo ""

################################################################################
# Log Analysis
################################################################################

log_section "LOG ANALYSIS"

log_info "Analyzing recent logs for errors..."

for deployment in $deployments; do
    log_info "Checking logs for deployment '$deployment'..."

    # Get logs from last 5 minutes
    recent_logs=$(kubectl logs deployment/"$deployment" -n "$NAMESPACE" --since=5m --tail=100 2>/dev/null || echo "")

    if [ -z "$recent_logs" ]; then
        log_warn "No recent logs found for '$deployment'"
        continue
    fi

    # Count errors
    error_count=$(echo "$recent_logs" | grep -ciE "error|exception|fatal" || echo "0")
    warning_count=$(echo "$recent_logs" | grep -ciE "warning|warn" || echo "0")

    log_info "  Errors: $error_count"
    log_info "  Warnings: $warning_count"

    if [ "$error_count" -gt 10 ]; then
        log_error "High error count detected in '$deployment' logs:"
        echo "$recent_logs" | grep -iE "error|exception|fatal" | head -5
        fail_validation "Excessive errors in logs for deployment '$deployment'"
    elif [ "$error_count" -gt 0 ]; then
        log_warn "Some errors detected in '$deployment' logs:"
        echo "$recent_logs" | grep -iE "error|exception|fatal" | head -3
    fi
done

log_info "✓ Log analysis completed"
echo ""

################################################################################
# Resource Utilization Check
################################################################################

log_section "RESOURCE UTILIZATION CHECK"

log_info "Checking resource utilization..."
kubectl top pods -n "$NAMESPACE" 2>/dev/null || log_warn "Metrics server not available"

echo ""

# Check for resource-constrained pods
log_info "Checking for resource constraints..."
oom_killed=$(kubectl get pods -n "$NAMESPACE" -o json 2>/dev/null | \
    jq -r '.items[] | select(.status.containerStatuses[]?.lastState.terminated.reason == "OOMKilled") | .metadata.name' || echo "")

if [ -n "$oom_killed" ]; then
    log_error "Found OOM killed pods:"
    echo "$oom_killed"
    fail_validation "Pods were killed due to out of memory"
fi

log_info "✓ No resource constraint issues detected"
echo ""

################################################################################
# Event Analysis
################################################################################

log_section "RECENT EVENTS ANALYSIS"

log_info "Checking recent events..."
warning_events=$(kubectl get events -n "$NAMESPACE" --field-selector type=Warning \
    --sort-by='.lastTimestamp' 2>/dev/null | tail -n +2 | head -10)

if [ -n "$warning_events" ]; then
    log_warn "Recent warning events:"
    echo "$warning_events"
    echo ""

    # Count critical events
    critical_events=$(echo "$warning_events" | grep -ciE "failed|error|backoff" || echo "0")

    if [ "$critical_events" -gt 5 ]; then
        fail_validation "Too many critical events detected"
    fi
else
    log_info "✓ No warning events found"
fi

echo ""

################################################################################
# Deployment Comparison
################################################################################

log_section "DEPLOYMENT COMPARISON"

for deployment in $deployments; do
    log_info "Deployment '$deployment' status:"

    desired=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
    current=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.replicas}' 2>/dev/null || echo "0")
    available=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.availableReplicas}' 2>/dev/null || echo "0")
    ready=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")

    log_info "  Desired: $desired"
    log_info "  Current: $current"
    log_info "  Available: $available"
    log_info "  Ready: $ready"

    if [ "$available" -ne "$desired" ]; then
        log_warn "Available replicas ($available) != Desired replicas ($desired)"

        if [ "$DEPLOYMENT_ENV" = "production" ] && [ "$available" -lt "$desired" ]; then
            fail_validation "Not all replicas are available in production"
        fi
    fi

    if [ "$ready" -ne "$desired" ]; then
        log_warn "Ready replicas ($ready) != Desired replicas ($desired)"
    fi

    log_info "✓ Deployment '$deployment' replica count is acceptable"
done

echo ""

################################################################################
# Performance Validation
################################################################################

log_section "PERFORMANCE VALIDATION"

log_info "Waiting 30s to collect performance metrics..."
sleep 30

log_info "Checking response times..."
for deployment in $deployments; do
    pods=$(kubectl get pods -n "$NAMESPACE" -l "app=$deployment" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")

    if [ -n "$pods" ]; then
        for pod in $pods; do
            # Test response time
            log_info "Testing response time for pod '$pod'..."

            response_time=$(kubectl exec -n "$NAMESPACE" "$pod" -- \
                sh -c 'time curl -sf http://localhost:8000/health' 2>&1 | \
                grep real | awk '{print $2}' || echo "N/A")

            if [ "$response_time" != "N/A" ]; then
                log_info "  Response time: $response_time"
            fi
        done
    fi
done

echo ""

################################################################################
# Final Summary
################################################################################

log_section "POST-DEPLOYMENT VALIDATION SUMMARY"

log_info "Environment: $DEPLOYMENT_ENV"
log_info "Namespace: $NAMESPACE"
log_info "Deployments validated: $deployments"
log_info ""

log_info "${GREEN}✓ Deployment validation passed successfully!${NC}"
log_info ""

# Display summary table
log_info "Deployment Summary:"
kubectl get deployments,pods,services -n "$NAMESPACE"

echo ""
log_info "Next steps:"
log_info "  1. Monitor logs: kubectl logs -f deployment/[service-name] -n $NAMESPACE"
log_info "  2. Check metrics: kubectl top pods -n $NAMESPACE"
log_info "  3. View details: kubectl describe deployment/[service-name] -n $NAMESPACE"
log_info ""

# Record deployment
log_info "Recording deployment metadata..."
cat > /tmp/deployment-record-$(date +%Y%m%d-%H%M%S).json <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "$DEPLOYMENT_ENV",
  "namespace": "$NAMESPACE",
  "cluster": "$CLUSTER_NAME",
  "region": "$CLUSTER_REGION",
  "deployments": $(kubectl get deployments -n "$NAMESPACE" -o json | jq -c '[.items[] | {name: .metadata.name, replicas: .spec.replicas, image: .spec.template.spec.containers[0].image}]'),
  "status": "success"
}
EOF

log_info "Deployment record saved to /tmp/deployment-record-*.json"
echo ""

log_info "${BLUE}Deployment completed successfully!${NC}"

exit 0
