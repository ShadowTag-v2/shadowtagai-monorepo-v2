#!/usr/bin/env bash
# tools/build_defs/dead_code_audit.sh — Bazel sh_test wrapper
set -euo pipefail
cd "${BUILD_WORKSPACE_DIRECTORY:-.}"
exec bash scripts/dead-code-audit.sh
