#!/usr/bin/env bash
set -euo pipefail

if command -v ast-grep >/dev/null 2>&1; then
  echo "[ast-grep] scanning structural rules..."
  ast-grep scan || true
elif command -v sg >/dev/null 2>&1; then
  echo "[ast-grep] scanning structural rules via sg..."
  sg scan || true
else
  echo "[ast-grep] skipped: ast-grep/sg not installed"
fi
