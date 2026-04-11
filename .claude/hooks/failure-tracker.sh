#!/usr/bin/env bash
# failure-tracker.sh — PostToolUseFailure handler
# Source: everything-claude-code hooks/post/mcp-health-check pattern
# Adapted for Antigravity monorepo
#
# Tracks tool failures and triggers MCP health checks on repeated failures.
# Implements the circuit breaker pattern from Rule 24 (Resilience).

set -euo pipefail

FAILURE_DIR="${HOME}/.claude/failures"
FAILURE_FILE="${FAILURE_DIR}/failure-log-$(date +%Y-%m-%d).jsonl"
CIRCUIT_FILE="${FAILURE_DIR}/.circuit-state.json"

# Read hook input from stdin
INPUT=$(cat)

# Extract fields
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','unknown'))" 2>/dev/null || echo "unknown")
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
ERROR=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error','')[:200])" 2>/dev/null || echo "")
IS_INTERRUPT=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('is_interrupt', False))" 2>/dev/null || echo "False")

# Create failure directory
mkdir -p "$FAILURE_DIR"

# Log the failure
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -c "
import json
entry = {
    'timestamp': '$TIMESTAMP',
    'session_id': '$SESSION_ID',
    'tool_name': '$TOOL_NAME',
    'error_preview': '''$ERROR'''[:200],
    'is_interrupt': $IS_INTERRUPT
}
print(json.dumps(entry))
" >> "$FAILURE_FILE" 2>/dev/null || true

# Circuit breaker: count recent failures for this tool
RECENT_FAILURES=$(tail -20 "$FAILURE_FILE" 2>/dev/null | grep -c "\"$TOOL_NAME\"" || echo "0")

OUTPUT='{}'

if [ "$RECENT_FAILURES" -ge 3 ]; then
  # Circuit breaker tripped — emit warning
  OUTPUT=$(python3 -c "
import json
output = {
    'hookSpecificOutput': {
        'hookEventName': 'PostToolUseFailure',
        'additionalContext': '⚠️ Circuit breaker: $TOOL_NAME has failed $RECENT_FAILURES times recently. Consider: (1) checking MCP server health, (2) switching to alternative tool, (3) investigating root cause.'
    }
}
print(json.dumps(output))
")
fi

echo "$OUTPUT"
