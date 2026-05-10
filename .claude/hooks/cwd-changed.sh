#!/bin/bash
# CwdChanged hook — fires when the working directory changes
# Updates workspace metadata and validates new CWD safety

set -e

INPUT=$(cat)

# Extract new CWD from hook input
NEW_CWD=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    hook_input = data.get('hook_input', data)
    print(hook_input.get('cwd', hook_input.get('newCwd', '')))
except Exception:
    print('')
")

if [ -z "$NEW_CWD" ]; then
    exit 0
fi

# =================================================================
# SECURITY: Validate CWD is not in a dangerous location
# =================================================================
BLOCKED_PATHS=(
    "/System"
    "/usr/local"
    "/private/var"
    "/Library/LaunchDaemons"
    "/Library/LaunchAgents"
)

for blocked in "${BLOCKED_PATHS[@]}"; do
    if [[ "$NEW_CWD" == "$blocked"* ]]; then
        echo "BLOCKED: CWD change to restricted path: $NEW_CWD" >&2
        exit 2  # Block the operation
    fi
done

# =================================================================
# WORKSPACE METADATA: Update session state
# =================================================================
LOGDIR="${CLAUDE_PROJECT_DIR:-.}/.claude/logs"
mkdir -p "$LOGDIR"
echo "[$(date -Iseconds)] CwdChanged: $NEW_CWD" >> "$LOGDIR/cwd-audit.log"

# Check if new CWD contains a git repository
if [ -d "$NEW_CWD/.git" ] || git -C "$NEW_CWD" rev-parse --git-dir >/dev/null 2>&1; then
    BRANCH=$(git -C "$NEW_CWD" branch --show-current 2>/dev/null || echo "detached")
    echo "📂 CWD → $NEW_CWD (git: $BRANCH)"
else
    echo "📂 CWD → $NEW_CWD (no git)"
fi

# Check for nested CLAUDE.md in new directory
if [ -f "$NEW_CWD/CLAUDE.md" ] || [ -f "$NEW_CWD/.claude/CLAUDE.md" ]; then
    echo "📋 Found CLAUDE.md in new CWD"
fi

# Output JSON for watchPaths — watch critical config files in new CWD
python3 -c "
import json
paths = []
for name in ['.env', '.envrc', 'CLAUDE.md', '.claude/CLAUDE.md', 'package.json', 'pyproject.toml']:
    import os
    p = os.path.join('$NEW_CWD', name)
    if os.path.exists(p):
        paths.append(p)
if paths:
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'CwdChanged', 'watchPaths': paths}}))
"

exit 0
