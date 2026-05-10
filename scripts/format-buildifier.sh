#!/usr/bin/env bash
set -euo pipefail

# format-buildifier.sh
#
# Formats Bazel/Starlark files with buildifier while avoiding forbidden,
# generated, archived, vendored, and local-only monorepo zones.
#
# Usage:
#   scripts/format-buildifier.sh
#   scripts/format-buildifier.sh --check
#
# Environment:
#   BUILDIFIER_BIN=/path/to/buildifier   Override buildifier binary.
#   BUILDIFIER_LINT=fix|warn|off         Default: fix for format, warn for check.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

MODE="fix"

case "${1:-}" in
  "")
    ;;
  --check)
    MODE="check"
    ;;
  --help|-h)
    cat <<'USAGE'
Usage:
  scripts/format-buildifier.sh
  scripts/format-buildifier.sh --check

Formats Bazel/Starlark files:
  BUILD
  BUILD.bazel
  WORKSPACE
  WORKSPACE.bazel
  MODULE.bazel
  *.bzl

Skips forbidden/heavy zones:
  archive/
  external_repos/
  legacy_workspaces/
  venv/
  .venv*/
  node_modules/
  .gitnexus/
  generated caches/build outputs
USAGE
    exit 0
    ;;
  *)
    echo "Unknown argument: $1" >&2
    echo "Run: scripts/format-buildifier.sh --help" >&2
    exit 2
    ;;
esac

# Set BUILDIFIER_LINT default based on mode, respecting env override.
if [ -z "${BUILDIFIER_LINT:-}" ]; then
  if [ "${MODE}" = "check" ]; then
    BUILDIFIER_LINT="warn"
  else
    BUILDIFIER_LINT="fix"
  fi
fi

BUILDIFIER_BIN="${BUILDIFIER_BIN:-buildifier}"

if ! command -v "${BUILDIFIER_BIN}" >/dev/null 2>&1; then
  echo "ERROR: buildifier not found on PATH." >&2
  echo "Install buildifier or set BUILDIFIER_BIN=/absolute/path/to/buildifier." >&2
  exit 127
fi

echo "== Buildifier =="
"${BUILDIFIER_BIN}" --version 2>/dev/null || true

echo "== Discovering Bazel/Starlark files =="

tmpfile="$(mktemp)"
trap 'rm -f "${tmpfile}"' EXIT

# Use git-tracked files first so ignored local bloat never enters the formatter.
# Include root files and Starlark files. This intentionally avoids a broad
# filesystem walk across archive/, venvs, node_modules, .gitnexus, etc.
git ls-files -z \
  'BUILD' \
  'BUILD.bazel' \
  'WORKSPACE' \
  'WORKSPACE.bazel' \
  'MODULE.bazel' \
  '*.bzl' \
  '*/BUILD' \
  '*/BUILD.bazel' \
  '*/WORKSPACE' \
  '*/WORKSPACE.bazel' \
  '*/MODULE.bazel' \
  '*/*.bzl' \
  '*/*/*.bzl' \
  '*/*/*/*.bzl' \
  '*/*/*/*/*.bzl' \
  | tr '\0' '\n' \
  | grep -Ev '(^|/)(archive|external_repos|legacy_workspaces|venv|\.venv[^/]*|node_modules|\.gitnexus|\.mypy_cache|\.ruff_cache|\.pytest_cache|dist|build|out|\.next|\.turbo)(/|$)' \
  | sort -u \
  > "${tmpfile}"

if [ ! -s "${tmpfile}" ]; then
  echo "No tracked Bazel/Starlark files found."
  exit 0
fi

count="$(wc -l < "${tmpfile}" | tr -d ' ')"
echo "Found ${count} file(s)."

if [ "${MODE}" = "check" ]; then
  echo "== Checking Buildifier formatting =="
  xargs "${BUILDIFIER_BIN}" -mode=check -lint="${BUILDIFIER_LINT}" < "${tmpfile}"
  echo "Buildifier check passed."
else
  echo "== Formatting with Buildifier =="
  xargs "${BUILDIFIER_BIN}" -mode=fix -lint="${BUILDIFIER_LINT}" < "${tmpfile}"
  echo "Buildifier formatting complete."
fi
