#!/bin/bash
set -euo pipefail

# KovelAI Frame Extraction Script
# Usage: ./extract_frames_kovelai.sh <input_video> <output_folder> <frame_rate>

INPUT_VIDEO=${1:-"labs/uphillsnowball/external_payloads/veo_output/hero_gavel.mp4"}
OUTPUT_DIR=${2:-"apps/kovelai/public/frames"}
FRAME_RATE=${3:-30}

echo "🎬 [KovelAI] Starting frame extraction..."
echo "Input: $INPUT_VIDEO"
echo "Output: $OUTPUT_DIR"
echo "Frame Rate: $FRAME_RATE fps"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Extract frames using ffmpeg
ffmpeg -i "$INPUT_VIDEO" -vf "fps=$FRAME_RATE" -q:v 2 "$OUTPUT_DIR/frame_%04d.png"

# Count extracted frames
FRAME_COUNT=$(ls -1 "$OUTPUT_DIR"/*.png 2>/dev/null | wc -l)

echo "✅ [KovelAI] Extraction complete."
echo "📊 Total frames extracted: $FRAME_COUNT"

# Output frame count for use in scripts
echo "$FRAME_COUNT" > "$OUTPUT_DIR/frame_count.txt"

echo "🎉 [KovelAI] Pipeline step completed successfully."