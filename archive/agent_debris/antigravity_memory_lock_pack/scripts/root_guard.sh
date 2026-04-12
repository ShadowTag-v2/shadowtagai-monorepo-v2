#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd -P)"
for f in monorepo_manifest.yaml AGENTS.md antigravity-mcp-config.json; do
  if [[ ! -f "$ROOT/$f" ]]; then
    echo "[root_guard] missing required file: $f"
    exit 1
  fi
done
echo "[root_guard] OK: $ROOT"
