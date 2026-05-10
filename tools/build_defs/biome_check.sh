#!/usr/bin/env bash
# tools/build_defs/biome_check.sh — Bazel sh_test wrapper for biome
set -euo pipefail
cd "${BUILD_WORKSPACE_DIRECTORY:-.}"
exec biome check .
