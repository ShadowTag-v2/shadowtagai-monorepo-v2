#!/usr/bin/env bash
# ==============================================================================
# sovereign_egress_daemon.sh — Background MLX Daemon for Secret Manager Migration
#
# Performs: full-repo key scan → replace literal keys with ${VAR} refs →
#           amend commit → re-push through egress gates
#
# Logs to: /tmp/sovereign_egress_daemon.log
# ==============================================================================
set -eo pipefail

REPO_ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
LOG="/tmp/sovereign_egress_daemon.log"
# Fetch key at runtime from Secret Manager — never embed literals in source
KEY_LITERAL=$(gcloud secrets versions access latest --secret=google-design-api-key --project=shadowtag-omega-v4 2>/dev/null || echo "FETCH_FAILED")
if [ "$KEY_LITERAL" = "FETCH_FAILED" ]; then
    echo "  ❌ Failed to fetch key from Secret Manager. Aborting."
    exit 1
fi
KEY_REPLACEMENT="\${GOOGLE_DESIGN_API_KEY}"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

exec > >(tee -a "$LOG") 2>&1

echo "═══════════════════════════════════════════════"
echo "  Sovereign Egress Daemon — Started $TIMESTAMP"
echo "═══════════════════════════════════════════════"

cd "$REPO_ROOT"

# ── Phase 1: Full-Repo Literal Key Scan ──
echo ""
echo "[Phase 1] Scanning entire repo for literal key occurrences..."
echo "  Pattern: $KEY_LITERAL"

# Use git grep (respects .gitignore, fast)
OCCURRENCES=$(git grep -rn "$KEY_LITERAL" -- ':(exclude).git' 2>/dev/null || true)

if [ -z "$OCCURRENCES" ]; then
    echo "  ✅ No remaining literal key occurrences found in tracked files."
else
    echo "  ⚠️  Found occurrences:"
    echo "$OCCURRENCES" | while IFS= read -r line; do
        echo "    → $line"
    done

    # ── Phase 2: Replace in each file ──
    echo ""
    echo "[Phase 2] Replacing literal keys with \${GOOGLE_DESIGN_API_KEY}..."

    echo "$OCCURRENCES" | cut -d: -f1 | sort -u | while IFS= read -r filepath; do
        # Skip .gitleaksignore (fingerprints are expected there)
        if [[ "$filepath" == ".gitleaksignore" ]]; then
            echo "  ⏭  Skipping $filepath (allowlist file)"
            continue
        fi
        echo "  🔧 Patching: $filepath"
        # Use sed for in-place replacement (macOS sed)
        sed -i '' "s|$KEY_LITERAL|$KEY_REPLACEMENT|g" "$filepath"
    done

    echo "  ✅ All replacements complete."
fi

# ── Phase 3: Verify clean ──
echo ""
echo "[Phase 3] Post-patch verification..."
REMAINING=$(git grep -rn "$KEY_LITERAL" -- ':(exclude).git' ':(exclude).gitleaksignore' 2>/dev/null || true)

if [ -n "$REMAINING" ]; then
    echo "  ❌ STILL FOUND (manual review needed):"
    echo "$REMAINING"
    echo ""
    echo "  Daemon exiting — manual intervention required."
    exit 1
fi
echo "  ✅ Zero literal occurrences remain (excluding .gitleaksignore)."

# ── Phase 4: Check if anything changed ──
echo ""
echo "[Phase 4] Staging and amending commit..."
CHANGED=$(git diff --name-only 2>/dev/null || true)

if [ -z "$CHANGED" ]; then
    echo "  ℹ️  No working tree changes detected — commit already clean."
else
    echo "  Files modified:"
    echo "$CHANGED" | while IFS= read -r f; do echo "    → $f"; done
    git add -A
    git commit --amend --no-edit --allow-empty
    echo "  ✅ Commit amended successfully."
fi

# ── Phase 5: Verify diff is egress-clean ──
echo ""
echo "[Phase 5] Pre-flight egress simulation..."
DIFF_CHECK=$(git diff HEAD~1..HEAD | grep -cE 'AIza[a-zA-Z0-9_-]{35}' 2>/dev/null || echo "0")
DIFF_CHECK=$(echo "$DIFF_CHECK" | tr -cd '0-9')

if [ "${DIFF_CHECK:-0}" -gt 0 ]; then
    echo "  ❌ Egress simulation FAILED — $DIFF_CHECK AIza patterns still in diff"
    echo "  Showing context:"
    git diff HEAD~1..HEAD | grep -B2 -A2 'AIza' | head -20
    exit 1
fi
echo "  ✅ Egress simulation PASSED — 0 AIza patterns in diff."

# ── Phase 6: Generate fresh token and push ──
echo ""
echo "[Phase 6] Pushing via SSH to sovereign repo..."
git push origin chore/sovereign-migration-config 2>&1 || {
    echo ""
    echo "  ⚠️  SSH push encountered egress gate."
    echo "  Attempting to diagnose..."
    echo "  Check log at: $LOG"
    exit 1
}

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ SOVEREIGN EGRESS COMPLETE"
echo "  Branch: chore/sovereign-migration-config"
echo "  Remote: origin (shadowtagai-monorepo-v2)"
echo "  Completed: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "═══════════════════════════════════════════════"

# ── Phase 7: Fast-forward merge to main ──
echo ""
echo "[Phase 7] Merging into main (fast-forward)..."
git checkout main
git merge --ff-only chore/sovereign-migration-config
git push origin main
echo "  ✅ main updated and pushed."

echo ""
echo "══════════════════════════════════════"
echo "  🏁 DAEMON COMPLETE — ALL PHASES OK"
echo "══════════════════════════════════════"
