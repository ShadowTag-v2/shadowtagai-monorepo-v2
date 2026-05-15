#!/usr/bin/env bash
# ============================================================================
# Canonical Guillotine v9.0 — Dead Code Janitor
# ============================================================================
# V22 Pruned Singularity: vulture removed. ruff F401/F841 handles dead code.
# Pre-commit gate (fast, local, report-only)
#
# Astral Ruff Integration:
#   - Core: https://github.com/astral-sh/ruff
#   - Pre-commit: https://github.com/astral-sh/ruff-pre-commit
#   - VSCode: https://github.com/astral-sh/ruff-vscode (charliermarsh.ruff)
#
# Complementary to gca_autolint_daemon.py (scheduled/CI autonomous sweep)
# ============================================================================

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Resolve tool paths — prefer .venv/bin, then Homebrew, then system
RUFF="${REPO_ROOT}/.venv/bin/ruff"
[[ -x "${REPO_ROOT}/.venv/bin/ruff" ]] || RUFF=$(command -v ruff 2>/dev/null || echo "")
[[ -n "$RUFF" && -x "$RUFF" ]] || RUFF="/opt/homebrew/bin/ruff"
[[ -x "$RUFF" ]] || RUFF=""

echo ">>> 🔪 Initializing Guillotine v9.0 [ruff + biome]..."

# 1. Ruff check and fix (full rule set)
if [[ -n "$RUFF" && -x "$RUFF" ]]; then
    echo ">>> Ruff version: $($RUFF --version)"
    echo ">>> Running ruff --fix ($RUFF)..."
    "$RUFF" check . --fix --exit-zero
    echo ">>> Running ruff --statistics..."
    "$RUFF" check --statistics . 2>&1 || true
else
    echo "⚠️ ruff not found. Install: pip install ruff>=0.15.11 (https://github.com/astral-sh/ruff)"
fi

# 2. Ruff dead-code focused pass (subsumes vulture)
if [[ -n "$RUFF" && -x "$RUFF" ]]; then
    echo ">>> Running ruff dead-code pass (F401 unused-import + F841 unused-variable)..."
    "$RUFF" check . --select F401,F841 --statistics 2>&1 || true
fi

echo ">>> ✅ Guillotine v9.0 sweep complete."
