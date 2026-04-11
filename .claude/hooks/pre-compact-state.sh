#!/usr/bin/env bash
# pre-compact-state.sh — PreCompact hook for state preservation
# Source: everything-claude-code PreCompact patterns
# Adapted for Antigravity monorepo
#
# Runs before manual compaction to save important state:
# 1. Git status snapshot
# 2. Active branch and recent commits
# 3. Modified file list
# This state survives compaction and helps rebuild context.

set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

CWD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || echo "$(pwd)")
TRIGGER=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('trigger','manual'))" 2>/dev/null || echo "manual")
CUSTOM_INSTRUCTIONS=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('custom_instructions','') or '')" 2>/dev/null || echo "")

# Capture git state
GIT_BRANCH=$(cd "$CWD" && git branch --show-current 2>/dev/null || echo "detached")
GIT_STATUS=$(cd "$CWD" && git status --porcelain 2>/dev/null | head -20 || echo "no git")
GIT_RECENT=$(cd "$CWD" && git log --oneline -5 2>/dev/null || echo "no commits")
MODIFIED_COUNT=$(cd "$CWD" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ' || echo "0")

# Build context summary that survives compaction
CONTEXT="📋 Pre-compact state capture (${TRIGGER}):
Branch: ${GIT_BRANCH}
Modified files: ${MODIFIED_COUNT}
Recent commits:
${GIT_RECENT}"

if [ -n "$CUSTOM_INSTRUCTIONS" ]; then
  CONTEXT="${CONTEXT}
Custom focus: ${CUSTOM_INSTRUCTIONS}"
fi

if [ "$MODIFIED_COUNT" -gt 0 ]; then
  CONTEXT="${CONTEXT}
Changed files:
${GIT_STATUS}"
fi

python3 -c "
import json
output = {
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'additionalContext': '''${CONTEXT}'''
    }
}
print(json.dumps(output))
"
