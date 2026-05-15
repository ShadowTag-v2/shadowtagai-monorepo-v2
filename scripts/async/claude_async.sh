#!/bin/bash
# =============================================================================
# Claude Code Async Wrapper with Teleport URL Capture
# Based on JR Engine Tuned Decision: OPTION 1 - EXPLOIT NOW, FENCE AND MEASURE
#
# PURPOSE: Non-blocking long-running tasks for:
#   - ShadowTag DCT watermark analysis
#   - JR Engine / Judge 6 performance analytics
#   - Large refactor/code review simulations
#
# GUARDRAILS:
#   - NO schema migrations
#   - NO infra changes
#   - NO secrets
#   - NO live-customer data
# =============================================================================

set -euo pipefail

VERSION="1.0.0"
LOG_DIR="/var/log/pnkln/claude-async"
MANIFEST_FILE="$LOG_DIR/async_manifest.jsonl"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_teleport() { echo -e "${CYAN}[TELEPORT]${NC} $1"; }

# =============================================================================
# KILL-SWITCH CONDITIONS (p99 survivability)
# =============================================================================
# Trigger kill-switch if ANY of:
#   - Message display bug hides critical conversation parts
#   - Teleport URL not presented or not capturable
#   - Local logs missing or corrupted
#   - Inconsistency between CLI output and web conversation
# =============================================================================

KILL_SWITCH_FILE="$LOG_DIR/.kill_switch"

check_kill_switch() {
    if [ -f "$KILL_SWITCH_FILE" ]; then
        log_error "KILL-SWITCH ACTIVE: Async Claude disabled due to p99 violation"
        log_error "Reason: $(cat "$KILL_SWITCH_FILE")"
        log_error "Remove $KILL_SWITCH_FILE after investigation to re-enable"
        exit 1
    fi
}

activate_kill_switch() {
    local reason="$1"
    echo "$reason" > "$KILL_SWITCH_FILE"
    log_error "KILL-SWITCH ACTIVATED: $reason"
    log_error "Async Claude is now DISABLED"
}

# =============================================================================
# SETUP
# =============================================================================

setup_logging() {
    mkdir -p "$LOG_DIR"

    if [ ! -f "$MANIFEST_FILE" ]; then
        echo '{"version":"1.0","created":"'$(date -Iseconds)'"}' > "$MANIFEST_FILE"
    fi
}

# =============================================================================
# MAIN ASYNC WRAPPER
# =============================================================================

run_async() {
    local task_name="${1:-unnamed_task}"
    local prompt_file="${2:-}"
    local prompt_text="${3:-}"

    # Validate inputs
    if [ -z "$prompt_file" ] && [ -z "$prompt_text" ]; then
        log_error "Usage: claude_async.sh <task_name> <prompt_file> OR <task_name> - <prompt_text>"
        exit 1
    fi

    # Generate job ID
    local job_id="${task_name}_${TIMESTAMP}_$(openssl rand -hex 4)"
    local log_file="$LOG_DIR/${job_id}.log"
    local input_file="$LOG_DIR/${job_id}_input.json"

    log_info "Starting async job: $job_id"

    # Get prompt content
    local prompt
    if [ -n "$prompt_file" ] && [ -f "$prompt_file" ]; then
        prompt=$(cat "$prompt_file")
    else
        prompt="$prompt_text"
    fi

    # Write input manifest
    cat > "$input_file" << EOF
{
    "job_id": "$job_id",
    "task_name": "$task_name",
    "timestamp": "$(date -Iseconds)",
    "prompt_length": ${#prompt},
    "prompt_preview": "$(echo "$prompt" | head -c 200 | tr '\n' ' ')..."
}
EOF

    log_info "Input recorded: $input_file"
    log_info "Log file: $log_file"

    # Run Claude Code in background with output capture
    # The `&` puts it in background, tee captures output
    {
        echo "=== ASYNC JOB START: $job_id ==="
        echo "Timestamp: $(date -Iseconds)"
        echo "Task: $task_name"
        echo "---"

        # Execute Claude CLI (adjust path as needed)
        if command -v claude &> /dev/null; then
            echo "$prompt" | claude 2>&1
        else
            # Fallback: simulate for testing
            log_warn "Claude CLI not found, simulating..."
            echo "[SIMULATED] Processing: $prompt"
            sleep 5
            echo "[SIMULATED] Complete. Teleport URL would appear here."
        fi

        echo "---"
        echo "=== ASYNC JOB END: $job_id ==="
    } 2>&1 | tee "$log_file" &

    local pid=$!

    # Record to manifest
    local manifest_entry=$(cat << EOF
{"job_id":"$job_id","task":"$task_name","pid":$pid,"log":"$log_file","input":"$input_file","started":"$(date -Iseconds)","status":"running"}
EOF
)
    echo "$manifest_entry" >> "$MANIFEST_FILE"

    log_info "Job $job_id started (PID: $pid)"
    log_teleport "Monitor with: tail -f $log_file"
    log_teleport "Check status: $0 status $job_id"

    echo "$job_id"
}

# =============================================================================
# STATUS CHECK
# =============================================================================

check_status() {
    local job_id="$1"
    local log_file="$LOG_DIR/${job_id}.log"

    if [ ! -f "$log_file" ]; then
        log_error "Job not found: $job_id"
        exit 1
    fi

    # Check if still running
    local pid=$(grep "$job_id" "$MANIFEST_FILE" | tail -1 | jq -r '.pid // empty')
    local running="false"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        running="true"
    fi

    # Extract teleport URL if present
    local teleport_url=$(grep -oE 'https://claude\.ai/[a-zA-Z0-9/_-]+' "$log_file" 2>/dev/null | head -1 || echo "")

    cat << EOF
{
    "job_id": "$job_id",
    "running": $running,
    "log_file": "$log_file",
    "log_lines": $(wc -l < "$log_file"),
    "teleport_url": "${teleport_url:-null}",
    "last_line": "$(tail -1 "$log_file" | tr '"' "'")"
}
EOF
}

# =============================================================================
# LIST ALL JOBS
# =============================================================================

list_jobs() {
    log_info "Recent async jobs:"
    echo "---"
    tail -20 "$MANIFEST_FILE" | while read line; do
        local job_id=$(echo "$line" | jq -r '.job_id // empty')
        local task=$(echo "$line" | jq -r '.task // empty')
        local started=$(echo "$line" | jq -r '.started // empty')

        if [ -n "$job_id" ]; then
            local status="completed"
            local pid=$(echo "$line" | jq -r '.pid // empty')
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                status="running"
            fi
            printf "%-40s %-20s %-10s %s\n" "$job_id" "$task" "$status" "$started"
        fi
    done
}

# =============================================================================
# VALIDATE TRIAL RESULTS (p99 check)
# =============================================================================

validate_trial() {
    local job_id="$1"
    local log_file="$LOG_DIR/${job_id}.log"

    log_info "Validating p99 survivability for: $job_id"

    local failures=0
    local report=""

    # Check 1: Log file exists and has content
    if [ ! -f "$log_file" ] || [ ! -s "$log_file" ]; then
        report+="FAIL: Log file missing or empty\n"
        ((failures++))
    else
        report+="PASS: Log file exists ($(wc -l < "$log_file") lines)\n"
    fi

    # Check 2: Job start marker present
    if ! grep -q "ASYNC JOB START" "$log_file" 2>/dev/null; then
        report+="FAIL: Missing job start marker\n"
        ((failures++))
    else
        report+="PASS: Job start marker present\n"
    fi

    # Check 3: Job end marker present (if completed)
    if grep -q "ASYNC JOB END" "$log_file" 2>/dev/null; then
        report+="PASS: Job end marker present\n"
    else
        report+="WARN: Job end marker not found (may still be running)\n"
    fi

    # Check 4: No error indicators
    if grep -qi "error\|exception\|failed" "$log_file" 2>/dev/null; then
        report+="WARN: Error indicators found in log\n"
    else
        report+="PASS: No error indicators\n"
    fi

    echo -e "$report"

    if [ "$failures" -gt 0 ]; then
        log_error "VALIDATION FAILED: $failures critical issues"
        log_warn "Consider activating kill-switch if pattern repeats"
        return 1
    else
        log_info "VALIDATION PASSED"
        return 0
    fi
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    setup_logging
    check_kill_switch

    case "${1:-help}" in
        run)
            shift
            run_async "$@"
            ;;
        status)
            shift
            check_status "$@"
            ;;
        list)
            list_jobs
            ;;
        validate)
            shift
            validate_trial "$@"
            ;;
        kill-switch)
            shift
            activate_kill_switch "${1:-Manual activation}"
            ;;
        help|*)
            cat << EOF
Claude Code Async Wrapper v$VERSION

Usage:
    $0 run <task_name> <prompt_file>     Run async task from file
    $0 run <task_name> - "<prompt>"      Run async task from string
    $0 status <job_id>                   Check job status
    $0 list                              List recent jobs
    $0 validate <job_id>                 Validate p99 survivability
    $0 kill-switch "<reason>"            Activate kill-switch

Examples:
    $0 run shadowtag_analysis ./prompts/shadowtag.txt
    $0 run quick_review - "Review the auth module for security issues"
    $0 status shadowtag_analysis_20251125_143022_a1b2c3d4

Guardrails (MANDATORY):
    - NO schema migrations
    - NO infra changes
    - NO secrets or credentials
    - NO live customer data

Kill-switch triggers:
    - Message display bugs
    - Missing teleport URLs
    - Corrupted logs
    - CLI/web inconsistencies
EOF
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
