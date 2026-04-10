#!/usr/bin/env bash
set -euo pipefail

EXPECTED="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
ACTUAL="$(pwd -P)"

if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "[pnkln-root-guard] ERROR"
  echo "Expected workspace root:"
  echo "  $EXPECTED"
  echo "Actual:"
  echo "  $ACTUAL"
  exit 1
fi

echo "[pnkln-root-guard] OK: $ACTUAL"
