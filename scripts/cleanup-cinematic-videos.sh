#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR="${JUDGE6_REPORT_DIR:-${PWD}/artifacts/judge6-reports}"
BUCKET="${JUDGE6_GCS_BUCKET:-}"
DAYS="${JUDGE6_RETENTION_DAYS:-7}"
TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
LOG_DIR="${PWD}/artifacts/logs"
LOG_FILE="${LOG_DIR}/judge6-cleanup-${TIMESTAMP}.log"

mkdir -p "${REPORT_DIR}" "${LOG_DIR}"

log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "${LOG_FILE}"
}

log "Judge-6 cleanup starting"

find "${REPORT_DIR}" -type f -name "judge6-*.md" -mtime +"${DAYS}" -print -delete | tee -a "${LOG_FILE}"

if [ -z "${BUCKET}" ]; then
  log "JUDGE6_GCS_BUCKET not set; skipping remote cleanup"
  log "Judge-6 cleanup complete"
  exit 0
fi

if ! command -v gcloud >/dev/null 2>&1; then
  log "gcloud not installed; skipping remote cleanup"
  log "Judge-6 cleanup complete"
  exit 0
fi

CUTOFF_EPOCH="$(date -u -d "${DAYS} days ago" +%s)"

while IFS=$'\t' read -r created object; do
  [ -z "${created}" ] && continue
  [ -z "${object}" ] && continue

  created_epoch="$(date -u -d "${created}" +%s 2>/dev/null || echo 0)"
  if [ "${created_epoch}" -gt 0 ] && [ "${created_epoch}" -lt "${CUTOFF_EPOCH}" ]; then
    log "Deleting remote object: ${object}"
    gcloud storage rm --quiet "${object}"
  fi
done < <(
  gcloud storage ls --recursive --long "${BUCKET%/}/videos/**" 2>/dev/null \
    | awk '/^ +[0-9]+/ {print $2 "\t" $NF}'
)

log "Judge-6 cleanup complete"
