#!/usr/bin/env bash
# ============================================================================
# Canonical Guillotine v8.6 — Dead Code Janitor
# ============================================================================
# Enforces Invariant #67: ruff + vulture sweep
# Uses .venv/bin/ tools first, falls back to system PATH
# ============================================================================

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Resolve tool paths — prefer .venv/bin over system
RUFF="${REPO_ROOT}/.venv/bin/ruff"
VULTURE="${REPO_ROOT}/.venv/bin/vulture"
command -v ruff &> /dev/null && RUFF=$(command -v ruff)
command -v vulture &> /dev/null && VULTURE=$(command -v vulture)
[[ -x "${REPO_ROOT}/.venv/bin/ruff" ]] && RUFF="${REPO_ROOT}/.venv/bin/ruff"
[[ -x "${REPO_ROOT}/.venv/bin/vulture" ]] && VULTURE="${REPO_ROOT}/.venv/bin/vulture"

echo ">>> 🔪 Initializing Guillotine [ruff + vulture]..."

# 1. Ruff check and fix
if [[ -x "$RUFF" ]]; then
    echo ">>> Running ruff --fix ($RUFF)..."
    "$RUFF" check . --fix --exit-zero
else
    echo "⚠️ ruff not found. Skipping."
fi

# 2. Vulture check
if [[ -x "$VULTURE" ]]; then
    echo ">>> Running vulture sweep (minimum confidence 80%)..."
    # Exclude standard directories and potential noise
    "$VULTURE" . --min-confidence 80 --exclude "archive,**/node_modules,**/venv,external_repos,external_sdks,control/legacy_workspaces,reference_architectures,apps/kovelai/venv,packages,apps/aiyou_stack/aiyou-fastapi-services/external_repos,tools,third_party,deep-archive,clones,clone-base,docs/bundles,branches,libs"
else
    echo "⚠️ vulture not found. Skipping."
fi

echo ">>> ✅ Guillotine sweep complete."
