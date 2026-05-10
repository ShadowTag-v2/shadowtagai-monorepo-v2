#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title GCA Pruner
# @raycast.mode fullOutput
# @raycast.packageName Monorepo Tools

# Optional parameters:
# @raycast.icon 🧹
# @raycast.argument1 { "type": "dropdown", "placeholder": "Mode", "data": [{"title": "Dry Run", "value": "dry"}, {"title": "Write (Prune)", "value": "write"}] }

SCRIPT="$HOME/.gemini/antigravity/Monorepo-Uphillsnowball/scripts/prune_gca_chat_threads.py"

if [ "$1" = "write" ]; then
    echo "🔴 WRITE MODE — pruning GCA chatThreads..."
    python3 "$SCRIPT" --write
else
    echo "🔍 DRY RUN — inspecting GCA state..."
    python3 "$SCRIPT"
fi
