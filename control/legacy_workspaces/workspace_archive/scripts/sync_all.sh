#!/bin/bash
# Workspace Archive Sync Script
# Syncs all workspace sources to git, strips secrets, pushes to GitHub

set -e

ARCHIVE_DIR="/Users/pikeymickey/aiyou-stack/workspace_archive"
REPO="ehanc69/chatgpt-archive"
LOG_FILE="$ARCHIVE_DIR/sync.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Secret patterns to strip
SECRET_PATTERNS=(
    'ghp_[a-zA-Z0-9]{36}'           # GitHub PAT
    'gho_[a-zA-Z0-9]{36}'           # GitHub OAuth
    'sk-[a-zA-Z0-9]{48}'            # OpenAI API key
    'AKIA[A-Z0-9]{16}'              # AWS Access Key
    'AIza[a-zA-Z0-9_-]{35}'         # Google API Key
    'xox[baprs]-[a-zA-Z0-9-]+'      # Slack tokens
    'anthropic-[a-zA-Z0-9-]+'       # Anthropic keys
)

strip_secrets() {
    local file="$1"
    for pattern in "${SECRET_PATTERNS[@]}"; do
        sed -i '' -E "s/$pattern/[REDACTED]/g" "$file" 2>/dev/null || true
    done
}

log "=== Starting workspace sync ==="

# 1. Sync iCloud Notes (already in ShadowTag-v2)
log "Syncing iCloud Notes..."
if [ -d "/Users/pikeymickey/aiyou-stack/ShadowTag-v2/docs/icloud_notes_imported" ]; then
    rsync -av --delete "/Users/pikeymickey/aiyou-stack/ShadowTag-v2/docs/icloud_notes_imported/" "$ARCHIVE_DIR/icloud_notes/"
    log "  - iCloud Notes: $(ls -1 "$ARCHIVE_DIR/icloud_notes/" 2>/dev/null | wc -l | tr -d ' ') files"
fi

# 2. Sync Claude CLI history
log "Syncing Claude CLI history..."
if [ -d "/Users/pikeymickey/.claude/projects_imported" ]; then
    rsync -av "/Users/pikeymickey/.claude/projects_imported/" "$ARCHIVE_DIR/claude_cli/"
    log "  - Claude CLI: $(ls -1 "$ARCHIVE_DIR/claude_cli/" 2>/dev/null | wc -l | tr -d ' ') sessions"
fi

# 3. Sync ChatGPT exports
log "Syncing ChatGPT exports..."
if [ -d "/Users/pikeymickey/Downloads/ChatGPT data" ]; then
    rsync -av "/Users/pikeymickey/Downloads/ChatGPT data/" "$ARCHIVE_DIR/chatgpt/"
    log "  - ChatGPT: synced"
fi

# 4. Sync Antigravity/Google Drive extracts
log "Syncing Google Drive extracts..."
if [ -d "/Users/pikeymickey/aiyou-stack/ShadowTag-v2/extracted/antigravity_brain" ]; then
    rsync -av "/Users/pikeymickey/aiyou-stack/ShadowTag-v2/extracted/antigravity_brain/" "$ARCHIVE_DIR/google_drive/antigravity_brain/"
    log "  - Antigravity brain: synced"
fi

# 5. Sync local code summaries
log "Creating local code index..."
find /Users/pikeymickey/aiyou-stack -maxdepth 2 -type d -name ".git" 2>/dev/null | \
    sed 's/\/.git$//' | \
    while read repo; do
        echo "$(basename "$repo"): $repo"
    done > "$ARCHIVE_DIR/local_code/repo_index.txt"
log "  - Local repos indexed"

# 6. Strip secrets from all text files
log "Stripping secrets..."
find "$ARCHIVE_DIR" -type f \( -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.py" -o -name "*.yaml" -o -name "*.yml" \) | while read file; do
    strip_secrets "$file"
done
log "  - Secrets stripped"

# 7. Git commit and push
log "Committing to git..."
cd "$ARCHIVE_DIR"
git add -A
if git diff --cached --quiet; then
    log "  - No changes to commit"
else
    git commit -m "Workspace sync: $(date '+%Y-%m-%d %H:%M')" \
        -m "Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
    git push origin main
    log "  - Pushed to GitHub"
fi

log "=== Sync complete ==="
