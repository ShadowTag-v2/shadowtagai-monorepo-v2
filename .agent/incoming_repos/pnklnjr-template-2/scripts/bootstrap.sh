#!/usr/bin/env bash
set -euo pipefail
echo "[bootstrap] installing deps"
npm i -g pnpm@9 || true
pnpm i || npm i
echo "[bootstrap] lint/test"
pnpm -r lint || true
pnpm -r test || true

