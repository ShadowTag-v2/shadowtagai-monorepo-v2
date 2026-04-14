#!/usr/bin/env bash
# scripts/deploy_hero_videos.sh — Cache-busting deployment for GCS-hosted hero videos
# Usage: ./scripts/deploy_hero_videos.sh [--force]
#
# This script:
# 1. Uploads hero video assets to GCS with cache-busting filenames
# 2. Updates HTML source references in both platforms
# 3. Deploys Firebase Hosting with the updated references
# 4. Optionally invalidates CDN cache

set -euo pipefail

BUCKET="gs://shadowtag-omega-v4-archive/hero-videos"
PROJECT="shadowtag-omega-v4"
TIMESTAMP=$(date +%s)

SHADOWTAG_HTML="apps/shadowtagai/public/index.html"
KOVELAI_HTML="apps/kovelai/public/index.html"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[deploy]${NC} $1"; }
warn() { echo -e "${YELLOW}[warn]${NC} $1"; }
err() { echo -e "${RED}[error]${NC} $1" >&2; }

# Verify prerequisites
command -v gcloud >/dev/null 2>&1 || { err "gcloud not found"; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { err "ffmpeg not found"; exit 1; }

# Source videos (local or from GCS)
SHADOWTAG_MP4="${1:-/tmp/fluid-kinetic-aura.mp4}"
KOVELAI_MP4="${2:-/tmp/legal-data-arch.mp4}"

if [[ ! -f "$SHADOWTAG_MP4" ]]; then
    log "Downloading current ShadowTag video from GCS..."
    gcloud storage cp "${BUCKET}/fluid-kinetic-aura.mp4" "$SHADOWTAG_MP4"
fi

if [[ ! -f "$KOVELAI_MP4" ]]; then
    log "Downloading current KovelAI video from GCS..."
    gcloud storage cp "${BUCKET}/legal-data-arch.mp4" "$KOVELAI_MP4"
fi

# Generate cache-busted filenames
SHADOWTAG_VERSIONED="fluid-kinetic-aura-v${TIMESTAMP}.mp4"
KOVELAI_VERSIONED="legal-data-arch-v${TIMESTAMP}.mp4"
SHADOWTAG_WEBM="fluid-kinetic-aura-v${TIMESTAMP}.webm"
KOVELAI_WEBM="legal-data-arch-v${TIMESTAMP}.webm"

log "Transcoding WebM fallbacks (VP9)..."
ffmpeg -y -i "$SHADOWTAG_MP4" -c:v libvpx-vp9 -crf 30 -b:v 0 -an -deadline good -cpu-used 2 "/tmp/${SHADOWTAG_WEBM}" 2>/dev/null
ffmpeg -y -i "$KOVELAI_MP4" -c:v libvpx-vp9 -crf 30 -b:v 0 -an -deadline good -cpu-used 2 "/tmp/${KOVELAI_WEBM}" 2>/dev/null

log "Uploading versioned assets to GCS..."
UPLOAD_OPTS="--cache-control=public,max-age=31536000,immutable"

gcloud storage cp "$SHADOWTAG_MP4" "${BUCKET}/${SHADOWTAG_VERSIONED}" --content-type="video/mp4" ${UPLOAD_OPTS}
gcloud storage cp "$KOVELAI_MP4" "${BUCKET}/${KOVELAI_VERSIONED}" --content-type="video/mp4" ${UPLOAD_OPTS}
gcloud storage cp "/tmp/${SHADOWTAG_WEBM}" "${BUCKET}/${SHADOWTAG_WEBM}" --content-type="video/webm" ${UPLOAD_OPTS}
gcloud storage cp "/tmp/${KOVELAI_WEBM}" "${BUCKET}/${KOVELAI_WEBM}" --content-type="video/webm" ${UPLOAD_OPTS}

GCS_BASE="https://storage.googleapis.com/shadowtag-omega-v4-archive/hero-videos"

log "Updating HTML source references..."
# ShadowTag AI
sed -i '' "s|${GCS_BASE}/fluid-kinetic-aura[^\"]*\.mp4|${GCS_BASE}/${SHADOWTAG_VERSIONED}|g" "$SHADOWTAG_HTML"
sed -i '' "s|${GCS_BASE}/fluid-kinetic-aura[^\"]*\.webm|${GCS_BASE}/${SHADOWTAG_WEBM}|g" "$SHADOWTAG_HTML"

# KovelAI
sed -i '' "s|${GCS_BASE}/legal-data-arch[^\"]*\.mp4|${GCS_BASE}/${KOVELAI_VERSIONED}|g" "$KOVELAI_HTML"
sed -i '' "s|${GCS_BASE}/legal-data-arch[^\"]*\.webm|${GCS_BASE}/${KOVELAI_WEBM}|g" "$KOVELAI_HTML"

log "Deploying Firebase Hosting..."
npx firebase-tools deploy --only hosting --project "$PROJECT"

log "✅ Cache-busted deployment complete!"
echo ""
echo "  ShadowTag MP4: ${GCS_BASE}/${SHADOWTAG_VERSIONED}"
echo "  ShadowTag WebM: ${GCS_BASE}/${SHADOWTAG_WEBM}"
echo "  KovelAI MP4: ${GCS_BASE}/${KOVELAI_VERSIONED}"
echo "  KovelAI WebM: ${GCS_BASE}/${KOVELAI_WEBM}"
echo ""
echo "  Timestamp: ${TIMESTAMP}"
