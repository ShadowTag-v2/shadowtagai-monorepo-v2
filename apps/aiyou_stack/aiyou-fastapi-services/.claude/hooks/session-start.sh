#!/bin/bash
# SessionStart hook - Initialize environment and provide context

set -e

# Read the input JSON
INPUT=$(cat)

# Parse session info
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', 'unknown'))")
SOURCE=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('source', 'unknown'))")

# Initialize environment variables if CLAUDE_ENV_FILE is available
if [ -n "$CLAUDE_ENV_FILE" ]; then
  # Set up Node.js environment
  if [ -f "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
    # Capture environment before and after nvm use
    ENV_BEFORE=$(export -p | sort)
    nvm use --silent 2>/dev/null || true
    ENV_AFTER=$(export -p | sort)
    comm -13 <(echo "$ENV_BEFORE") <(echo "$ENV_AFTER") >> "$CLAUDE_ENV_FILE"
  fi

  # Set project-specific environment variables
  echo 'export PROJECT_NAME="ShadowTag-v2-fastapi-services"' >> "$CLAUDE_ENV_FILE"
  echo 'export NODE_ENV="development"' >> "$CLAUDE_ENV_FILE"

  # Add node_modules/.bin to PATH
  if [ -d "$CLAUDE_PROJECT_DIR/node_modules/.bin" ]; then
    echo "export PATH=\"\$PATH:$CLAUDE_PROJECT_DIR/node_modules/.bin\"" >> "$CLAUDE_ENV_FILE"
  fi
fi

# Provide context to Claude
cat <<EOF
Session started: $SOURCE (ID: $SESSION_ID)

Project: ShadowTag-v2-fastapi-services - Claude Agent SDK Migration Project

## Project Context
This project has been migrated from Claude Code SDK to Claude Agent SDK.

## Available Packages
- @anthropic-ai/claude-agent-sdk (npm): 0.1.30
- claude-agent-sdk (pip): 0.1.6

## Key Information
- Migration completed: 2025-11-07
- No existing source code files yet
- Ready for development with Claude Agent SDK

## Hooks Enabled
- SessionStart: Environment setup and context injection
- UserPromptSubmit: Prompt validation and context
- PreToolUse: Bash command and file operation validation
- PostToolUse: Code formatting and command logging
- Stop: Intelligent stop decision with LLM
- Notification: Permission request notifications

Use the hooks reference in .claude/HOOKS.md for details.
EOF

exit 0
