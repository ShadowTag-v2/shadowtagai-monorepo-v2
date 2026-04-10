#!/bin/bash
# ==============================================================================
# PNKLN ASYNC WRAPPER (CLAUDE CODE)
# ------------------------------------------------------------------------------
# PURPOSE: Wraps Claude Code CLI calls to capture Teleport URLs and generate
#          Apertus-compatible JSONL logs for future Elasticsearch indexing.
#
# USAGE:   ./claude_async.sh start "context_tag" "Your prompt here"
# EXAMPLE: ./claude_async.sh start "shadowtag_audit" "Analyze generic_watermark.py"
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs/async"
PNKLN_LOG_DIR="$PROJECT_ROOT/logs/pnkln/claude-async"
MANIFEST_FILE="$PNKLN_LOG_DIR/manifest.jsonl"
CONTEXT_INDEX="$PROJECT_ROOT/docs/CONTEXT_INDEX.json"

# Configuration - 4hr guard shift optimal
MAX_RUNTIME_MINUTES=${MAX_RUNTIME_MINUTES:-240}
P99_LATENCY_THRESHOLD_MS=${P99_LATENCY_THRESHOLD_MS:-5000}
MAX_CONSECUTIVE_ERRORS=${MAX_CONSECUTIVE_ERRORS:-3}

mkdir -p "$LOG_DIR"
mkdir -p "$PNKLN_LOG_DIR"

usage() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start <context_id> <prompt>  Start async task (Apertus-compatible)"
    echo "  status <job_id>              Check job status"
    echo "  kill <job_id>                Kill running job"
    echo "  list                         List running jobs"
    echo "  rotate                       Rotate shifts (kill old, start fresh)"
    echo "  manifest                     Show recent manifest entries"
    echo ""
    echo "Options:"
    echo "  --tier FREE|FLASH|PRO        API tier (default: FREE)"
    echo "  --timeout <minutes>          Max runtime (default: 240 = 4hr guard shift)"
}

generate_job_id() {
    echo "job_$(date +%Y%m%d_%H%M%S)"
}

check_kill_conditions() {
    local job_id="$1"
    local log_file="$LOG_DIR/$job_id.log"

    local error_count=$(grep -c "ERROR\|Error\|error" "$log_file" 2>/dev/null || echo 0)
    if [[ $error_count -ge $MAX_CONSECUTIVE_ERRORS ]]; then
        echo "KILL: Max consecutive errors exceeded ($error_count >= $MAX_CONSECUTIVE_ERRORS)"
        return 1
    fi

    local start_time=$(stat -f %m "$log_file" 2>/dev/null || stat -c %Y "$log_file" 2>/dev/null)
    local now=$(date +%s)
    local runtime=$(( (now - start_time) / 60 ))
    if [[ $runtime -ge $MAX_RUNTIME_MINUTES ]]; then
        echo "KILL: 4hr guard shift exceeded ($runtime >= $MAX_RUNTIME_MINUTES minutes)"
        return 1
    fi

    return 0
}

start_job() {
    local context_id="$1"
    local prompt="$2"
    local tier="${3:-FREE}"

    if [[ -z "$context_id" || -z "$prompt" ]]; then
        echo "ERROR: context_id and prompt required"
        exit 1
    fi

    # Generate unique identifiers
    local run_id=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "$(date +%s)-$$")
    local job_id=$(generate_job_id)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local log_file="$LOG_DIR/$job_id.log"
    local pnkln_log="$PNKLN_LOG_DIR/${timestamp}_${run_id}.raw.log"
    local pid_file="$LOG_DIR/$job_id.pid"

    # Create job metadata (legacy format)
    cat > "$LOG_DIR/$job_id.json" << EOF
{
    "job_id": "$job_id",
    "run_id": "$run_id",
    "context_id": "$context_id",
    "tier": "$tier",
    "prompt": "$prompt",
    "started": "$timestamp",
    "status": "running",
    "guard_shift": "4hr"
}
EOF

    echo "------------------------------------------------"
    echo "STARTING PNKLN ASYNC TASK"
    echo "Job ID:   $job_id"
    echo "Run ID:   $run_id"
    echo "Context:  $context_id"
    echo "Tier:     $tier"
    echo "Log:      $log_file"
    echo "Guard:    4hr max"
    echo "------------------------------------------------"

    (
        echo $$ > "$pid_file"

        echo "=== Claude Async Job: $job_id ===" >> "$log_file"
        echo "Run ID: $run_id" >> "$log_file"
        echo "Context: $context_id" >> "$log_file"
        echo "Started: $(date)" >> "$log_file"
        echo "Guard Shift: 4hr" >> "$log_file"
        echo "Prompt: $prompt" >> "$log_file"
        echo "===" >> "$log_file"

        if command -v claude &> /dev/null; then
            claude "$prompt" 2>&1 | tee -a "$log_file" "$pnkln_log"
        else
            echo "ERROR: claude command not found" >> "$log_file"
        fi

        echo "" >> "$log_file"
        echo "=== Completed: $(date) ===" >> "$log_file"

        # Update job status
        if [[ -f "$LOG_DIR/$job_id.json" ]]; then
            tmp=$(mktemp)
            jq '.status = "completed" | .completed = "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"' \
                "$LOG_DIR/$job_id.json" > "$tmp" && mv "$tmp" "$LOG_DIR/$job_id.json"
        fi

        rm -f "$pid_file"
    ) &

    local pid=$!
    echo $pid > "$pid_file"

    echo "Process started (PID: $pid)"

    # Wait briefly to capture Teleport URL
    sleep 3

    # Attempt to capture Teleport URL from log
    local teleport_url=$(grep -oE "https://(claude\.ai|console\.anthropic\.com)[^[:space:]]*" "$log_file" 2>/dev/null | head -n 1 || true)
    if [[ -z "$teleport_url" ]]; then
        teleport_url="PENDING_OR_NOT_FOUND"
        echo "Teleport URL not yet detected (check logs later)"
    else
        echo "Teleport URL: $teleport_url"
    fi

    # Generate Apertus-compatible JSONL for future Elasticsearch indexing
    if command -v jq &> /dev/null; then
        local json_payload=$(jq -n \
            --arg rid "$run_id" \
            --arg jid "$job_id" \
            --arg ts "$timestamp" \
            --arg ctx "$context_id" \
            --arg content "$prompt" \
            --arg url "$teleport_url" \
            --arg log "$log_file" \
            --arg tier "$tier" \
            '{
                run_id: $rid,
                job_id: $jid,
                timestamp: $ts,
                context_id: $ctx,
                content: $content,
                tier: $tier,
                safety_scores: {
                    compliance_flag: false,
                    manual_review: false
                },
                meta: {
                    teleport_url: $url,
                    local_log_path: $log,
                    status: "initiated",
                    guard_shift: "4hr"
                }
            }')
        echo "$json_payload" >> "$MANIFEST_FILE"
        echo "Manifest updated: $MANIFEST_FILE"
    fi

    echo "------------------------------------------------"
}

show_manifest() {
    if [[ -f "$MANIFEST_FILE" ]]; then
        echo "Recent manifest entries:"
        tail -5 "$MANIFEST_FILE" | jq .
    else
        echo "No manifest file found"
    fi
}

check_status() {
    local job_id="$1"
    local meta_file="$LOG_DIR/$job_id.json"
    local pid_file="$LOG_DIR/$job_id.pid"
    local log_file="$LOG_DIR/$job_id.log"

    if [[ ! -f "$meta_file" ]]; then
        echo "ERROR: Job not found: $job_id"
        exit 1
    fi

    local status=$(jq -r '.status' "$meta_file")
    local thread_id=$(jq -r '.thread_id' "$meta_file")
    local started=$(jq -r '.started' "$meta_file")

    echo "Job: $job_id"
    echo "Thread: $thread_id"
    echo "Started: $started"
    echo "Status: $status"

    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "PID: $pid (running)"
            if ! check_kill_conditions "$job_id"; then
                echo "WARNING: Kill condition triggered!"
            fi
        fi
    fi

    if [[ -f "$log_file" ]]; then
        echo ""
        echo "Last 10 lines:"
        tail -10 "$log_file"
    fi
}

kill_job() {
    local job_id="$1"
    local pid_file="$LOG_DIR/$job_id.pid"
    local meta_file="$LOG_DIR/$job_id.json"

    if [[ ! -f "$pid_file" ]]; then
        echo "No PID file for job: $job_id"
        exit 1
    fi

    local pid=$(cat "$pid_file")

    if ps -p "$pid" > /dev/null 2>&1; then
        echo "Killing job $job_id (PID: $pid)"
        kill "$pid" 2>/dev/null || true
        sleep 1
        kill -9 "$pid" 2>/dev/null || true

        if [[ -f "$meta_file" ]]; then
            tmp=$(mktemp)
            jq '.status = "killed"' "$meta_file" > "$tmp" && mv "$tmp" "$meta_file"
        fi

        rm -f "$pid_file"
        echo "Job killed"
    else
        echo "Job not running"
    fi
}

rotate_shifts() {
    echo "///▞ Rotating guard shifts..."

    for meta_file in "$LOG_DIR"/*.json; do
        if [[ -f "$meta_file" ]]; then
            local job_id=$(jq -r '.job_id' "$meta_file")
            local pid_file="$LOG_DIR/$job_id.pid"

            if [[ -f "$pid_file" ]]; then
                if ! check_kill_conditions "$job_id" 2>/dev/null; then
                    echo "Rotating out: $job_id"
                    kill_job "$job_id"
                fi
            fi
        fi
    done

    echo "///▞ Shift rotation complete"
}

list_jobs() {
    echo "Async Jobs (4hr guard shifts):"
    echo ""
    printf "%-25s %-12s %-10s %s\n" "JOB_ID" "THREAD" "STATUS" "STARTED"

    for meta_file in "$LOG_DIR"/*.json; do
        if [[ -f "$meta_file" ]]; then
            local job_id=$(jq -r '.job_id' "$meta_file")
            local thread_id=$(jq -r '.thread_id' "$meta_file")
            local status=$(jq -r '.status' "$meta_file")
            local started=$(jq -r '.started' "$meta_file")

            printf "%-25s %-12s %-10s %s\n" "$job_id" "$thread_id" "$status" "$started"
        fi
    done
}

case "${1:-}" in
    start)
        start_job "$2" "$3" "$4"
        ;;
    status)
        check_status "$2"
        ;;
    kill)
        kill_job "$2"
        ;;
    rotate)
        rotate_shifts
        ;;
    list)
        list_jobs
        ;;
    manifest)
        show_manifest
        ;;
    *)
        usage
        exit 1
        ;;
esac
