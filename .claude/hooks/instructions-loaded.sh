#!/bin/bash
# InstructionsLoaded hook — fires when CLAUDE.md/rules are loaded
# Validates instruction integrity and logs load events

set -e

INPUT=$(cat)

# Extract the instruction source info
INSTRUCTION_INFO=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    hook_input = data.get('hook_input', data)
    source = hook_input.get('source', 'unknown')
    path = hook_input.get('path', '')
    print(f'{source}|{path}')
except Exception:
    print('unknown|')
")

SOURCE=$(echo "$INSTRUCTION_INFO" | cut -d'|' -f1)
INST_PATH=$(echo "$INSTRUCTION_INFO" | cut -d'|' -f2)

# Log load event for audit trail
LOGDIR="${CLAUDE_PROJECT_DIR:-.}/.claude/logs"
mkdir -p "$LOGDIR"
echo "[$(date -Iseconds)] InstructionsLoaded: source=$SOURCE path=$INST_PATH" >> "$LOGDIR/instructions-audit.log"

# Validate CLAUDE.md brevity (30-70 lines optimal, max 73 for ours)
if [ -n "$INST_PATH" ] && [ -f "$INST_PATH" ]; then
    LINE_COUNT=$(wc -l < "$INST_PATH" 2>/dev/null | tr -d ' ')
    if [ "$LINE_COUNT" -gt 100 ]; then
        echo "⚠ CLAUDE.md is $LINE_COUNT lines — target 30-70 for optimal cache efficiency" >&2
        # Non-blocking warning (exit 1)
        exit 1
    fi
fi

# Sync CLAUDE.md → AGENTS.md if source is project CLAUDE.md
if [ "$SOURCE" = "project" ] && [ -f "${CLAUDE_PROJECT_DIR:-.}/.claude/CLAUDE.md" ]; then
    if [ -f "${CLAUDE_PROJECT_DIR:-.}/AGENTS.md" ]; then
        # Only sync if CLAUDE.md is newer
        if [ "${CLAUDE_PROJECT_DIR:-.}/.claude/CLAUDE.md" -nt "${CLAUDE_PROJECT_DIR:-.}/AGENTS.md" ]; then
            cp "${CLAUDE_PROJECT_DIR:-.}/.claude/CLAUDE.md" "${CLAUDE_PROJECT_DIR:-.}/AGENTS.md"
            echo "✓ Synced CLAUDE.md → AGENTS.md"
        fi
    fi
fi

exit 0
