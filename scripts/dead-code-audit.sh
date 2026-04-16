#!/usr/bin/env bash
# ============================================================================
# Canonical Guillotine v8.5 — Dead Code Janitor
# ============================================================================
# Enforces Invariant #67: ruff + vulture sweep
# ============================================================================

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

echo ">>> 🔪 Initializing Guillotine [ruff + vulture]..."

# 1. Ruff check and fix
if command -v ruff &> /dev/null; then
    echo ">>> Running ruff --fix..."
    ruff check . --fix --exit-zero
else
    echo "⚠️ ruff not found. Skipping."
fi

# 2. Vulture check
if command -v vulture &> /dev/null; then
    echo ">>> Running vulture sweep (minimum confidence 80%)..."
    # Exclude standard directories and potential noise
    vulture . --min-confidence 80 --exclude "archive,**/node_modules,**/venv"
else
    echo "⚠️ vulture not found. Skipping."
fi

echo ">>> ✅ Guillotine sweep complete."
