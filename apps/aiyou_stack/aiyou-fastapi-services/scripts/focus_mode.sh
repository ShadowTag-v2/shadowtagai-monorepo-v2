#!/bin/bash
# Focus Mode: Replicate Google's "CitC" Sparse Checkout behavior
# Usage: ./scripts/focus_mode.sh <path_to_focus_on>

set -e

FOCUS_PATH=$1

if [ -z "$FOCUS_PATH" ]; then
    echo "Usage: $0 <path_to_focus_on>"
    echo "Example: $0 src/autoresearch"
    echo "To reset (view all): $0 all"
    exit 1
fi

if [ "$FOCUS_PATH" == "all" ]; then
    echo "🌍 Disabling Focus Mode (Expanding View)..."
    git sparse-checkout disable
    echo "✅ View Expanded. You can see the whole world."
    exit 0
fi

echo "🔭 Engaging Focus Mode on: $FOCUS_PATH"
# Initialize if not already
git sparse-checkout init --cone

# Set the focus
git sparse-checkout set "$FOCUS_PATH" Docs tools scripts
echo "✅ Focus Locked. You only see: $FOCUS_PATH (plus Docs, tools, scripts)"
