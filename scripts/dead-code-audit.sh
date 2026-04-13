#!/usr/bin/env bash
# ============================================================================
# Canonical Guillotine v8.4 — Pre-Commit Hook
# ============================================================================
# This is a thin delegation shim. ALL logic lives in scripts/dead-code-audit.sh
# to prevent drift between the hook and the auditable script.
# ============================================================================
exec "$(git rev-parse --show-toplevel)/scripts/dead-code-audit.sh"
