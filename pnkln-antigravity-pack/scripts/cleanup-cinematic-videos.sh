#!/usr/bin/env bash
set -euo pipefail
BUCKET="gs://pnkln-cinematic-artifacts"
DAYS=7
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG="docs/judge6-cleanup-${TIMESTAMP}.log"
echo "=== Judge-6 Video Cleanup Started: $(date) ===" | tee -a "${LOG}"
gcloud storage ls --recursive "${BUCKET}/videos/" | awk '{print $1}' | xargs -I {} gcloud storage rm --quiet {} 2>&1 | tee -a "${LOG}"
find docs/judge6-reports -name "judge6-*.md" -mtime +${DAYS} -delete 2>&1 | tee -a "${LOG}"
echo "=== Cleanup Complete ===" | tee -a "${LOG}"
