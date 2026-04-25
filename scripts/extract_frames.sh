#!/usr/bin/env bash
# extract_frames.sh — Extracts video frames for scroll-driven canvas animation
# Per veo3-flow-cinematic SKILL.md: direct <video> playback on scroll is choppy.
# Frame-sequence + canvas + requestAnimationFrame = Apple-style smoothness.
#
# Usage:
#   ./scripts/extract_frames.sh path/to/hero.mp4 [output_dir] [fps]
#
# Defaults:
#   output_dir = labs/uphillsnowball/external_payloads/veo_output/frames
#   fps        = 30

set -euo pipefail

INPUT="${1:?Usage: extract_frames.sh <input.mp4> [output_dir] [fps]}"
OUTPUT_DIR="${2:-labs/uphillsnowball/external_payloads/veo_output/frames}"
FPS="${3:-30}"

if ! command -v ffmpeg &>/dev/null; then
  echo "ERROR: ffmpeg not found. Install via: brew install ffmpeg" >&2
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"

echo "━━━ Frame Extraction ━━━"
echo "  Input:  ${INPUT}"
echo "  Output: ${OUTPUT_DIR}"
echo "  FPS:    ${FPS}"

# Extract frames with quality control
# -q:v 2 = near-lossless JPEG quality
# scale=1920:-1 = normalize to 1920px wide, maintain aspect ratio
ffmpeg -i "${INPUT}" \
  -vf "fps=${FPS},scale=1920:-1" \
  -q:v 2 \
  "${OUTPUT_DIR}/frame_%04d.jpg" \
  -y 2>&1

FRAME_COUNT=$(find "${OUTPUT_DIR}" -name "frame_*.jpg" | wc -l | tr -d ' ')
echo ""
echo "✅ Extracted ${FRAME_COUNT} frames to ${OUTPUT_DIR}/"
echo "   Duration: ~$(echo "scale=1; ${FRAME_COUNT} / ${FPS}" | bc)s at ${FPS}fps"
