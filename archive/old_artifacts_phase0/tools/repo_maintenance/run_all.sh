#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

mkdir -p tools/repo_maintenance/reports

echo "[repo-maintenance] root: $ROOT"

bash tools/repo_maintenance/betterleaks_scan.sh
bash tools/repo_maintenance/ruff_check.sh
bash tools/repo_maintenance/biome_check.sh
bash tools/repo_maintenance/ast_grep_scan.sh

echo "[repo-maintenance] final git status"
git status --short

echo "[repo-maintenance] complete"
