#!/usr/bin/env bash
# scripts/check-buildifier.sh — Pre-push Bazel formatting gate
# Verifies all tracked Bazel files pass buildifier formatting.
# Exit 0 = clean, Exit 1 = formatting violations found.
#
# Usage:
#   ./scripts/check-buildifier.sh          # Check all tracked Bazel files
#   ./scripts/check-buildifier.sh --fix    # Auto-fix formatting issues

set -euo pipefail

# Resolve buildifier location
BUILDIFIER="$(command -v buildifier 2>/dev/null || true)"
if [[ -z "${BUILDIFIER}" ]]; then
  echo "ERROR: buildifier not found on PATH."
  echo "Install: brew install buildifier"
  exit 1
fi

MODE="check"
if [[ "${1:-}" == "--fix" ]]; then
  MODE="fix"
fi

echo "Checking Bazel file formatting (mode=${MODE})..."

# Collect tracked Bazel files only (excludes .bazelignore'd zones)
FILES=$(git ls-files \
  'BUILD' \
  'BUILD.bazel' \
  'WORKSPACE' \
  'WORKSPACE.bazel' \
  'MODULE.bazel' \
  '*.bzl' \
  '**/BUILD' \
  '**/BUILD.bazel' \
  '**/MODULE.bazel' \
  '**/*.bzl' 2>/dev/null || true)

if [[ -z "${FILES}" ]]; then
  echo "No tracked Bazel files found."
  exit 0
fi

COUNT=$(echo "${FILES}" | wc -l | tr -d ' ')
echo "Found ${COUNT} Bazel file(s)."

if [[ "${MODE}" == "fix" ]]; then
  echo "${FILES}" | xargs "${BUILDIFIER}"
  echo "Buildifier formatting applied to ${COUNT} file(s)."
else
  if echo "${FILES}" | xargs "${BUILDIFIER}" -mode=check; then
    echo "All ${COUNT} Bazel file(s) are correctly formatted."
  else
    echo ""
    echo "ERROR: Bazel files have formatting issues."
    echo "Run: ./scripts/check-buildifier.sh --fix"
    exit 1
  fi
fi
