#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
HOOK_DIR="$ROOT/.git/hooks"
HOOK_FILE="$HOOK_DIR/pre-push"

cd "$ROOT"

if [[ ! -d ".git" ]]; then
  echo "ERROR: .git directory not found at $ROOT"
  exit 1
fi

mkdir -p "$HOOK_DIR"

# Natively load hook from existing script to bypass unconstrained bash heredocs
cp "$ROOT/scripts/source_pre_push.sh" "$HOOK_FILE" || true

chmod +x "$HOOK_FILE"
echo "Installed pre-push hook at $HOOK_FILE"
