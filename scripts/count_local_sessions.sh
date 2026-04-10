#!/usr/bin/env bash
# count_local_sessions.sh — audit local Claude sessions vs manifest
# Usage: bash scripts/count_local_sessions.sh

set -euo pipefail

MANIFEST="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/apps/ShadowTag-v2_stack/nascent-apollo/Docs/TELEPORT_MANIFEST.json"
CLAUDE_PROJECTS="$HOME/.claude/projects/-Users-pikeymickey"

echo "=== Claude Session Audit ==="
echo ""

# Local project entries
LOCAL_COUNT=0
if [[ -d "$CLAUDE_PROJECTS" ]]; then
    LOCAL_COUNT=$(ls "$CLAUDE_PROJECTS" | wc -l | tr -d ' ')
    echo "Local ~/.claude/projects entries : $LOCAL_COUNT"
    echo "  (JSONL files + dirs):"
    ls "$CLAUDE_PROJECTS" | head -10
    [[ $LOCAL_COUNT -gt 10 ]] && echo "  ... and $((LOCAL_COUNT - 10)) more"
else
    echo "WARNING: $CLAUDE_PROJECTS not found"
fi

echo ""

# Manifest count
MANIFEST_COUNT=0
if [[ -f "$MANIFEST" ]]; then
    MANIFEST_COUNT=$(python3 -c "
import json
d = json.load(open('$MANIFEST'))
print(d['meta']['total_unique_sessions'])
")
    echo "Manifest total_unique_sessions  : $MANIFEST_COUNT"
    echo "Manifest date                   : $(python3 -c "import json; d=json.load(open('$MANIFEST')); print(d['meta']['date'])")"
    echo ""
    echo "Groups:"
    python3 -c "
import json
d = json.load(open('$MANIFEST'))
for g, v in sorted(d['groups'].items(), key=lambda x: x[1]['priority']):
    print(f'  P{v[\"priority\"]} {g}: {v[\"count\"]} sessions')
"
else
    echo "WARNING: manifest not found at $MANIFEST"
    echo "Run: python scripts/session_manifest_builder.py Docs/raw_sessions.txt"
fi

echo ""

# Ingest status
if [[ -f "$MANIFEST" ]]; then
    python3 -c "
import json
d = json.load(open('$MANIFEST'))
status = d.get('ingest_status', {})
if not status:
    print('Ingest status: no sessions ingested yet')
else:
    by_status = {}
    for v in status.values():
        s = v.get('status','unknown')
        by_status[s] = by_status.get(s, 0) + 1
    print('Ingest status:')
    for s, n in sorted(by_status.items()):
        print(f'  {s}: {n}')
"
fi

echo ""
echo "=== To ingest Judge sessions ==="
echo "  ShadowTag-v2_DRY_RUN=1 python scripts/session_ingestor.py --group JUDGE_LEVEL"
echo ""
echo "=== To rebuild manifest ==="
echo "  python scripts/session_manifest_builder.py Docs/raw_sessions.txt --merge"
