#!/bin/bash
# Verify all backup locations are in sync
# Run weekly to ensure nothing is lost

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Backup Verification ==="
echo ""

# Check 1: Local archive database
echo "[1/5] Local Archive Database"
if [ -f "$HOME/.consensus_archive.db" ]; then
    SIZE=$(ls -lh "$HOME/.consensus_archive.db" | awk '{print $5}')
    MODIFIED=$(ls -l "$HOME/.consensus_archive.db" | awk '{print $6, $7, $8}')
    echo "  ✓ Found: ~/.consensus_archive.db"
    echo "    Size: $SIZE"
    echo "    Modified: $MODIFIED"
else
    echo "  ✗ NOT FOUND: ~/.consensus_archive.db"
    echo "    This is your primary archive! Create it by running queries."
fi
echo ""

# Check 2: Local git repository
echo "[2/5] Local Git Repository"
cd "$REPO_DIR"
if [ -d ".git" ]; then
    LAST_COMMIT=$(git log -1 --format="%h - %s (%cr)")
    BRANCH=$(git branch --show-current)
    echo "  ✓ Git repository active"
    echo "    Branch: $BRANCH"
    echo "    Last commit: $LAST_COMMIT"

    # Check if we're ahead of remote
    git fetch origin -q 2>/dev/null
    AHEAD=$(git rev-list --count origin/$BRANCH..$BRANCH 2>/dev/null || echo "0")
    if [ "$AHEAD" -gt "0" ]; then
        echo "    ⚠️  $AHEAD commit(s) not pushed to GitHub"
        echo "       Run: git push"
    else
        echo "    ✓ In sync with GitHub"
    fi
else
    echo "  ✗ NOT FOUND: Git repository"
fi
echo ""

# Check 3: GitHub remote
echo "[3/5] GitHub Remote"
cd "$REPO_DIR"
if git remote -v | grep -q "github.com\|local_proxy"; then
    REMOTE_URL=$(git remote get-url origin)
    echo "  ✓ GitHub remote configured"
    echo "    URL: $REMOTE_URL"

    # Try to fetch to verify connection
    if git fetch origin -q 2>/dev/null; then
        REMOTE_COMMIT=$(git log origin/$(git branch --show-current) -1 --format="%h - %s (%cr)" 2>/dev/null)
        echo "    ✓ Connection successful"
        echo "    Remote: $REMOTE_COMMIT"
    else
        echo "    ⚠️  Cannot connect to GitHub (check internet)"
    fi
else
    echo "  ✗ GitHub remote not configured"
fi
echo ""

# Check 4: Dropbox backup
echo "[4/5] Dropbox Backup"
if [ -d "$HOME/Dropbox" ]; then
    LATEST_DB=$(ls -t "$HOME/Dropbox"/consensus_backup_*.db 2>/dev/null | head -1)
    if [ -n "$LATEST_DB" ]; then
        SIZE=$(ls -lh "$LATEST_DB" | awk '{print $5}')
        MODIFIED=$(ls -l "$LATEST_DB" | awk '{print $6, $7, $8}')
        FILENAME=$(basename "$LATEST_DB")
        echo "  ✓ Found: $FILENAME"
        echo "    Size: $SIZE"
        echo "    Modified: $MODIFIED"

        # Check if it's recent (within 7 days)
        AGE=$(( ($(date +%s) - $(stat -f %m "$LATEST_DB" 2>/dev/null || stat -c %Y "$LATEST_DB")) / 86400 ))
        if [ "$AGE" -gt 7 ]; then
            echo "    ⚠️  Backup is $AGE days old. Run backup_consensus.sh"
        else
            echo "    ✓ Backup is recent ($AGE days old)"
        fi
    else
        echo "  ⚠️  No backups found in ~/Dropbox/"
        echo "     Run: cp ~/.consensus_archive.db ~/Dropbox/consensus_backup_$(date +%Y%m%d).db"
    fi
else
    echo "  ⚠️  Dropbox folder not found at ~/Dropbox"
    echo "     Install Dropbox or use alternative cloud storage"
fi
echo ""

# Check 5: Archive exports
echo "[5/5] Archive Exports (Markdown/JSON)"
cd "$SCRIPT_DIR"
if [ -d "archives" ]; then
    MD_COUNT=$(find archives -name "daily_*.md" 2>/dev/null | wc -l | tr -d ' ')
    JSON_COUNT=$(find archives -name "cost_report_*.json" 2>/dev/null | wc -l | tr -d ' ')
    LATEST_MD=$(find archives -name "daily_*.md" 2>/dev/null | sort | tail -1)

    echo "  ✓ Found archives directory"
    echo "    Markdown exports: $MD_COUNT files"
    echo "    JSON cost reports: $JSON_COUNT files"
    if [ -n "$LATEST_MD" ]; then
        echo "    Latest export: $(basename "$LATEST_MD")"
    fi

    # Check if exports are recent
    if [ -n "$LATEST_MD" ]; then
        AGE=$(( ($(date +%s) - $(stat -f %m "$LATEST_MD" 2>/dev/null || stat -c %Y "$LATEST_MD")) / 86400 ))
        if [ "$AGE" -gt 7 ]; then
            echo "    ⚠️  Latest export is $AGE days old"
            echo "       Run: ./backup_consensus.sh"
        else
            echo "    ✓ Exports are recent ($AGE days old)"
        fi
    fi
else
    echo "  ⚠️  No archives directory found"
    echo "     Will be created on first backup"
fi

echo ""
echo "=== Summary ==="
echo ""

# Count issues
ISSUES=0
[ ! -f "$HOME/.consensus_archive.db" ] && ((ISSUES++))
[ ! -d "$REPO_DIR/.git" ] && ((ISSUES++))
[ ! -d "$HOME/Dropbox" ] || [ -z "$(ls -t "$HOME/Dropbox"/consensus_backup_*.db 2>/dev/null | head -1)" ] && ((ISSUES++))

if [ "$ISSUES" -eq 0 ]; then
    echo "✓ All backups verified!"
    echo ""
    echo "Your work is safe in 3 locations:"
    echo "  1. Local database (~/.consensus_archive.db)"
    echo "  2. Git repository (local + GitHub)"
    echo "  3. Dropbox backup"
    echo ""
    echo "Next steps:"
    echo "  - Run queries: python message_consensus.py 'your question'"
    echo "  - Daily backup: ./backup_consensus.sh"
    echo "  - Weekly verify: ./verify_backups.sh"
else
    echo "⚠️  Found $ISSUES issue(s)"
    echo ""
    echo "Recommendations:"
    if [ ! -f "$HOME/.consensus_archive.db" ]; then
        echo "  - Start using consensus: cd voice_consensus && python message_consensus.py 'test'"
    fi
    if [ ! -d "$HOME/Dropbox" ]; then
        echo "  - Install Dropbox or set up alternative cloud backup"
    fi
    echo "  - Run: ./backup_consensus.sh to sync everything"
fi

echo ""
