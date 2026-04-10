#!/bin/bash
# Sync workspace archive to Google Drive (founder@shadowtagai.com)
# Uses rclone with gdrive-corp remote

set -e

RCLONE="/opt/homebrew/Cellar/rclone/1.72.1/bin/rclone"
LOCAL_DIR="/Users/pikeymickey/ShadowTag-v2-stack/workspace_archive"
REMOTE="gdrive-corp:workspace_archive"
LOG_FILE="$LOCAL_DIR/gdrive_sync.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Starting Google Drive sync ==="
log "Local: $LOCAL_DIR"
log "Remote: $REMOTE"

# Create remote folder if needed
$RCLONE mkdir "$REMOTE" 2>/dev/null || true

# Sync with progress
$RCLONE sync "$LOCAL_DIR" "$REMOTE" \
    --exclude ".git/**" \
    --exclude "*.log" \
    --exclude "__pycache__/**" \
    --exclude "*.pyc" \
    --progress \
    --stats-one-line \
    -v 2>&1 | tee -a "$LOG_FILE"

log "=== Google Drive sync complete ==="

# Show what's on Drive
log "Remote contents:"
$RCLONE lsd "$REMOTE" 2>&1 | tee -a "$LOG_FILE"
