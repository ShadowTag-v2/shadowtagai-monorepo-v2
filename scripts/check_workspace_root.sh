#!/usr/bin/env bash
set -euo pipefail

CANONICAL_ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

if ! command -v realpath >/dev/null 2>&1; then
  echo "ERROR: realpath is required but not installed." >&2
  exit 1
fi

ACTUAL_ROOT="$(realpath "${PWD}")"
EXPECTED_ROOT="$(realpath "${CANONICAL_ROOT}")"

if [ "${ACTUAL_ROOT}" != "${EXPECTED_ROOT}" ]; then
  echo "ERROR: Workspace drift detected." >&2
  echo "Expected root: ${EXPECTED_ROOT}" >&2
  echo "Actual root:   ${ACTUAL_ROOT}" >&2
  echo "Refusing to continue outside canonical monorepo root." >&2
  exit 1
fi

if [ ! -f "${EXPECTED_ROOT}/monorepo_manifest.yaml" ]; then
  echo "ERROR: monorepo_manifest.yaml not found at canonical root." >&2
  exit 1
fi

if [ ! -f "${EXPECTED_ROOT}/MODULE.bazel" ]; then
  echo "ERROR: MODULE.bazel not found at canonical root." >&2
  exit 1
fi

echo "Workspace root verified: ${EXPECTED_ROOT}"
echo "Mode: single-root"
echo "Manifest: present"
echo "Bazel root: present"
