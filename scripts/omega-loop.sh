#!/usr/bin/env bash

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
export pnkln_WORKSPACE_ROOT="$ROOT"
export GOOGLE_CLOUD_PROJECT="shadowtag-omega-v4"

echo "💎 Initializing Omega Loop Absolute Sync..."

cd "$ROOT" || exit 1

if [[ -f "$ROOT/scripts/omega_sync.py" ]]; then
    python3 "$ROOT/scripts/omega_sync.py"
elif [[ -f "$ROOT/scripts/finish_changes.py" ]]; then
    python3 "$ROOT/scripts/finish_changes.py"
else
    echo "   -> Error: Neither omega_sync.py nor finish_changes.py found."
    exit 1
fi

echo "✅ Codebase Canonicalized, Secured, and Delivered."
