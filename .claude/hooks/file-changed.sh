#!/bin/bash
# FileChanged hook — fires when watched files change (via chokidar)
# Runs tsc --noEmit + eslint for TS/JS changes (ant-grade verification)
# Validates .env files haven't been corrupted

set -e

INPUT=$(cat)

# Extract changed file info
FILE_INFO=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    hook_input = data.get('hook_input', data)
    path = hook_input.get('path', hook_input.get('filePath', ''))
    event = hook_input.get('event', 'change')
    print(f'{path}|{event}')
except Exception:
    print('|change')
")

FILE_PATH=$(echo "$FILE_INFO" | cut -d'|' -f1)
EVENT_TYPE=$(echo "$FILE_INFO" | cut -d'|' -f2)

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

FILE_EXT="${FILE_PATH##*.}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
LOGDIR="$PROJECT_DIR/.claude/logs"
mkdir -p "$LOGDIR"

echo "[$(date -Iseconds)] FileChanged: $EVENT_TYPE $FILE_PATH" >> "$LOGDIR/file-audit.log"

# =================================================================
# ANT-GRADE VERIFICATION: tsc --noEmit + eslint
# Simulates the ant-mode behavior that forces compilation + error
# detection and avoids false "Done" messages
# =================================================================
case "$FILE_EXT" in
    ts|tsx)
        # TypeScript: run tsc --noEmit if tsconfig exists
        if [ -f "$PROJECT_DIR/tsconfig.json" ] && command -v tsc &>/dev/null; then
            echo "🔍 Running tsc --noEmit for $FILE_PATH..."
            TSC_OUTPUT=$(cd "$PROJECT_DIR" && tsc --noEmit 2>&1 | head -20) || true
            if [ -n "$TSC_OUTPUT" ]; then
                echo "⚠ TypeScript errors detected:" >&2
                echo "$TSC_OUTPUT" >&2
                # Non-blocking — report but don't block
                exit 1
            fi
            echo "✓ TypeScript: no errors"
        fi
        ;;&  # Fall through to also check ESLint

    js|jsx|ts|tsx)
        # ESLint: run on JS/TS files if eslint is available
        if command -v eslint &>/dev/null; then
            echo "🔍 Running eslint on $FILE_PATH..."
            ESLINT_OUTPUT=$(eslint "$FILE_PATH" --no-error-on-unmatched-pattern 2>&1 | head -20) || true
            if [ -n "$ESLINT_OUTPUT" ]; then
                echo "⚠ ESLint issues:" >&2
                echo "$ESLINT_OUTPUT" >&2
                exit 1
            fi
            echo "✓ ESLint: clean"
        fi
        ;;

    py)
        # Python: ruff check if available
        if command -v ruff &>/dev/null; then
            echo "🔍 Running ruff check on $FILE_PATH..."
            RUFF_OUTPUT=$(ruff check "$FILE_PATH" 2>&1 | head -20) || true
            if [ -n "$RUFF_OUTPUT" ]; then
                echo "⚠ Ruff issues:" >&2
                echo "$RUFF_OUTPUT" >&2
                exit 1
            fi
            echo "✓ Ruff: clean"
        fi
        ;;

    env|envrc)
        # .env files: check for accidental secret exposure
        if grep -qE '(password|secret|token|api.?key)=.{8,}' "$FILE_PATH" 2>/dev/null; then
            echo "⚠ WARNING: Potential secrets detected in $FILE_PATH" >&2
            echo "Review before committing." >&2
            exit 1
        fi
        ;;
esac

exit 0
