#!/bin/bash
# FFmpeg Screen Recording Demo — CounselConduit
# Records a 15s screen capture with system audio (macOS)
# Output: demo_recording.mp4 (H.264, 1080p, AAC audio)

set -euo pipefail

OUTPUT="${1:-demo_recording.mp4}"
DURATION="${2:-15}"

echo "📹 Starting screen recording for ${DURATION}s..."
echo "   Output: $OUTPUT"

# macOS screen capture (avfoundation, screen index 0, no audio)
ffmpeg -y \
  -f avfoundation \
  -framerate 30 \
  -i "1:none" \
  -t "$DURATION" \
  -c:v libx264 \
  -preset fast \
  -crf 23 \
  -pix_fmt yuv420p \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  "$OUTPUT" 2>&1

echo ""
echo "✅ Recording saved: $OUTPUT"
echo "   Size: $(du -sh "$OUTPUT" | cut -f1)"
echo "   Duration: ${DURATION}s"

# Generate thumbnail
ffmpeg -y -i "$OUTPUT" -vframes 1 -q:v 2 "${OUTPUT%.mp4}_thumb.jpg" 2>/dev/null
echo "   Thumbnail: ${OUTPUT%.mp4}_thumb.jpg"
