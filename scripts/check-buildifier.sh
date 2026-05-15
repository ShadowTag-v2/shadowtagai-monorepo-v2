#!/usr/bin/env bash
set -euo pipefail
# check-buildifier.sh — Thin wrapper around format-buildifier.sh --check.
# Single source of truth for Bazel formatting lives in format-buildifier.sh.
"$(dirname "$0")/format-buildifier.sh" --check
