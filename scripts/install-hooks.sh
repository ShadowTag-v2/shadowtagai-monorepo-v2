#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# scripts/install-hooks.sh — Install Git hooks for the monorepo
# Symlinks governance hooks into .git/hooks/ for automatic enforcement.
#
# Usage: bash scripts/install-hooks.sh
# ═══════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "═══ Installing Git Hooks ═══"

# ── Pre-push: Bloat Gate ──
BLOAT_GATE="$REPO_ROOT/scripts/prepush-bloat-gate.sh"
if [ -f "$BLOAT_GATE" ]; then
  ln -sf "$BLOAT_GATE" "$HOOKS_DIR/pre-push"
  chmod +x "$HOOKS_DIR/pre-push"
  echo "  ✓ pre-push → prepush-bloat-gate.sh"
else
  echo "  ✗ prepush-bloat-gate.sh not found"
fi

# ── Pre-commit: pre-commit framework ──
if command -v pre-commit &>/dev/null; then
  (cd "$REPO_ROOT" && pre-commit install --allow-missing-config 2>/dev/null)
  echo "  ✓ pre-commit hooks installed"
else
  echo "  ⚠ pre-commit not found (install: pip install pre-commit)"
fi

echo ""
echo "═══ Hook Installation Complete ═══"
echo "  Run 'pre-commit run --all-files' to validate."
