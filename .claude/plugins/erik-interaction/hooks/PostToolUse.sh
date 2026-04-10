#!/bin/bash
# Hook: PostToolUse
# Update context after tool execution

TOOL_NAME="$1"
TOOL_OUTPUT="$2"

# Update session memory with new information
python3 .claude/plugins/erik-interaction/scripts/memory-updater.py \
  --tool "$TOOL_NAME" \
  --output "$TOOL_OUTPUT"

exit 0
