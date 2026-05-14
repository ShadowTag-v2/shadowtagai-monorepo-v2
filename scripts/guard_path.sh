#!/usr/bin/env bash
set -euo pipefail

CANONICAL_ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path>" >&2
  exit 2
fi

TARGET="$1"

if ! command -v realpath >/dev/null 2>&1; then
  echo "ERROR: realpath is required but not installed." >&2
  exit 1
fi

ROOT_REAL="$(realpath "${CANONICAL_ROOT}")"
TARGET_REAL="$(realpath -m "${TARGET}")"

case "${TARGET_REAL}" in
  "${ROOT_REAL}"|"${ROOT_REAL}"/*)
    ;;
  *)
    echo "ERROR: Target path is outside canonical root." >&2
    echo "Canonical root: ${ROOT_REAL}" >&2
    echo "Target path:    ${TARGET_REAL}" >&2
    exit 1
    ;;
esac

case "${TARGET_REAL}" in
  "${ROOT_REAL}"/archive/*|\
  "${ROOT_REAL}"/tools/legacy/*|\
  "${ROOT_REAL}"/docs/legacy_shadowtag_v2/*|\
  "${ROOT_REAL}"/apps/aiyou_ecosystem/raw_ingest/*|\
  */_PRE_OMEGA_BACKUP_*/*|\
  */ShadowTag-Omega/*|\
  */arsenal_recovered/*|\
  */repos/*-legacy/*)
    echo "ERROR: Target path is inside a denied zone." >&2
    echo "Target path: ${TARGET_REAL}" >&2
    exit 1
    ;;
  *)
    ;;
esac

echo "${TARGET_REAL}"
