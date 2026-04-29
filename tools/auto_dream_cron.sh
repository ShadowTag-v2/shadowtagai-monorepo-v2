#!/bin/bash
# ╔═══════════════════════════════════════════════╗
# ║  Auto-Dream — Nightly Memory Consolidation     ║
# ║  COR.KAIROS Protocol § Invariant #65               ║
# ║  Model: gemini-3.1-flash-lite-preview           ║
# ║  Project: shadowtag-omega-v4                    ║
# ╚═══════════════════════════════════════════════╝
#
# Called by com.pnkln.auto-dream launchd plist every 24h.
# Orient → Gather → Consolidate → Prune

set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/bin:/usr/sbin:/bin:/Users/pikeymickey/Library/Python/3.13/bin:/Users/pikeymickey/Library/Python/3.14/bin:$PATH"
export HOME="/Users/pikeymickey"

REPO="$HOME/.gemini/antigravity/Monorepo-Uphillsnowball"
BEADS="$REPO/.beads"
LOG="$REPO/auto-dream.log"
VAULT="${OBSIDIAN_VAULT_ROOT:-$HOME/Documents/Obsidian/ShadowTag-Vault}"
TODAY=$(date +%Y-%m-%d)

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] === AUTO-DREAM START ===" >> "$LOG"

# Phase 1: Orient — Check what sessions produced today
BRAIN_SESSIONS="$HOME/.gemini/antigravity/brain"
SESSION_COUNT=$(find "$BRAIN_SESSIONS" -name "task.md" -newer "$LOG" 2>/dev/null | wc -l | tr -d ' ')
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Orient: $SESSION_COUNT new sessions since last dream" >> "$LOG"

# Phase 2: Gather — Collect new .beads entries
if [ -d "$BEADS" ]; then
    BEAD_COUNT=$(wc -l < "$BEADS/issues.jsonl" 2>/dev/null || echo "0")
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Gather: $BEAD_COUNT beads in ledger" >> "$LOG"
fi

# Phase 3: Consolidate — Archive old brain sessions (>7 days)
ARCHIVED=0
if [ -d "$BRAIN_SESSIONS" ]; then
    for session_dir in "$BRAIN_SESSIONS"/*/; do
        [ -d "$session_dir" ] || continue
        session_name=$(basename "$session_dir")
        # Skip non-UUID directories
        [[ "$session_name" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]] || continue

        # Check age (7+ days old)
        if [ -f "$session_dir/task.md" ]; then
            age_days=$(( ($(date +%s) - $(stat -f %m "$session_dir/task.md" 2>/dev/null || echo $(date +%s))) / 86400 ))
            if [ "$age_days" -gt 7 ]; then
                ARCHIVED=$((ARCHIVED + 1))
            fi
        fi
    done
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Consolidate: $ARCHIVED sessions eligible for archival" >> "$LOG"
fi

# Phase 4: Prune — Remove temp files
PRUNED=0
for tmpfile in /tmp/pre-agent-*.md /tmp/session-summary-*.md; do
    if [ -f "$tmpfile" ]; then
        # Only prune if older than 2 days
        age_days=$(( ($(date +%s) - $(stat -f %m "$tmpfile" 2>/dev/null || echo $(date +%s))) / 86400 ))
        if [ "$age_days" -gt 2 ]; then
            rm -f "$tmpfile"
            PRUNED=$((PRUNED + 1))
        fi
    fi
done
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Prune: Removed $PRUNED temp files" >> "$LOG"

# Phase 5: Obsidian daily note check
if [ -d "$VAULT" ]; then
    DAILY="$VAULT/10-Daily/$TODAY.md"
    if [ ! -f "$DAILY" ]; then
        mkdir -p "$(dirname "$DAILY")"
        cat > "$DAILY" <<EOF
---
date: "$TODAY"
type: daily-note
tags: [daily, auto-dream]
---
# $TODAY

## Auto-Dream Consolidation
- Sessions: $SESSION_COUNT
- Beads: ${BEAD_COUNT:-0}
- Archived: $ARCHIVED
- Pruned: $PRUNED
EOF
        echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Created daily note: $DAILY" >> "$LOG"
    fi
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] === AUTO-DREAM COMPLETE ===" >> "$LOG"
