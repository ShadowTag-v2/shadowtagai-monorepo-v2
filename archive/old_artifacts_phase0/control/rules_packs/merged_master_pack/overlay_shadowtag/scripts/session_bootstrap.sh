#!/usr/bin/env bash
set -euo pipefail

echo "[bootstrap] checking repo status"
git status --short || true

echo "[bootstrap] current branch"
git branch --show-current || true

echo "[bootstrap] current directory"
pwd

echo "[bootstrap] reminder: read docs/Cor.Constitution.v3.md and workflow files"
