#!/usr/bin/env bash
set -euo pipefail

# python-typecheck.sh — Pyrefly type checking wrapper
#
# Usage:
#   bash scripts/python-typecheck.sh advisory
#   bash scripts/python-typecheck.sh enforced
#
# Referenced by: push-with-app-gates.sh, .pre-commit-config.yaml

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

mkdir -p .reports/python

MODE="${1:-advisory}"
REPORT=".reports/python/pyrefly-${MODE}.log"

if ! command -v pyrefly >/dev/null 2>&1; then
  echo "ERROR: pyrefly not found on PATH." | tee "${REPORT}"
  echo "Install pyrefly or use the pinned pyrefly-pre-commit hook." | tee -a "${REPORT}"
  exit 127
fi

set +e
pyrefly check --output-format=github 2>&1 | tee "${REPORT}"
status="${PIPESTATUS[0]}"
set -e

if [ "${status}" -ne 0 ]; then
  echo "Pyrefly found type errors. Report: ${REPORT}"
  if [ "${MODE}" = "enforced" ]; then
    exit "${status}"
  fi
fi

echo "Pyrefly typecheck complete. Report: ${REPORT}"
