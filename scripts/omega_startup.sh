#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$REPO_ROOT"

bash scripts/root_guard.sh
python3 scripts/memory_lock_audit.py --repo-root "$REPO_ROOT" --write
python3 scripts/rebuild_context_packet.py --repo-root "$REPO_ROOT" --write

echo
printf '%s\n' '[omega_startup] Read these next:'
printf '%s\n' '  AGENTS.md'
printf '%s\n' '  docs/MEMORY_LOCK.md'
printf '%s\n' '  docs/SESSION_PACKET.md'
printf '%s\n' '  docs/AUDIT_REPORT.md'
