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

# ── Pre-push: Composite Gate (Bloat + Release Readiness) ──
BLOAT_GATE="$REPO_ROOT/scripts/prepush-bloat-gate.sh"
RELEASE_GATE="$REPO_ROOT/scripts/release-readiness-gate.sh"
COMPOSITE_HOOK="$HOOKS_DIR/pre-push"

cat > "$COMPOSITE_HOOK" << 'HOOK_EOF'
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
HOOK_EOF

chmod +x "$COMPOSITE_HOOK"
echo "  ✓ pre-push → composite (bloat + release-readiness)"

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
