#!/bin/bash
# Automated consensus archive backup to GitHub
# Run this daily or after each research session

set -e

DATE=$(date +%Y%m%d)
MONTH=$(date +%Y_%m)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
ARCHIVE_DIR="$SCRIPT_DIR/archives/$MONTH"

echo "=== Consensus Archive Backup - $DATE ==="
echo ""

# Create monthly archive directory
mkdir -p "$ARCHIVE_DIR"

# Navigate to voice_consensus directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Export today's transcripts to markdown
echo "[1/4] Exporting daily transcripts..."
python transcript_archive.py export "$ARCHIVE_DIR/daily_$DATE.md" 2>/dev/null || echo "  No new transcripts to export"

# Export cost report
echo "[2/4] Exporting cost report..."
python cost_tracker.py export "$ARCHIVE_DIR/cost_report_$DATE.json" --days 30 2>/dev/null || echo "  No cost data to export"

# Backup the SQLite database to Dropbox (if Dropbox folder exists)
if [ -d "$HOME/Dropbox" ]; then
    echo "[3/4] Backing up database to Dropbox..."
    cp ~/.consensus_archive.db "$HOME/Dropbox/consensus_backup_$DATE.db" 2>/dev/null || echo "  Database backup skipped"
else
    echo "[3/4] Skipping Dropbox backup (folder not found)"
fi

# Commit to git
echo "[4/4] Committing to git..."
cd "$REPO_DIR"

git add voice_consensus/archives/
git commit -m "Auto-backup: Archives and cost report $DATE" 2>/dev/null || {
    echo "  Nothing new to commit"
}

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push 2>/dev/null && {
    echo ""
    echo "✓ Backup complete!"
    echo ""
    echo "Backed up to:"
    echo "  - GitHub: https://github.com/ShadowTag-v2/ShadowTag-v2-fastapi-services"
    echo "  - Local exports: $ARCHIVE_DIR/"
    if [ -d "$HOME/Dropbox" ]; then
        echo "  - Dropbox: ~/Dropbox/consensus_backup_$DATE.db"
    fi
    echo ""
} || {
    echo ""
    echo "⚠️  Git push failed. Check your connection."
    echo "   Local backups are still saved."
    echo ""
}

# Show quick stats
echo "Archive Stats:"
python transcript_archive.py stats 2>/dev/null | grep -E "Total|Cost" || echo "  (Stats unavailable)"

echo ""
echo "=== Backup Complete ==="
