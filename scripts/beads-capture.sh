#!/usr/bin/env bash
# beads-capture.sh — Ingests a memory bead into the .beads/ journal.
# Usage: beads-capture.sh <type> <title> [description]
#   type: one of issue|fact|decision|event
#   title: short slug (kebab-case)
#   description: optional multi-line body
#
# Examples:
#   beads-capture.sh issue "fix-stripe-webhook" "Webhook signature mismatch on staging"
#   beads-capture.sh fact "firebase-auth-layer2" "MCP server auth is in-memory OAuth2"
#   beads-capture.sh decision "reject-bullmq" "Cloud Tasks is exclusive queue broker"
#   beads-capture.sh event "deploy-counselconduit-v3.2" "Revision 00037-7mf live"
set -euo pipefail

BEADS_DIR="${BEADS_DIR:-.beads}"
ISSUES_FILE="${BEADS_DIR}/issues.jsonl"
EVENTS_FILE="${MEMORY_DIR:-.memory}/events.ndjson"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- Argument validation ------------------------------------------------
TYPE="${1:-}"
TITLE="${2:-}"
DESCRIPTION="${3:-}"

if [[ -z "$TYPE" || -z "$TITLE" ]]; then
  echo "Usage: beads-capture.sh <type> <title> [description]"
  echo "  type: issue | fact | decision | event"
  exit 1
fi

case "$TYPE" in
  issue|fact|decision|event) ;;
  *)
    echo "Error: type must be one of: issue, fact, decision, event"
    exit 1
    ;;
esac

# --- Ensure directories exist -------------------------------------------
mkdir -p "$BEADS_DIR"
mkdir -p "$(dirname "$EVENTS_FILE")"

# --- Generate unique bead ID --------------------------------------------
if command -v uuidgen &>/dev/null; then
  BEAD_ID="$(uuidgen | tr '[:upper:]' '[:lower:]')"
else
  BEAD_ID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
fi

# --- Capture to the appropriate store ------------------------------------
case "$TYPE" in
  issue)
    # Append to .beads/issues.jsonl (Beads-native format)
    ENTRY=$(python3 -c "
import json, sys
print(json.dumps({
    'id': '${BEAD_ID}',
    'type': 'issue',
    'title': sys.argv[1],
    'description': sys.argv[2] if len(sys.argv) > 2 else '',
    'status': 'open',
    'created': '${TIMESTAMP}',
    'labels': [],
    'depends_on': [],
    'blocks': []
}, separators=(',', ':')))
" "$TITLE" "$DESCRIPTION")
    echo "$ENTRY" >> "$ISSUES_FILE"
    echo "✅ Issue captured → $ISSUES_FILE (id: ${BEAD_ID})"
    ;;
  fact|decision)
    # Write to .memory/atoms/<type>/ as a markdown atom
    ATOM_DIR=".memory/atoms"
    case "$TYPE" in
      fact)     ATOM_DIR=".memory/atoms/facts" ;;
      decision) ATOM_DIR=".memory/atoms/decisions" ;;
    esac
    mkdir -p "$ATOM_DIR"
    ATOM_FILE="${ATOM_DIR}/${TITLE}.md"
    cat > "$ATOM_FILE" <<EOF
---
id: ${BEAD_ID}
type: ${TYPE}
created: ${TIMESTAMP}
source: beads-capture
---

# ${TITLE}

${DESCRIPTION}
EOF
    echo "✅ ${TYPE^} captured → $ATOM_FILE"
    ;;
  event)
    # Append to .memory/events.ndjson
    EVENT=$(python3 -c "
import json, sys
print(json.dumps({
    'id': '${BEAD_ID}',
    'type': 'event',
    'title': sys.argv[1],
    'description': sys.argv[2] if len(sys.argv) > 2 else '',
    'timestamp': '${TIMESTAMP}'
}, separators=(',', ':')))
" "$TITLE" "$DESCRIPTION")
    echo "$EVENT" >> "$EVENTS_FILE"
    echo "✅ Event captured → $EVENTS_FILE (id: ${BEAD_ID})"
    ;;
esac
