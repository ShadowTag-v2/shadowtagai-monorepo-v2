#!/usr/bin/env bash
set -euo pipefail
EXPECTED="$(cd "$(dirname "$0")/.." && pwd)"
ACTUAL="$(pwd -P)"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "[root-guard] ERROR"
  echo "Expected workspace root:"
  echo "  $EXPECTED"
  echo "Actual:"
  echo "  $ACTUAL"
  exit 1
fi

echo "[root-guard] OK: $ACTUAL"
