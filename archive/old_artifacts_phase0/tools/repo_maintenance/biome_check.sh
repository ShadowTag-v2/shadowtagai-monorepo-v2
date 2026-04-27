#!/usr/bin/env bash
set -euo pipefail

if command -v biome >/dev/null 2>&1; then
  echo "[biome] checking JS/TS..."
  biome check --write .
elif command -v npx >/dev/null 2>&1; then
  echo "[biome] checking JS/TS via npx..."
  npx @biomejs/biome check --write .
else
  echo "[biome] skipped: biome/npx not installed"
fi
