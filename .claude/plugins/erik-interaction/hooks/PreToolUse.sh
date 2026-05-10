#!/bin/bash
# Hook: PreToolUse
# Validate against JR constraints before executing tools

TOOL_NAME="$1"
TOOL_INPUT="$2"

# Run JR validation
python3 .claude/plugins/erik-interaction/scripts/jr-validator.py \
  --tool "$TOOL_NAME" \
  --input "$TOOL_INPUT"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  # JR compliant
  echo '{"decision": "approve"}'
  exit 0
elif [ $EXIT_CODE -eq 1 ]; then
  # JR violation detected
  echo '{"decision": "block", "reason": "JR constraint violation detected"}'
  exit 1
else
  # Validation error
  echo '{"decision": "ask", "reason": "Unable to validate JR compliance"}'
  exit 2
fi
