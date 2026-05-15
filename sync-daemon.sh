#!/bin/bash
# ╔═══════════════════════════════════════════════╗
# ║  Git Sync Daemon — Antigravity Monorepo       ║
# ║  Model: gemini-3.1-flash-lite-preview          ║
# ║  Project: shadowtag-omega-v4                   ║
# ╚═══════════════════════════════════════════════╝
#
# Called by com.antigravity.gitsync launchd plist every 5 minutes.
# Performs a safe, non-destructive sync of the monorepo.

set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/bin:/usr/sbin:/bin:$PATH"
export HOME="/Users/pikeymickey"

REPO="$HOME/.gemini/antigravity/Monorepo-Uphillsnowball"
LOG="$REPO/launchd-sync.log"
LOCKFILE="/tmp/antigravity-gitsync.lock"
PEM="$HOME/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
APP_ID="3018200"

# Prevent concurrent runs
if [ -f "$LOCKFILE" ]; then
    pid=$(cat "$LOCKFILE" 2>/dev/null)
    if kill -0 "$pid" 2>/dev/null; then
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] SKIP: Already running (PID $pid)" >> "$LOG"
        exit 0
    fi
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

cd "$REPO" || {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] FATAL: Repo directory missing" >> "$LOG"
    exit 1
}

# Check for uncommitted changes
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] INFO: Uncommitted changes detected — skipping sync" >> "$LOG"
    exit 0
fi

# Fetch latest (non-destructive)
git fetch origin --prune 2>/dev/null && {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK: Fetch complete" >> "$LOG"
} || {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARN: Fetch failed (network?)" >> "$LOG"
    exit 0
}

# Check divergence
LOCAL=$(git rev-parse HEAD 2>/dev/null)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "unknown")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK: In sync ($LOCAL)" >> "$LOG"
else
    BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
    AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] INFO: Diverged — $AHEAD ahead, $BEHIND behind" >> "$LOG"
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] DONE" >> "$LOG"
