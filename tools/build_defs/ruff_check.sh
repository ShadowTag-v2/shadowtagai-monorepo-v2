#!/usr/bin/env bash
# tools/build_defs/ruff_check.sh — Bazel sh_test wrapper for ruff
set -euo pipefail
cd "${BUILD_WORKSPACE_DIRECTORY:-.}"
exec ruff check --select F401,F841 .
