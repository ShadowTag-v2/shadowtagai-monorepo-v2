#!/bin/bash
#==============================================================================
# Thread Export Utility
#==============================================================================
# Captures clipboard content (from browser copy) and saves as timestamped file
#
# Usage:
#   1. Select all text in browser conversation (Cmd+A)
#   2. Copy (Cmd+C)
#   3. Run: ./scripts/export-thread.sh [optional-name]
#
# Output: transcripts/YYYY-MM-DD_HH-MM-SS_[name].txt
#==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
TRANSCRIPTS_DIR="$BASE_DIR/transcripts"

# Create transcripts directory if needed
mkdir -p "$TRANSCRIPTS_DIR"

# Generate filename
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
NAME="${1:-session}"
FILENAME="$TRANSCRIPTS_DIR/${TIMESTAMP}_${NAME}.txt"

# Export from clipboard
if command -v pbpaste &> /dev/null; then
    # macOS
    pbpaste > "$FILENAME"
elif command -v xclip &> /dev/null; then
    # Linux with xclip
    xclip -selection clipboard -o > "$FILENAME"
elif command -v xsel &> /dev/null; then
    # Linux with xsel
    xsel --clipboard --output > "$FILENAME"
else
    echo "ERROR: No clipboard utility found (pbpaste, xclip, or xsel)"
    exit 1
fi

# Verify file was created
if [ -s "$FILENAME" ]; then
    LINE_COUNT=$(wc -l < "$FILENAME")
    CHAR_COUNT=$(wc -c < "$FILENAME")
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  THREAD EXPORTED                                             ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║  File: $FILENAME"
    echo "║  Lines: $LINE_COUNT"
    echo "║  Size: $CHAR_COUNT bytes"
    echo "╚══════════════════════════════════════════════════════════════╝"
else
    echo "ERROR: Clipboard was empty or export failed"
    rm -f "$FILENAME"
    exit 1
fi
