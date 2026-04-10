#!/bin/bash
# Setup automated memory sync cron job

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_memory.sh"
LOG_FILE="$HOME/.consensus_sync.log"

echo "================================"
echo "CRON JOB SETUP"
echo "================================"
echo ""
echo "This will setup a daily cron job to:"
echo "  - Extract patterns from consensus archive"
echo "  - Sync personal memory to GitHub"
echo "  - Sync team memory to GCS"
echo "  - Update Kubernetes ConfigMap"
echo ""
echo "Schedule: Daily at 8:00 PM"
echo "Script: $SYNC_SCRIPT"
echo "Logs: $LOG_FILE"
echo ""

# Check if sync script exists
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo "Error: Sync script not found: $SYNC_SCRIPT"
    exit 1
fi

# Make sync script executable
chmod +x "$SYNC_SCRIPT"

# Create cron entry
CRON_ENTRY="0 20 * * * cd $SCRIPT_DIR && $SYNC_SCRIPT >> $LOG_FILE 2>&1"

# Check if cron entry already exists
if crontab -l 2>/dev/null | grep -q "sync_memory.sh"; then
    echo "Cron job already exists. Replacing..."
    crontab -l 2>/dev/null | grep -v "sync_memory.sh" | crontab -
fi

# Add new cron entry
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✓ Cron job installed"
echo ""
echo "Current cron jobs:"
crontab -l
echo ""
echo "================================"
echo "SETUP COMPLETE"
echo "================================"
echo ""
echo "The memory sync will run daily at 8:00 PM."
echo ""
echo "Manual sync:"
echo "  $SYNC_SCRIPT"
echo ""
echo "View logs:"
echo "  tail -f $LOG_FILE"
echo ""
echo "Remove cron job:"
echo "  crontab -l | grep -v sync_memory.sh | crontab -"
echo ""
