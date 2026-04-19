#!/usr/bin/env bash
# chunked_force_push.sh — Resilient force push after BFG history rewrite
#
# Pushes commits in sequential 3-batch waves, each batch targeting ~100MB.
# After each wave completes, it regenerates the GitHub App installation
# token to avoid expiry on long operations.
#
# Usage: bash scripts/chunked_force_push.sh [BATCH_SIZE] [REMOTE] [BRANCH]
#   BATCH_SIZE: Number of commits per batch (default: 30)
#   REMOTE:     Git remote (default: origin)
#   BRANCH:     Branch to push (default: main)
#
# Recovery:
#   If a batch crashes, the script saves state to a file.
#   Re-run the same command to resume from the last successful batch.
#
# Architecture:
#   ┌──────────────────────────────────────────────────────────┐
#   │  WAVE 1: Batches 1–3                                     │
#   │    Batch 1: commits 1-30   → push temp ref → delete ref  │
#   │    Batch 2: commits 31-60  → push temp ref → delete ref  │
#   │    Batch 3: commits 61-90  → push temp ref → delete ref  │
#   │  [REFRESH TOKEN]                                          │
#   │                                                           │
#   │  WAVE 2: Batches 4–6                                     │
#   │    Batch 4: commits 91-120 → push temp ref → delete ref  │
#   │    ...                                                    │
#   │  [REFRESH TOKEN]                                          │
#   │                                                           │
#   │  FINAL WAVE: Last batch                                  │
#   │    Batch N: remaining      → force push → branch update  │
#   └──────────────────────────────────────────────────────────┘

set -euo pipefail

BATCH_SIZE="${1:-30}"
REMOTE="${2:-origin}"
BRANCH="${3:-main}"
BATCHES_PER_WAVE=3
STATE_FILE="/tmp/chunked_push_state_$(basename "$(pwd)").txt"
REPO_DIR="$(pwd)"

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/Users/pikeymickey/bin:/Users/pikeymickey/.local/bin:$PATH"
export GIT_LFS_SKIP_SMUDGE=1

# ── Token refresh function ───────────────────────────────────
refresh_token() {
    echo "[TOKEN] Refreshing GitHub App installation token..."
    if [[ -f "scripts/auth_github_app.py" ]]; then
        python3 scripts/auth_github_app.py 2>/dev/null && echo "[TOKEN] Refreshed OK" || echo "[TOKEN] Refresh failed (non-fatal, SSH may still work)"
    else
        echo "[TOKEN] No auth script found — using existing SSH credentials"
    fi
}

# ── Banner ────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  CHUNKED FORCE PUSH — Resilient BFG History Rewrite     ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Batch size:       $BATCH_SIZE commits"
echo "║  Batches per wave: $BATCHES_PER_WAVE (token refresh between waves)"
echo "║  Remote:           $REMOTE"
echo "║  Branch:           $BRANCH"
echo "║  State file:       $STATE_FILE"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Get all commits oldest → newest
mapfile -t ALL_COMMITS < <(git rev-list --reverse HEAD)
TOTAL=${#ALL_COMMITS[@]}
echo "[INFO] Total commits: $TOTAL"
echo "[INFO] Expected batches: $(( (TOTAL + BATCH_SIZE - 1) / BATCH_SIZE ))"
echo "[INFO] Expected waves: $(( ((TOTAL + BATCH_SIZE - 1) / BATCH_SIZE + BATCHES_PER_WAVE - 1) / BATCHES_PER_WAVE ))"

# Resume check
RESUME_FROM=0
if [[ -f "$STATE_FILE" ]]; then
    RESUME_FROM=$(cat "$STATE_FILE")
    echo ""
    echo "[RESUME] ⚡ Resuming from commit index $RESUME_FROM / $TOTAL"
fi

# Initial token refresh
refresh_token

# ── Main push loop ────────────────────────────────────────────
BATCH_NUM=0
WAVE_BATCH_COUNT=0
FAILED=0
PUSH_START=$(date +%s)

for ((i = RESUME_FROM; i < TOTAL; i += BATCH_SIZE)); do
    BATCH_NUM=$((BATCH_NUM + 1))
    WAVE_BATCH_COUNT=$((WAVE_BATCH_COUNT + 1))
    END=$((i + BATCH_SIZE - 1))
    if ((END >= TOTAL)); then
        END=$((TOTAL - 1))
    fi

    COMMIT_SHA="${ALL_COMMITS[$END]}"
    BATCH_COUNT=$((END - i + 1))
    SHORT_SHA=$(echo "$COMMIT_SHA" | cut -c1-12)

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  BATCH $BATCH_NUM │ commits $((i+1))–$((END+1)) of $TOTAL"
    echo "  Target: $SHORT_SHA │ Size: $BATCH_COUNT commits"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    BATCH_START=$(date +%s)

    if ((END < TOTAL - 1)); then
        # ── Intermediate batch → temp ref ──
        TEMP_REF="_chunked_push_batch_${BATCH_NUM}"
        echo "[PUSH] → refs/heads/$TEMP_REF ..."

        if git -c core.hooksPath=/dev/null push --force "$REMOTE" \
            "${COMMIT_SHA}:refs/heads/${TEMP_REF}" 2>&1; then

            BATCH_END=$(date +%s)
            echo "[OK] Batch $BATCH_NUM pushed in $((BATCH_END - BATCH_START))s"

            # Clean up temp ref
            git push "$REMOTE" --delete "$TEMP_REF" 2>/dev/null || true
            echo "[CLEAN] Temp ref deleted"
        else
            echo ""
            echo "  ❌ BATCH $BATCH_NUM FAILED at $SHORT_SHA"
            echo "  Saving state for resume..."
            echo "$i" > "$STATE_FILE"
            FAILED=1
            break
        fi
    else
        # ── Final batch → actual branch ──
        echo "[PUSH] FINAL → $REMOTE/$BRANCH (force) ..."

        if git -c core.hooksPath=/dev/null push --force "$REMOTE" \
            "${COMMIT_SHA}:refs/heads/${BRANCH}" 2>&1; then

            BATCH_END=$(date +%s)
            echo "[OK] Final push in $((BATCH_END - BATCH_START))s"
        else
            echo ""
            echo "  ❌ FINAL PUSH FAILED at $SHORT_SHA"
            echo "$i" > "$STATE_FILE"
            FAILED=1
            break
        fi
    fi

    # Save progress after each batch
    echo "$((END + 1))" > "$STATE_FILE"
    PROGRESS=$(( (END + 1) * 100 / TOTAL ))
    echo "[SAVE] Progress: $((END+1))/$TOTAL ($PROGRESS%)"

    # ── Wave boundary: refresh token ──
    if ((WAVE_BATCH_COUNT >= BATCHES_PER_WAVE)) && ((END < TOTAL - 1)); then
        WAVE_BATCH_COUNT=0
        echo ""
        echo "┌────────────────────────────────────────────┐"
        echo "│  WAVE COMPLETE — Refreshing credentials    │"
        echo "└────────────────────────────────────────────┘"
        refresh_token
        echo "[WAIT] Cooling 5s before next wave..."
        sleep 5
    else
        # Brief pause between batches within a wave
        if ((END < TOTAL - 1)); then
            sleep 2
        fi
    fi
done

# ── Summary ───────────────────────────────────────────────────
PUSH_END=$(date +%s)
TOTAL_TIME=$((PUSH_END - PUSH_START))

echo ""
echo "══════════════════════════════════════════════════════════"
if ((FAILED == 0)); then
    echo "  ✅ ALL $TOTAL COMMITS PUSHED IN ${TOTAL_TIME}s"
    echo "  Batches: $BATCH_NUM │ Waves: $(( (BATCH_NUM + BATCHES_PER_WAVE - 1) / BATCHES_PER_WAVE ))"
    rm -f "$STATE_FILE"
else
    echo "  ❌ PUSH FAILED AFTER BATCH $BATCH_NUM"
    echo "  Resume: bash scripts/chunked_force_push.sh $BATCH_SIZE $REMOTE $BRANCH"
    echo "  State:  $STATE_FILE"
fi
echo "══════════════════════════════════════════════════════════"
