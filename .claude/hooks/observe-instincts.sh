#!/bin/bash
# observe-instincts.sh — Captures tool use observations for the instinct system
# Source: ECC continuous-learning-v2/hooks/observe.sh (adapted)
# Wired to PreToolUse + PostToolUse hooks

set -euo pipefail

HOMUNCULUS_DIR="$HOME/.claude/homunculus"
CONFIG_FILE="$HOMUNCULUS_DIR/config.json"

# Check if observer is enabled
if [ -f "$CONFIG_FILE" ]; then
    ENABLED=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['observer']['enabled'])" 2>/dev/null || echo "false")
    if [ "$ENABLED" != "True" ] && [ "$ENABLED" != "true" ]; then
        exit 0
    fi
fi

# Detect project context
PROJECT_ID=""
PROJECT_NAME=""
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
    if [ -n "$REMOTE_URL" ]; then
        PROJECT_ID=$(echo -n "$REMOTE_URL" | shasum -a 256 | cut -c1-12)
    else
        REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
        if [ -n "$REPO_ROOT" ]; then
            PROJECT_ID=$(echo -n "$REPO_ROOT" | shasum -a 256 | cut -c1-12)
        fi
    fi
    PROJECT_NAME=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
fi

# Determine observation target directory
if [ -n "$PROJECT_ID" ]; then
    OBS_DIR="$HOMUNCULUS_DIR/projects/$PROJECT_ID"
    mkdir -p "$OBS_DIR/instincts/personal" "$OBS_DIR/instincts/inherited" "$OBS_DIR/evolved"

    # Write project metadata if missing
    if [ ! -f "$OBS_DIR/project.json" ]; then
        cat > "$OBS_DIR/project.json" <<PROJ
{
  "id": "$PROJECT_ID",
  "name": "$PROJECT_NAME",
  "root": "$(git rev-parse --show-toplevel 2>/dev/null || echo "")",
  "remote": "$(git remote get-url origin 2>/dev/null || echo "")",
  "first_seen": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
PROJ
    fi
    OBS_FILE="$OBS_DIR/observations.jsonl"
else
    OBS_FILE="$HOMUNCULUS_DIR/observations.jsonl"
fi

# Read hook input from stdin (JSON with tool_name, tool_input, session_id, etc.)
INPUT=$(cat 2>/dev/null || echo "{}")

# Build observation record
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id',''))" 2>/dev/null || echo "")

# Append observation (atomic append, no lock needed for JSONL)
echo "{\"ts\":\"$TIMESTAMP\",\"tool\":\"$TOOL_NAME\",\"session\":\"$SESSION_ID\",\"project\":\"$PROJECT_ID\",\"project_name\":\"$PROJECT_NAME\"}" >> "$OBS_FILE"

# Rotate observations if > 10K lines
if [ -f "$OBS_FILE" ]; then
    LINE_COUNT=$(wc -l < "$OBS_FILE" | tr -d ' ')
    if [ "$LINE_COUNT" -gt 10000 ]; then
        ARCHIVE_DIR="$(dirname "$OBS_FILE")/observations.archive"
        mkdir -p "$ARCHIVE_DIR"
        mv "$OBS_FILE" "$ARCHIVE_DIR/observations_$(date +%Y%m%d_%H%M%S).jsonl"
    fi
fi
