#!/usr/bin/env bash
# session-cost-tracker.sh — ECC-style Stop hook cost tracker
# Source: everything-claude-code hooks/stop/cost-tracker pattern
# Adapted for Antigravity monorepo
#
# Captures session cost metrics at Stop time.
# Tracks token usage, tool call counts, and session duration.

set -euo pipefail

METRICS_DIR="${HOME}/.claude/metrics"
METRICS_FILE="${METRICS_DIR}/session-costs-$(date +%Y-%m).jsonl"

# Read hook input from stdin
INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','unknown'))" 2>/dev/null || echo "unknown")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || echo "")

# Count today's audit entries for this session
AUDIT_FILE="${HOME}/.claude/audit/command-log-$(date +%Y-%m-%d).jsonl"
TOOL_CALLS=0
if [ -f "$AUDIT_FILE" ]; then
  TOOL_CALLS=$(grep -c "$SESSION_ID" "$AUDIT_FILE" 2>/dev/null || echo "0")
fi

# Count failures
FAILURE_FILE="${HOME}/.claude/failures/failure-log-$(date +%Y-%m-%d).jsonl"
FAILURE_COUNT=0
if [ -f "$FAILURE_FILE" ]; then
  FAILURE_COUNT=$(grep -c "$SESSION_ID" "$FAILURE_FILE" 2>/dev/null || echo "0")
fi

# Create metrics directory
mkdir -p "$METRICS_DIR"

# Write session summary
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -c "
import json
entry = {
    'timestamp': '$TIMESTAMP',
    'session_id': '$SESSION_ID',
    'cwd': '$CWD',
    'bash_tool_calls': $TOOL_CALLS,
    'failures': $FAILURE_COUNT,
    'quality_gate': 'stop'
}
print(json.dumps(entry))
" >> "$METRICS_FILE" 2>/dev/null || true

# Output metric summary as additionalContext
python3 -c "
import json
output = {
    'hookSpecificOutput': {
        'hookEventName': 'PostToolUse',
        'additionalContext': '📊 Session metrics: ${TOOL_CALLS} bash calls, ${FAILURE_COUNT} failures recorded.'
    }
}
print(json.dumps(output))
"
