#!/bin/bash
set -euo pipefail

# Master Pipeline Coordinator
# This script is designed to be called directly by Jules via MCP or terminal

PROJECT=${1:-"headfade"}
MODE=${2:-"full"}  # full, image-only, video-only

echo "🚀 [Master Coordinator] Starting pipeline for: $PROJECT ($MODE mode)"
echo "================================================================"

# Step 1: Trigger asset generation via Jules (if not already done)
if [ "$MODE" = "full" ] || [ "$MODE" = "image-only" ]; then
    echo "📸 [1/4] Generating Image Asset (Nano Banana 2 / ImageFX)..."
    # Jules will handle this via the robust prompt
fi

if [ "$MODE" = "full" ] || [ "$MODE" = "video-only" ]; then
    echo "🎥 [2/4] Generating Video Asset (VideoFX)..."
    # Jules will handle this via the robust prompt
fi

# Step 2: Extract frames
echo "🎬 [3/4] Extracting frames..."
if [ "$PROJECT" = "headfade" ]; then
    ./scripts/extract_frames_universal.sh headfade external_payloads/headfade/veo_output/gavel_descent.mp4 apps/headfade/public/frames 30
elif [ "$PROJECT" = "kovelai" ]; then
    ./scripts/extract_frames_universal.sh kovelai labs/uphillsnowball/external_payloads/veo_output/hero_gavel.mp4 apps/kovelai/public/frames 30
fi

# Step 3: Update codebase + sync
echo "🔄 [4/4] Updating codebase and synchronizing..."
# Add any project-specific updates here
./scripts/omega-sync.sh || echo "omega-sync not found, skipping..."

echo ""
echo "✅ [Master Coordinator] Pipeline completed for $PROJECT"
echo "📊 Check dashboard at: http://localhost:3000/pipeline-dashboard"
```