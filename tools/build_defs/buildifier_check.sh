#!/usr/bin/env bash
# tools/build_defs/buildifier_check.sh — Bazel sh_test wrapper
set -euo pipefail
cd "${BUILD_WORKSPACE_DIRECTORY:-.}"
exec bash scripts/check-buildifier.sh
