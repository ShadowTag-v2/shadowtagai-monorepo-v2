#!/bin/bash
set -euo pipefail

# HeadFade Frame Extraction Script
# Usage: ./extract_frames_headfade.sh <input_video> <output_folder> <frame_rate>

INPUT_VIDEO=${1:-"external_payloads/headfade/veo_output/gavel_descent.mp4"}
OUTPUT_DIR=${2:-"apps/headfade/public/frames"}
FRAME_RATE=${3:-30}

echo "🎬 [HeadFade] Starting frame extraction..."
echo "Input: $INPUT_VIDEO"
echo "Output: $OUTPUT_DIR"
echo "Frame Rate: $FRAME_RATE fps"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Extract frames using ffmpeg
ffmpeg -i "$INPUT_VIDEO" -vf "fps=$FRAME_RATE" -q:v 2 "$OUTPUT_DIR/frame_%04d.png"

# Count extracted frames
FRAME_COUNT=$(ls -1 "$OUTPUT_DIR"/*.png 2>/dev/null | wc -l)

echo "✅ [HeadFade] Extraction complete."
echo "📊 Total frames extracted: $FRAME_COUNT"

# Output frame count for use in scripts
echo "$FRAME_COUNT" > "$OUTPUT_DIR/frame_count.txt"

echo "🎉 [HeadFade] Pipeline step completed successfully."