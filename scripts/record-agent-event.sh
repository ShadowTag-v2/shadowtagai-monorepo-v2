#!/usr/bin/env bash
set -euo pipefail

# record-agent-event.sh — Monorepo OS Evidence Recorder
#
# Appends a structured event to the appropriate truth file:
#   - .memory/events.ndjson       (knowledge mutations)
#   - .beads/issues.jsonl         (task/issue mutations)
#   - .agent/evidence/            (push/deploy evidence packets)
#
# Usage:
#   scripts/record-agent-event.sh memory  <type> <summary> [--atom <path>]
#   scripts/record-agent-event.sh beads   <type> <summary> [--id <issue_id>]
#   scripts/record-agent-event.sh evidence <type> <summary> [--file <json_path>]
#
# Examples:
#   scripts/record-agent-event.sh memory create "Added doctrine on upload policy" --atom .memory/atoms/upload-policy.md
#   scripts/record-agent-event.sh beads  close  "Resolved lint failures" --id ISSUE-042
#   scripts/record-agent-event.sh evidence push  "Pushed 3 commits to main"
#
# Referenced by: truth_surfaces.yaml, MONOREPO_OS.md, tool_contracts/

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

SUBSYSTEM="${1:-}"
EVENT_TYPE="${2:-}"
SUMMARY="${3:-}"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
ACTOR="${USER:-agent}"

if [[ -z "${SUBSYSTEM}" || -z "${EVENT_TYPE}" || -z "${SUMMARY}" ]]; then
  echo "Usage: scripts/record-agent-event.sh <memory|beads|evidence> <type> <summary> [options]" >&2
  exit 2
fi

# Parse optional flags
ATOM_PATH=""
ISSUE_ID=""
EVIDENCE_FILE=""
shift 3
while [[ $# -gt 0 ]]; do
  case "$1" in
    --atom) ATOM_PATH="${2:-}"; shift 2 ;;
    --id)   ISSUE_ID="${2:-}"; shift 2 ;;
    --file) EVIDENCE_FILE="${2:-}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

# --- Memory subsystem ---
record_memory() {
  local target="${ROOT}/.memory/events.ndjson"
  mkdir -p "$(dirname "${target}")"

  python3 -c "
import json, sys
event = {
    'timestamp': '${TIMESTAMP}',
    'type': '${EVENT_TYPE}',
    'summary': '''${SUMMARY}''',
    'actor': '${ACTOR}',
    'atom': '${ATOM_PATH}' or None
}
# Remove None values
event = {k: v for k, v in event.items() if v is not None}
print(json.dumps(event, sort_keys=True))
" >> "${target}"

  echo "Recorded memory event: ${EVENT_TYPE} → ${target}"
}

# --- Beads subsystem ---
record_beads() {
  local target="${ROOT}/.beads/issues.jsonl"
  mkdir -p "$(dirname "${target}")"

  python3 -c "
import json
event = {
    'timestamp': '${TIMESTAMP}',
    'type': '${EVENT_TYPE}',
    'summary': '''${SUMMARY}''',
    'actor': '${ACTOR}',
    'issue_id': '${ISSUE_ID}' or None
}
event = {k: v for k, v in event.items() if v is not None}
print(json.dumps(event, sort_keys=True))
" >> "${target}"

  echo "Recorded beads event: ${EVENT_TYPE} → ${target}"
}

# --- Evidence subsystem ---
record_evidence() {
  local evidence_dir="${ROOT}/.agent/evidence"
  local ts_slug
  ts_slug="$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "${evidence_dir}"

  if [[ -n "${EVIDENCE_FILE}" && -f "${EVIDENCE_FILE}" ]]; then
    cp "${EVIDENCE_FILE}" "${evidence_dir}/${ts_slug}-${EVENT_TYPE}.json"
    echo "Copied evidence file: ${evidence_dir}/${ts_slug}-${EVENT_TYPE}.json"
  else
    python3 -c "
import json, pathlib
event = {
    'timestamp': '${TIMESTAMP}',
    'type': '${EVENT_TYPE}',
    'summary': '''${SUMMARY}''',
    'actor': '${ACTOR}'
}
path = pathlib.Path('${evidence_dir}/${ts_slug}-${EVENT_TYPE}.json')
path.write_text(json.dumps(event, indent=2, sort_keys=True))
print(path)
"
    echo "Recorded evidence event: ${evidence_dir}/${ts_slug}-${EVENT_TYPE}.json"
  fi
}

# --- Dispatch ---
case "${SUBSYSTEM}" in
  memory)   record_memory ;;
  beads)    record_beads ;;
  evidence) record_evidence ;;
  *)
    echo "Unknown subsystem: ${SUBSYSTEM}" >&2
    echo "Valid: memory, beads, evidence" >&2
    exit 2
    ;;
esac
