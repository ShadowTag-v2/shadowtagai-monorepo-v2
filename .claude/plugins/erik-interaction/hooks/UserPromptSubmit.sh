#!/bin/bash
# Hook: UserPromptSubmit
# Runs before processing Erik's question

SESSION_ID="$1"
USER_INPUT="$2"

# Extract context from past conversations if needed
# This would call into a Python script that does the actual search

python3 .claude/plugins/erik-interaction/scripts/context-loader.py \
  --session-id "$SESSION_ID" \
  --input "$USER_INPUT"

# Exit code 0 = continue
# Echo additional context to stdout to inject into prompt
