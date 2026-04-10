#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

echo "[pre-commit] running startup relock"
bash scripts/startup_relock.sh >/tmp/startup_relock.out 2>/tmp/startup_relock.err || {
  echo "[pre-commit] FAIL: startup_relock.sh failed"
  cat /tmp/startup_relock.out 2>/dev/null || true
  cat /tmp/startup_relock.err 2>/dev/null || true
  exit 1
}

echo "[pre-commit] checking forbidden refresh string"
if rg -n --hidden \
  --glob '!**/.git/**' \
  --glob '!**/node_modules/**' \
  --glob '!**/.venv/**' \
  --glob '!**/dist/**' \
  --glob '!**/build/**' \
  'headless-runner@shadowtag-omega-v4\.iam\.gserviceaccount\.com is now REFRESHING at the start of every tool call' \
  "$ROOT" >/dev/null 2>&1; then
  echo "[pre-commit] FAIL: forbidden refresh string still present"
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/.venv/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    'headless-runner@shadowtag-omega-v4\.iam\.gserviceaccount\.com is now REFRESHING at the start of every tool call' \
    "$ROOT" || true
  exit 1
fi

echo "[pre-commit] checking for inline secret candidates"
if rg -n --hidden \
  --glob '!**/.git/**' \
  --glob '!**/node_modules/**' \
  --glob '!**/.venv/**' \
  --glob '!**/dist/**' \
  --glob '!**/build/**' \
  -e 'AIza[0-9A-Za-z\-_]{20,}' \
  -e 'sk-[A-Za-z0-9]{20,}' \
  -e 'ghp_[A-Za-z0-9]{20,}' \
  -e 'github_pat_[A-Za-z0-9_]{20,}' \
  -e 'BEGIN PRIVATE KEY' \
  "$ROOT" >/dev/null 2>&1; then
  echo "[pre-commit] FAIL: likely inline secret detected"
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/.venv/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    -e 'AIza[0-9A-Za-z\-_]{20,}' \
    -e 'sk-[A-Za-z0-9]{20,}' \
    -e 'ghp_[A-Za-z0-9]{20,}' \
    -e 'github_pat_[A-Za-z0-9_]{20,}' \
    -e 'BEGIN PRIVATE KEY' \
    "$ROOT" || true
  exit 1
fi

echo "[pre-commit] PASS"
