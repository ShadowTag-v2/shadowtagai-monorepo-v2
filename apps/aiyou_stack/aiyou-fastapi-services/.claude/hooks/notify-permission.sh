#!/bin/bash
# Notification hook for permission_prompt - Handle permission request notifications

set -e

# Read the input JSON
INPUT=$(cat)

# Parse notification information
MESSAGE=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', ''))")
TYPE=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('notification_type', ''))")

# Only process permission_prompt notifications
if [ "$TYPE" != "permission_prompt" ]; then
    exit 0
fi

# Log permission requests
LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "[$TIMESTAMP] Permission Request: $MESSAGE" >> "$LOG_DIR/permissions.log"

# You could add desktop notifications here if running locally
# notify-send "Claude Permission Request" "$MESSAGE" 2>/dev/null || true

exit 0
