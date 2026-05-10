#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# ANTIGRAVITY OS: FORCE-PUSH INTERCEPTOR (Invariant #105 / ISSUE-018)
# Prevents destructive force pushes unless STATE B is explicitly engaged.
# Called from the composite pre-push hook chain.
# ------------------------------------------------------------------------------
set -euo pipefail

echo "🛡️ [Antigravity] Checking for force-push / history rewrite..."

FORCE_DETECTED=0

while read -r local_ref local_oid remote_ref remote_oid; do
    # Skip branch deletion (local_oid = 0000...)
    if [ "$local_oid" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi

    # Skip new branch creation (remote_oid = 0000...)
    if [ "$remote_oid" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi

    # Check for non-fast-forward (force push indicator)
    if ! git merge-base --is-ancestor "$remote_oid" "$local_oid" 2>/dev/null; then
        FORCE_DETECTED=1
        echo "   ⚠️  Non-fast-forward detected: $local_ref → $remote_ref"
    fi
done

if [ "$FORCE_DETECTED" -eq 1 ]; then
    # Check for STATE B clutch file
    if [ -f /etc/antigravity/STATE_B_CLUTCH ]; then
        echo "   🔓 STATE B CLUTCH ENGAGED. Force push authorized by human."
        echo "   ⚠️  Remember to disengage: sudo rm /etc/antigravity/STATE_B_CLUTCH"
        exit 0
    fi

    echo ""
    echo "🛑 KERNEL BLOCK: Destructive Force Push / History Rewrite Detected."
    echo "   STATE B CLUTCH is offline. Invariant #105 / ISSUE-018 violated."
    echo ""
    echo "   Human Authorization Required:"
    echo "     sudo touch /etc/antigravity/STATE_B_CLUTCH"
    echo "   Then retry your push."
    exit 1
fi

echo "✅ [Antigravity] No force-push detected. Fast-forward push authorized."
