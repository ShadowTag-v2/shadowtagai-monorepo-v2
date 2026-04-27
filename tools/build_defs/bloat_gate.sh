#!/usr/bin/env bash
# tools/build_defs/bloat_gate.sh — Bazel sh_test wrapper
set -euo pipefail
cd "${BUILD_WORKSPACE_DIRECTORY:-.}"
exec bash scripts/prepush-bloat-gate.sh
