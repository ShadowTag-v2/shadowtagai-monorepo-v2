#!/usr/bin/env bash
set -euo pipefail

mkdir -p tools/repo_maintenance/reports

echo "[betterleaks] scanning working tree..."
betterleaks dir \
  --report-format=json \
  --report-path=tools/repo_maintenance/reports/betterleaks-dir.json \
  .

echo "[betterleaks] scanning git history..."
betterleaks git \
  --git-workers="${BETTERLEAKS_GIT_WORKERS:-8}" \
  --report-format=sarif \
  --report-path=tools/repo_maintenance/reports/betterleaks-git.sarif \
  .

echo "[betterleaks] complete"
