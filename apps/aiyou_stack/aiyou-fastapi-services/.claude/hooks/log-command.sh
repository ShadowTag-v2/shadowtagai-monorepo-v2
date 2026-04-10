#!/bin/bash
# PostToolUse hook for Bash - Log executed commands

set -e

# Read the input JSON
INPUT=$(cat)

# Parse tool information
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_name', ''))")
COMMAND=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))")
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', 'unknown'))")

# Only process Bash commands
if [ "$TOOL_NAME" != "Bash" ]; then
    exit 0
fi

# Skip if no command
if [ -z "$COMMAND" ]; then
    exit 0
fi

# Create logs directory if it doesn't exist
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

# Log file path
LOG_FILE="$LOG_DIR/commands.log"

# Append to log with timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[$TIMESTAMP] [Session: ${SESSION_ID:0:8}] $COMMAND" >> "$LOG_FILE"

# Keep only last 1000 lines to prevent log from growing too large
tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"

exit 0
