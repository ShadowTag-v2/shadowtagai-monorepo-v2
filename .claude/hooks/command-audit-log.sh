#!/usr/bin/env bash
# command-audit-log.sh — ECC-style PostToolUse(Bash) audit logger
# Source: everything-claude-code hooks/post/command-log-audit.sh
# Adapted for Antigravity monorepo
#
# Logs all bash commands executed during a session to an audit file.
# Enables post-session review, security auditing, and cost analysis.

set -euo pipefail

AUDIT_DIR="${HOME}/.claude/audit"
AUDIT_FILE="${AUDIT_DIR}/command-log-$(date +%Y-%m-%d).jsonl"

# Read hook input from stdin
INPUT=$(cat)

# Extract fields from hook input
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id','unknown'))" 2>/dev/null || echo "unknown")
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
CWD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || echo "")

# Only log Bash tool calls
if [ "$TOOL_NAME" != "Bash" ]; then
  echo '{}'
  exit 0
fi

# Extract the command from tool_input
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# Create audit directory if needed
mkdir -p "$AUDIT_DIR"

# Write audit entry
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -c "
import json, sys
entry = {
    'timestamp': '$TIMESTAMP',
    'session_id': '$SESSION_ID',
    'cwd': '$CWD',
    'command': $(echo "$COMMAND" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null || echo '""')
}
print(json.dumps(entry))
" >> "$AUDIT_FILE"

# Output empty result (non-blocking)
echo '{}'
