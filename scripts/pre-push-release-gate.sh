#!/usr/bin/env bash
# Pre-push hook: runs release-readiness-gate before push
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔒 Running release readiness gate..."
if [ -f "$REPO_ROOT/scripts/release-readiness-gate.sh" ]; then
  bash "$REPO_ROOT/scripts/release-readiness-gate.sh"
else
  echo "⚠️  release-readiness-gate.sh not found — skipping"
fi
