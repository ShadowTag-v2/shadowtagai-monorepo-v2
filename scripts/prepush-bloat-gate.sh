#!/usr/bin/env bash
# Composite pre-push hook: bloat gate + release readiness gate
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "═══ Pre-Push Gate: Bloat Check ═══"
if [ -x "$REPO_ROOT/scripts/prepush-bloat-gate.sh" ]; then
  bash "$REPO_ROOT/scripts/prepush-bloat-gate.sh" --fast || exit 1
fi

echo ""
echo "═══ Pre-Push Gate: Release Readiness ═══"
if [ -x "$REPO_ROOT/scripts/release-readiness-gate.sh" ]; then
  bash "$REPO_ROOT/scripts/release-readiness-gate.sh" || exit 1
fi

echo ""
echo "✅ All pre-push gates passed."
