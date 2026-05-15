#!/usr/bin/env bash
# session-handoff.sh — Ensures continuity during agent session transitions.
#
# Captures the outgoing session's working state (dirty files, branch, open beads,
# heartbeat) into a handoff manifest that the incoming agent can read to resume
# without loss.
#
# Usage:
#   session-handoff.sh              # write handoff manifest
#   session-handoff.sh --read       # display the last handoff
#   session-handoff.sh --validate   # check handoff integrity
set -euo pipefail

HANDOFF_DIR="${HANDOFF_DIR:-.beads}"
HANDOFF_FILE="${HANDOFF_DIR}/session_handoff.json"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

case "${1:-write}" in
  --read)
    if [[ -f "$HANDOFF_FILE" ]]; then
      echo "=== Last Session Handoff ==="
      python3 -m json.tool "$HANDOFF_FILE"
    else
      echo "No handoff file found at $HANDOFF_FILE"
      exit 1
    fi
    ;;
  --validate)
    if [[ ! -f "$HANDOFF_FILE" ]]; then
      echo "❌ No handoff file"
      exit 1
    fi
    python3 -c "
import json, sys
with open('${HANDOFF_FILE}') as f:
    h = json.load(f)
required = ['timestamp', 'branch', 'head_commit', 'dirty_files']
missing = [k for k in required if k not in h]
if missing:
    print(f'❌ Missing keys: {missing}')
    sys.exit(1)
print('✅ Handoff manifest valid')
print(f'  Branch: {h[\"branch\"]}')
print(f'  HEAD: {h[\"head_commit\"]}')
print(f'  Dirty: {len(h[\"dirty_files\"])} files')
print(f'  Open issues: {h.get(\"open_issue_count\", \"?\")}')
"
    ;;
  write|*)
    mkdir -p "$HANDOFF_DIR"
    # Gather state
    BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'detached')"
    HEAD="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
    DIRTY="$(git diff --name-only HEAD 2>/dev/null | head -50)"
    STAGED="$(git diff --cached --name-only 2>/dev/null | head -50)"
    OPEN_ISSUES="$(grep -c '"status":"open"' .beads/issues.jsonl 2>/dev/null || echo 0)"
    IN_PROGRESS="$(grep -c '"status":"in_progress"' .beads/issues.jsonl 2>/dev/null || echo 0)"

    python3 -c "
import json, sys

dirty = [l for l in '''${DIRTY}'''.strip().split('\n') if l]
staged = [l for l in '''${STAGED}'''.strip().split('\n') if l]

handoff = {
    'timestamp': '${TIMESTAMP}',
    'branch': '${BRANCH}',
    'head_commit': '${HEAD}',
    'dirty_files': dirty,
    'staged_files': staged,
    'open_issue_count': int('${OPEN_ISSUES}'),
    'in_progress_count': int('${IN_PROGRESS}'),
    'heartbeat_file': '.beads/kairos_heartbeat.json',
    'notes': ''
}

with open('${HANDOFF_FILE}', 'w') as f:
    json.dump(handoff, f, indent=2)
print(f'✅ Handoff written → ${HANDOFF_FILE}')
print(f'  Branch: ${BRANCH} @ ${HEAD}')
print(f'  Dirty: {len(dirty)} | Staged: {len(staged)}')
print(f'  Open issues: ${OPEN_ISSUES} | In progress: ${IN_PROGRESS}')
"
    ;;
esac
