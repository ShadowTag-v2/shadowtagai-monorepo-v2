#!/usr/bin/env bash
# ==============================================================================
# ANTIGRAVITY OS: COMPOSITE PRE-PUSH HOOK
# Chains: Force-Push Guard → Bloat Gate → Release Readiness → Egress Scan
# ==============================================================================
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# ─── Gate 1: Force-Push / History Rewrite Guard (Invariant #105) ───
echo "═══ Pre-Push Gate 1: Force-Push Guard ═══"
if [ -x "$REPO_ROOT/scripts/force-push-guard.sh" ]; then
  bash "$REPO_ROOT/scripts/force-push-guard.sh" || exit 1
else
  echo "   ⚠️  force-push-guard.sh not found, skipping."
fi

echo ""

# ─── Gate 2: Bloat Check ───
echo "═══ Pre-Push Gate 2: Bloat Check ═══"
if [ -x "$REPO_ROOT/scripts/prepush-bloat-gate.sh" ]; then
  bash "$REPO_ROOT/scripts/prepush-bloat-gate.sh" --fast || exit 1
else
  echo "   ⚠️  prepush-bloat-gate.sh not found, skipping."
fi

echo ""

# ─── Gate 3: Release Readiness ───
echo "═══ Pre-Push Gate 3: Release Readiness ═══"
if [ -x "$REPO_ROOT/scripts/release-readiness-gate.sh" ]; then
  bash "$REPO_ROOT/scripts/release-readiness-gate.sh" || exit 1
else
  echo "   ⚠️  release-readiness-gate.sh not found, skipping."
fi

echo ""

# ─── Gate 4: Secret Egress Scan (Invariant #115) ───
echo "═══ Pre-Push Gate 4: Secret Egress Scan ═══"
if [ -x "$REPO_ROOT/scripts/sync-daemon.sh" ]; then
  bash "$REPO_ROOT/scripts/sync-daemon.sh" || exit 1
else
  echo "   ⚠️  sync-daemon.sh not found, skipping."
fi

echo ""
echo "✅ All pre-push gates passed."
