#!/usr/bin/env bash

# cleanup-cinematic-videos.sh
# Purges watermarked and non-watermarked play-through traces left by Judge-6
ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

find "$ROOT/test-results" -name "*.mp4" -delete 2>/dev/null
find "$ROOT/playwright-report" -name "*.mp4" -delete 2>/dev/null

echo "Cinematic traces purged successfully."
