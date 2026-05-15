#!/bin/bash
set -euo pipefail

# Universal Frame Extraction Script
# Usage: ./extract_frames_universal.sh <project> <input_video> <output_folder> <frame_rate>

PROJECT=${1:-"headfade"}
INPUT_VIDEO=${2}
OUTPUT_DIR=${3}
FRAME_RATE=${4:-30}

if [ -z "$INPUT_VIDEO" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <project> <input_video> <output_folder> [frame_rate]"
    echo "Example: $0 headfade external_payloads/headfade/veo_output/gavel_descent.mp4 apps/headfade/public/frames 30"
    exit 1
fi

echo "🎬 [Universal] Starting frame extraction for project: $PROJECT"
echo "Input: $INPUT_VIDEO"
echo "Output: $OUTPUT_DIR"
echo "Frame Rate: $FRAME_RATE fps"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Extract frames
ffmpeg -i "$INPUT_VIDEO" -vf "fps=$FRAME_RATE" -q:v 2 "$OUTPUT_DIR/frame_%04d.png"

# Count frames
FRAME_COUNT=$(ls -1 "$OUTPUT_DIR"/*.png 2>/dev/null | wc -l)

echo "✅ [Universal] Extraction complete for $PROJECT."
echo "📊 Total frames: $FRAME_COUNT"

# Save frame count
echo "$FRAME_COUNT" > "$OUTPUT_DIR/frame_count.txt"

# Project-specific post-processing
if [ "$PROJECT" = "headfade" ]; then
    echo "🔄 Updating HeadFade components..."
    # Add any HeadFade-specific updates here
elif [ "$PROJECT" = "kovelai" ]; then
    echo "🔄 Updating KovelAI components..."
    # Add any KovelAI-specific updates here
fi

echo "🎉 [Universal] Pipeline step completed for $PROJECT."
```