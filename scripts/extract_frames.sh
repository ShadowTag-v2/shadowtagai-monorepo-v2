#!/bin/bash
# extract_frames.sh — Hardware/Software Egress Bridge
# Bridges the browser's async filesystem to the monorepo workspace.
# Usage: ./scripts/extract_frames.sh <output_video_path> <frames_output_dir> [fps]
set -e

VIDEO_FILE="${1:?Usage: extract_frames.sh <video_path> <output_dir> [fps]}"
OUTPUT_DIR="${2:?Usage: extract_frames.sh <video_path> <output_dir> [fps]}"
FPS="${3:-30}"

# 1. Asynchronous Egress Guardrail — wait for Chrome download completion
echo "[extract_frames] Awaiting cryptographic completion of Chrome download..."
TIMEOUT=120
ELAPSED=0
while ls ~/Downloads/*.crdownload 1>/dev/null 2>&1; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "[extract_frames] ERROR: Download timeout after ${TIMEOUT}s"
        exit 1
    fi
done

# 2. Pipeline Relocation — grab the newest video
LATEST_VIDEO=$(ls -t ~/Downloads/*.mp4 2>/dev/null | head -n 1)
if [ -z "$LATEST_VIDEO" ]; then
    echo "[extract_frames] ERROR: No .mp4 found in ~/Downloads/"
    exit 1
fi

mkdir -p "$(dirname "$VIDEO_FILE")"
mv "$LATEST_VIDEO" "$VIDEO_FILE"
echo "[extract_frames] Relocated: $LATEST_VIDEO → $VIDEO_FILE"

# 3. Clean and Extract frames via ffmpeg
mkdir -p "$OUTPUT_DIR"
# Only clean png frames, not other files
find "$OUTPUT_DIR" -name 'frame_*.png' -delete 2>/dev/null || true

ffmpeg -i "$VIDEO_FILE" -vf "fps=$FPS" "$OUTPUT_DIR/frame_%04d.png" -hide_banner -loglevel error
FRAME_COUNT=$(find "$OUTPUT_DIR" -name 'frame_*.png' | wc -l | tr -d ' ')
echo "[extract_frames] Total frames extracted: $FRAME_COUNT"

# 4. Autonomous Code Patching — inject FRAME_COUNT into UI codebase
for TARGET_FILE in \
    "apps/kovelai/src/GavelHero.tsx" \
    "apps/kovelai/public/chassis-preview.html"; do
    if [ -f "$TARGET_FILE" ]; then
        sed -i.bak "s/const FRAME_COUNT = [0-9]*/const FRAME_COUNT = $FRAME_COUNT/g" "$TARGET_FILE"
        echo "[extract_frames] Patched FRAME_COUNT=$FRAME_COUNT in $TARGET_FILE"
    fi
done

echo "[extract_frames] Synchronization complete."
