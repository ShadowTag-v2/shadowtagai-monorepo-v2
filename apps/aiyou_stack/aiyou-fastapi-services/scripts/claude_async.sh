#!/bin/bash

# ==============================================================================
# PNKLN ASYNC WRAPPER (CLAUDE CODE)
# ------------------------------------------------------------------------------
# PURPOSE: Wraps Claude Code CLI calls to capture Teleport URLs and generate
#          Apertus-compatible JSONL logs for future indexing.
#
# USAGE:   ./claude_async.sh "context_tag" "Your prompt here"
# EXAMPLE: ./claude_async.sh "shadowtag_audit" "Analyze generic_watermark.py for defects"
# ==============================================================================

set -e

# --- CONFIGURATION ---
LOG_BASE_DIR="./logs/pnkln/claude-async"
MANIFEST_FILE="$LOG_BASE_DIR/manifest.jsonl"
mkdir -p "$LOG_BASE_DIR"

# --- INPUTS ---
CONTEXT_ID="$1"
PROMPT_INPUT="$2"

if [[ -z "$CONTEXT_ID" || -z "$PROMPT_INPUT" ]]; then
  echo "Usage: $0 <context_id> <prompt>"
  echo "Example: $0 'judge_6_review' 'Check this logic against GDPR Art 17'"
  exit 1
fi

# --- METADATA GENERATION ---
RUN_ID=$(uuidgen)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="$LOG_BASE_DIR/${TIMESTAMP}_${RUN_ID}.raw.log"

echo "------------------------------------------------"
echo "🚀 STARTING PNKLN ASYNC TASK"
echo "ID:      $RUN_ID"
echo "Context: $CONTEXT_ID"
echo "Log:     $LOG_FILE"
echo "------------------------------------------------"

# --- EXECUTION ---
# We run Claude in the background, piping stdout/stderr to our raw log.
# Note: We assume the CLI prints the URL to stdout.
# We explicitly do NOT wait for it to finish (Fire & Forget).
nohup bash -c "echo '$PROMPT_INPUT' | claude -p" > "$LOG_FILE" 2>&1 &
PID=$!

echo "✅ Process started (PID: $PID)"

# --- TELEPORT URL CAPTURE (Best Effort) ---
# Wait 5 seconds to allow the CLI to initialize and print the URL
sleep 5

# Attempt to grep the URL from the log file
# Regex matches standard Claude/Anthropic project URLs
TELEPORT_URL=$(grep -oE "https://(claude\.ai|console\.anthropic\.com)[^[:space:]]*" "$LOG_FILE" | head -n 1)

if [[ -z "$TELEPORT_URL" ]]; then
  TELEPORT_URL="PENDING_OR_NOT_FOUND"
  echo "⚠️  Teleport URL not yet detected (check logs later)"
else
  echo "🔗 Teleport URL: $TELEPORT_URL"
fi

# --- APERTUS-COMPATIBLE JSON GENERATION ---
# We use jq to safely escape the prompt and structure the object.
# This schema matches the "Pnkln Governance Index" requirements.

JSON_PAYLOAD=$(jq -n \
                  --arg rid "$RUN_ID" \
                  --arg ts "$TIMESTAMP" \
                  --arg ctx "$CONTEXT_ID" \
                  --arg content "$PROMPT_INPUT" \
                  --arg url "$TELEPORT_URL" \
                  --arg log "$LOG_FILE" \
                  '{
                    run_id: $rid,
                    timestamp: $ts,
                    context_id: $ctx,
                    content: $content,
                    safety_scores: {
                      compliance_flag: false,
                      manual_review: false
                    },
                    meta: {
                      teleport_url: $url,
                      local_log_path: $log,
                      status: "initiated"
                    }
                  }')

# --- MANIFEST APPEND ---
echo "$JSON_PAYLOAD" >> "$MANIFEST_FILE"

echo "📝 Manifest updated."
echo "------------------------------------------------"
