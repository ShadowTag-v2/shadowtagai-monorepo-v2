#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy_kovelai_hero_video.sh
# Upload the Veo 3.1 hero video to GCS and redeploy KovelAI Firebase Hosting.
#
# Prerequisites:
#   1. Video generated: apps/kovelai/public/hero-videos/legal-data-arch.mp4
#   2. gcloud auth login (ADC active)
#   3. firebase login
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

MONOREPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VIDEO_SRC="${MONOREPO_ROOT}/apps/kovelai/public/hero-videos/legal-data-arch.mp4"
GCS_DEST="gs://shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4"
PROJECT="shadowtag-omega-v4"

if [[ ! -f "${VIDEO_SRC}" ]]; then
    echo "❌  Video not found: ${VIDEO_SRC}"
    echo "    Run: ~/.local/bin/uv run --python 3.13 python scripts/gen_kovelai_hero_video.py"
    exit 1
fi

SIZE_MB=$(( $(stat -f%z "${VIDEO_SRC}") / 1048576 ))
echo "✅  Video found: ${VIDEO_SRC} (${SIZE_MB}MB)"

# ── Step 1: Upload to GCS ──────────────────────────────────────────────────
echo ""
echo "▶  Uploading to GCS..."
gsutil -h "Cache-Control:public,max-age=31536000" \
       -h "Content-Type:video/mp4" \
       cp "${VIDEO_SRC}" "${GCS_DEST}"

# Make publicly readable
gsutil acl ch -u AllUsers:R "${GCS_DEST}"

echo "✅  GCS URL: https://storage.googleapis.com/shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4"

# ── Step 2: Firebase Hosting Deploy ────────────────────────────────────────
echo ""
echo "▶  Deploying Firebase Hosting (kovelai)..."
cd "${MONOREPO_ROOT}/apps/kovelai"
firebase deploy --only hosting --project "${PROJECT}" 2>&1 | tail -15

echo ""
echo "✅  KovelAI deployed with Veo 3.1 hero video."
echo "    Live: https://kovelai.web.app"
