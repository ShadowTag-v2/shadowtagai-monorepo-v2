#!/usr/bin/env bash
set -euo pipefail

# beads-plan.sh — Beads Task Graph Wrapper
#
# Provides a human-friendly CLI over the Beads task graph.
# Reads/writes .beads/issues.jsonl as the authoritative mutation log.
# SQLite indexes are rebuilt from this file; they are never the source of truth.
#
# Usage:
#   scripts/beads-plan.sh list                    # list all issues
#   scripts/beads-plan.sh show <id>               # show a specific issue
#   scripts/beads-plan.sh add <summary>           # add a new issue
#   scripts/beads-plan.sh close <id> <reason>     # close an issue
#   scripts/beads-plan.sh stats                   # summary statistics
#
# Referenced by: truth_surfaces.yaml, MONOREPO_OS.md

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BEADS_DIR="${ROOT}/.beads"
ISSUES_FILE="${BEADS_DIR}/issues.jsonl"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ACTOR="${USER:-agent}"

mkdir -p "${BEADS_DIR}"

if [[ ! -f "${ISSUES_FILE}" ]]; then
  touch "${ISSUES_FILE}"
fi

CMD="${1:-list}"
shift || true

# ── List ──────────────────────────────────────────────
cmd_list() {
  echo "═══ Beads Task Graph ═══"
  if [[ ! -s "${ISSUES_FILE}" ]]; then
    echo "  (empty)"
    return
  fi

  python3 -c "
import json, sys
with open('${ISSUES_FILE}') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            status = d.get('status', d.get('type', '?'))
            ts = d.get('timestamp', '?')
            summary = d.get('summary', '(no summary)')
            issue_id = d.get('issue_id', d.get('id', f'#{i}'))
            print(f'  {issue_id:>12}  [{status:>8}]  {ts[:10]}  {summary[:72]}')
        except json.JSONDecodeError:
            print(f'  #{i}  [MALFORMED]  {line[:60]}', file=sys.stderr)
"
}

# ── Show ──────────────────────────────────────────────
cmd_show() {
  local target_id="${1:-}"
  if [[ -z "${target_id}" ]]; then
    echo "Usage: scripts/beads-plan.sh show <id>" >&2
    exit 2
  fi

  python3 -c "
import json
with open('${ISSUES_FILE}') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            iid = d.get('issue_id', d.get('id', ''))
            if '${target_id}' in str(iid):
                print(json.dumps(d, indent=2, sort_keys=True))
        except json.JSONDecodeError:
            pass
"
}

# ── Add ───────────────────────────────────────────────
cmd_add() {
  local summary="${*}"
  if [[ -z "${summary}" ]]; then
    echo "Usage: scripts/beads-plan.sh add <summary>" >&2
    exit 2
  fi

  local issue_id
  issue_id="BEAD-$(date -u +%Y%m%d%H%M%S)"

  python3 -c "
import json
event = {
    'timestamp': '${TIMESTAMP}',
    'type': 'create',
    'status': 'open',
    'issue_id': '${issue_id}',
    'summary': '''${summary}''',
    'actor': '${ACTOR}'
}
print(json.dumps(event, sort_keys=True))
" >> "${ISSUES_FILE}"

  echo "Created: ${issue_id} — ${summary}"
}

# ── Close ─────────────────────────────────────────────
cmd_close() {
  local target_id="${1:-}"
  local reason="${2:-resolved}"
  if [[ -z "${target_id}" ]]; then
    echo "Usage: scripts/beads-plan.sh close <id> [reason]" >&2
    exit 2
  fi

  python3 -c "
import json
event = {
    'timestamp': '${TIMESTAMP}',
    'type': 'close',
    'status': 'closed',
    'issue_id': '${target_id}',
    'summary': '''${reason}''',
    'actor': '${ACTOR}'
}
print(json.dumps(event, sort_keys=True))
" >> "${ISSUES_FILE}"

  echo "Closed: ${target_id} — ${reason}"
}

# ── Stats ─────────────────────────────────────────────
cmd_stats() {
  echo "═══ Beads Stats ═══"
  python3 -c "
import json, collections
counts = collections.Counter()
with open('${ISSUES_FILE}') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            counts[d.get('type', 'unknown')] += 1
        except json.JSONDecodeError:
            counts['malformed'] += 1
total = sum(counts.values())
print(f'  Total entries: {total}')
for k, v in sorted(counts.items()):
    print(f'  {k:>12}: {v}')
"
}

# ── Dispatch ──────────────────────────────────────────
case "${CMD}" in
  list)  cmd_list ;;
  show)  cmd_show "$@" ;;
  add)   cmd_add "$@" ;;
  close) cmd_close "$@" ;;
  stats) cmd_stats ;;
  *)
    echo "Usage: scripts/beads-plan.sh <list|show|add|close|stats>" >&2
    exit 2
    ;;
esac
