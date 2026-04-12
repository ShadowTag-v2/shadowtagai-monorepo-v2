#!/bin/bash
# ============================================================================
# tf-swarm.sh - Terraform with n-autoresearch/Kosmos/BioAgents Swarm Audit
# ============================================================================
#
# Usage:
#   ./scripts/tf-swarm.sh plan [terraform args...]
#   ./scripts/tf-swarm.sh apply
#   ./scripts/tf-swarm.sh audit <tfplan.json>
#   ./scripts/tf-swarm.sh burst-test [count]
#
# Description:
#   Wraps terraform commands with 600-agent swarm audit before apply.
#   - 570 Flash agents: Resource validation, naming, costs
#   - 30 Pro agents: JURA governance, security compliance
#
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
AUDIT_SCRIPT="$PROJECT_DIR/infrastructure/terraform/swarm_audit.py"
n-autoresearch/Kosmos/BioAgents_URL="${n-autoresearch/Kosmos/BioAgents_URL:-http://localhost:8600}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_n-autoresearch/Kosmos/BioAgents() {
    log_info "Checking n-autoresearch/Kosmos/BioAgents swarm..."
    HEALTH=$(curl -s "$n-autoresearch/Kosmos/BioAgents_URL/health" 2>/dev/null || echo '{}')

    if echo "$HEALTH" | jq -e '.status == "ok"' >/dev/null 2>&1; then
        AGENTS=$(echo "$HEALTH" | jq -r '.agents')
        log_success "n-autoresearch/Kosmos/BioAgents swarm online: $AGENTS agents"
        return 0
    else
        log_error "n-autoresearch/Kosmos/BioAgents swarm not available at $n-autoresearch/Kosmos/BioAgents_URL"
        return 1
    fi
}

run_swarm_audit() {
    local PLAN_JSON="$1"

    if [[ ! -f "$PLAN_JSON" ]]; then
        log_error "Plan file not found: $PLAN_JSON"
        return 1
    fi

    RESOURCE_COUNT=$(jq '.resource_changes | length' "$PLAN_JSON" 2>/dev/null || echo "0")
    echo ""
    log_info "Running swarm audit on $RESOURCE_COUNT resources..."
    echo ""

    python3 "$AUDIT_SCRIPT" "$PLAN_JSON"
    return $?
}

cmd_plan() {
    log_info "Running terraform plan..."

    # Run terraform plan
    terraform plan -out=tfplan "$@"

    # Export plan to JSON
    log_info "Exporting plan to JSON..."
    terraform show -json tfplan > tfplan.json

    # Check swarm is available
    if ! check_n-autoresearch/Kosmos/BioAgents; then
        log_warn "Skipping swarm audit (n-autoresearch/Kosmos/BioAgents unavailable)"
        log_warn "Run 'docker compose -f docker-compose.antigravity.yml up -d n-autoresearch/Kosmos/BioAgents' to start"
        return 0
    fi

    # Run swarm audit
    run_swarm_audit tfplan.json
}

cmd_apply() {
    if [[ -f ".swarm_approved" ]]; then
        log_success "Swarm audit approval found"
        log_info "Running terraform apply..."

        terraform apply tfplan

        # Cleanup
        rm -f .swarm_approved tfplan tfplan.json
        log_success "Apply complete, cleaned up temporary files"
    else
        log_error "Swarm audit required before apply"
        echo ""
        echo "Run: $0 plan"
        echo ""
        exit 1
    fi
}

cmd_audit() {
    local PLAN_JSON="${1:-tfplan.json}"

    if ! check_n-autoresearch/Kosmos/BioAgents; then
        exit 1
    fi

    run_swarm_audit "$PLAN_JSON"
}

cmd_burst_test() {
    local COUNT="${1:-600}"

    log_info "Running burst test with $COUNT parallel requests..."

    if ! check_n-autoresearch/Kosmos/BioAgents; then
        exit 1
    fi

    python3 -c "
import asyncio
import time
import httpx

async def burst_test():
    count = $COUNT
    url = '$n-autoresearch/Kosmos/BioAgents_URL/health'

    print(f'Firing {count} parallel requests to {url}...')
    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [client.get(url) for _ in range(count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = (time.perf_counter() - start) * 1000

    success = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 200)
    failed = count - success

    print()
    print('=' * 50)
    print(f'BURST TEST RESULTS')
    print('=' * 50)
    print(f'Total requests:    {count}')
    print(f'Successful:        {success}')
    print(f'Failed:            {failed}')
    print(f'Success rate:      {success/count*100:.1f}%')
    print(f'Total time:        {elapsed:.1f}ms')
    print(f'Avg per request:   {elapsed/count:.2f}ms')
    print(f'Throughput:        {count/elapsed*1000:.1f} req/sec')
    print('=' * 50)

asyncio.run(burst_test())
"
}

cmd_status() {
    echo ""
    echo "=========================================="
    echo "  TF-SWARM STATUS"
    echo "=========================================="
    echo ""

    # Check n-autoresearch/Kosmos/BioAgents
    HEALTH=$(curl -s "$n-autoresearch/Kosmos/BioAgents_URL/health" 2>/dev/null || echo '{}')
    if echo "$HEALTH" | jq -e '.status == "ok"' >/dev/null 2>&1; then
        AGENTS=$(echo "$HEALTH" | jq -r '.agents')
        UPTIME=$(echo "$HEALTH" | jq -r '.uptime_seconds // 0')
        BULK=$(echo "$HEALTH" | jq -r '.tiers.bulk.agents // 0')
        GOV=$(echo "$HEALTH" | jq -r '.tiers.governance.agents // 0')

        echo "n-autoresearch/Kosmos/BioAgents:  ONLINE"
        echo "  Agents:       $AGENTS total"
        echo "  Bulk (Flash): $BULK"
        echo "  Governance:   $GOV"
        echo "  Uptime:       ${UPTIME}s"
    else
        echo "n-autoresearch/Kosmos/BioAgents:  OFFLINE"
    fi

    echo ""

    # Check approval status
    if [[ -f ".swarm_approved" ]]; then
        echo "Approval:       APPROVED (ready to apply)"
    elif [[ -f "tfplan" ]]; then
        echo "Approval:       PENDING (run audit first)"
    else
        echo "Approval:       N/A (no plan found)"
    fi

    echo ""
    echo "=========================================="
}

cmd_help() {
    cat << EOF
tf-swarm - Terraform with n-autoresearch/Kosmos/BioAgents Swarm Audit

USAGE:
    tf-swarm <command> [args...]

COMMANDS:
    plan [args]         Run terraform plan + swarm audit
    apply               Apply (requires swarm approval)
    audit <file>        Run audit on existing plan JSON
    burst-test [count]  Test swarm with N parallel requests
    status              Show swarm and approval status
    help                Show this help

EXAMPLES:
    # Plan and audit infrastructure changes
    tf-swarm plan -target=module.gke

    # Apply after approval
    tf-swarm apply

    # Test swarm capacity
    tf-swarm burst-test 600

    # Audit existing plan
    tf-swarm audit my-plan.json

ENVIRONMENT:
    n-autoresearch/Kosmos/BioAgents_URL   n-autoresearch/Kosmos/BioAgents endpoint (default: http://localhost:8600)

EOF
}

# Main dispatch
ACTION="${1:-help}"
shift || true

case "$ACTION" in
    plan)
        cmd_plan "$@"
        ;;
    apply)
        cmd_apply "$@"
        ;;
    audit)
        cmd_audit "$@"
        ;;
    burst-test|burst)
        cmd_burst_test "$@"
        ;;
    status)
        cmd_status
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        # Pass through to terraform
        terraform "$ACTION" "$@"
        ;;
esac
