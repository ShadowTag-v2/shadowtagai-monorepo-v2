#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

echo "[startup] checking memory lock"
scripts/check_memory_lock.sh

echo "[startup] exporting canonical environment"
export GCP_PROJECT_ID="shadowtag-omega-v4"
export BRAIN_DIR="/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e50"

echo "[startup] verifying truth surfaces"
scripts/audit_truth_surfaces.sh

echo "[startup] ready"
