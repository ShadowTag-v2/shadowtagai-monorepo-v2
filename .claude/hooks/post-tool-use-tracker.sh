#!/bin/bash
# Post-Tool-Use Tracker Hook
# Logs all file edits to track changes across sessions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$CLAUDE_DIR/edit-log.json"

# Get tool use details from environment
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
FILE_PATH="${CLAUDE_FILE_PATH:-}"
LINES_CHANGED="${CLAUDE_LINES_CHANGED:-0}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Get current task from dev-docs if available
CURRENT_TASK="${CLAUDE_CURRENT_TASK:-none}"

# Only log file edits
if [[ "$TOOL_NAME" == "edit_file" || "$TOOL_NAME" == "write_file" ]]; then
    # Initialize log file if it doesn't exist
    if [ ! -f "$LOG_FILE" ]; then
        echo "[]" > "$LOG_FILE"
    fi

    # Create log entry
    ENTRY=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "tool": "$TOOL_NAME",
  "file": "$FILE_PATH",
  "linesChanged": $LINES_CHANGED,
  "task": "$CURRENT_TASK"
}
EOF
)

    # Append to log (using jq if available, otherwise simple append)
    if command -v jq >/dev/null 2>&1; then
        TMP_FILE=$(mktemp)
        jq ". += [$ENTRY]" "$LOG_FILE" > "$TMP_FILE"
        mv "$TMP_FILE" "$LOG_FILE"
    else
        # Fallback: simple JSON array append
        sed -i '' -e '$ s/]$/,/' "$LOG_FILE"
        echo "$ENTRY" >> "$LOG_FILE"
        echo "]" >> "$LOG_FILE"
    fi

    echo "✓ Logged edit: $FILE_PATH ($LINES_CHANGED lines)"
fi
