#!/usr/bin/env bash
# Deploy Bravo — Nanobana 3 deployment mission
# Project: shadowtag-omega-v4
set -euo pipefail

MONO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$MONO_ROOT/apps/nanobanana"
LOG_DIR="$MONO_ROOT/artifacts/deploy-logs"
mkdir -p "$LOG_DIR"

echo "=== Bravo Mission: Deploy Nanobana 3 ==="
echo "Root: $MONO_ROOT"
echo "App:  $APP_DIR"

if [ ! -d "$APP_DIR" ]; then
  echo "ERROR: $APP_DIR not found — check fold_in_checklist.yaml for nanobanana status"
  exit 1
fi

# Stage 1: pre-deploy checks
echo "[1/3] Pre-deploy checks..."
python3 "$MONO_ROOT/scripts/run_codepmcs_scan.sh" 2>/dev/null || bash "$MONO_ROOT/scripts/run_codepmcs_scan.sh"

# Stage 2: build
echo "[2/3] Building Nanobana 3..."
if [ -f "$APP_DIR/package.json" ]; then
  (cd "$APP_DIR" && npm ci --silent && npm run build 2>&1 | tee "$LOG_DIR/build-$(date +%Y%m%d-%H%M%S).log")
elif [ -f "$APP_DIR/pyproject.toml" ] || [ -f "$APP_DIR/setup.py" ]; then
  (cd "$APP_DIR" && pip install -e . --quiet)
else
  echo "No known build system found in $APP_DIR — skipping build step"
fi

# Stage 3: deploy to Cloud Run (requires gcloud auth)
echo "[3/3] Deploying to Cloud Run..."
GCLOUD="${GCLOUD:-/Users/pikeymickey/google-cloud-sdk/bin/gcloud}"
PROJECT="${GOOGLE_CLOUD_PROJECT:-acquired-jet-478701-b3}"

if command -v "$GCLOUD" &>/dev/null; then
  "$GCLOUD" run deploy nanobanana-3 \
    --source="$APP_DIR" \
    --project="$PROJECT" \
    --region=us-central1 \
    --allow-unauthenticated \
    2>&1 | tee "$LOG_DIR/deploy-$(date +%Y%m%d-%H%M%S).log"
else
  echo "gcloud not found at $GCLOUD — set GCLOUD env var or install Cloud SDK"
  echo "Manual deploy: gcloud run deploy nanobanana-3 --source=$APP_DIR --project=$PROJECT"
  exit 1
fi

echo "=== Bravo Mission COMPLETE ==="
