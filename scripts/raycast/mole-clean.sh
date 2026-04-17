#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Mole System Clean
# @raycast.mode fullOutput
# @raycast.packageName Monorepo Tools

# Optional parameters:
# @raycast.icon 🧹
# @raycast.argument1 { "type": "dropdown", "placeholder": "Mode", "data": [{"title": "Dry Run", "value": "dry"}, {"title": "Clean", "value": "clean"}, {"title": "Status", "value": "status"}] }

case "$1" in
    clean)
        echo "🔴 Running mo clean..."
        /opt/homebrew/bin/mo clean
        ;;
    status)
        echo "📊 System health status..."
        /opt/homebrew/bin/mo status
        ;;
    *)
        echo "🔍 Dry run preview..."
        /opt/homebrew/bin/mo clean --dry-run
        ;;
esac
