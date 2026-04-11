#!/usr/bin/env bash
# stop-quality-gate.sh — ECC-style Stop hook quality gate
# Source: everything-claude-code hooks/stop/format-typecheck.sh
# Adapted for Antigravity monorepo
#
# Runs at session Stop to batch-verify all edited files:
# 1. TypeScript type-check (tsc --noEmit)
# 2. ESLint on changed JS/TS files
# 3. Python type hints (mypy) if relevant
# This implements the "Ant-grade" verification from Rule 33.

set -euo pipefail

# Read hook input from stdin
INPUT=$(cat)

CWD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || echo "$(pwd)")

ERRORS=""
WARNINGS=""

# --- TypeScript verification ---
if [ -f "$CWD/tsconfig.json" ]; then
  TSC_OUTPUT=$(cd "$CWD" && npx tsc --noEmit 2>&1 || true)
  TSC_ERROR_COUNT=$(echo "$TSC_OUTPUT" | grep -c "error TS" || echo "0")
  
  if [ "$TSC_ERROR_COUNT" -gt 0 ]; then
    ERRORS="${ERRORS}\n❌ TypeScript: ${TSC_ERROR_COUNT} type errors found"
    # Include first 5 errors for context
    TSC_FIRST=$(echo "$TSC_OUTPUT" | grep "error TS" | head -5)
    ERRORS="${ERRORS}\n${TSC_FIRST}"
  fi
fi

# --- ESLint on staged/changed files ---
CHANGED_TS=$(cd "$CWD" && git diff --name-only HEAD 2>/dev/null | grep -E '\.(ts|tsx|js|jsx)$' || true)
if [ -n "$CHANGED_TS" ] && [ -f "$CWD/.eslintrc.json" -o -f "$CWD/.eslintrc.js" -o -f "$CWD/eslint.config.js" -o -f "$CWD/eslint.config.mjs" ]; then
  ESLINT_OUTPUT=$(cd "$CWD" && echo "$CHANGED_TS" | xargs npx eslint --no-error-on-unmatched-pattern 2>&1 || true)
  ESLINT_ERROR_COUNT=$(echo "$ESLINT_OUTPUT" | grep -cE "^\s+[0-9]+:[0-9]+\s+error" || echo "0")
  
  if [ "$ESLINT_ERROR_COUNT" -gt 0 ]; then
    WARNINGS="${WARNINGS}\n⚠️ ESLint: ${ESLINT_ERROR_COUNT} lint errors in changed files"
  fi
fi

# --- Python type check ---
CHANGED_PY=$(cd "$CWD" && git diff --name-only HEAD 2>/dev/null | grep -E '\.py$' || true)
if [ -n "$CHANGED_PY" ] && command -v mypy &>/dev/null; then
  # Only check if mypy is available and there's a mypy.ini or pyproject.toml
  if [ -f "$CWD/mypy.ini" -o -f "$CWD/pyproject.toml" ]; then
    MYPY_OUTPUT=$(cd "$CWD" && echo "$CHANGED_PY" | xargs mypy --ignore-missing-imports 2>&1 || true)
    MYPY_ERROR_COUNT=$(echo "$MYPY_OUTPUT" | grep -c "error:" || echo "0")
    
    if [ "$MYPY_ERROR_COUNT" -gt 0 ]; then
      WARNINGS="${WARNINGS}\n⚠️ mypy: ${MYPY_ERROR_COUNT} type errors in changed Python files"
    fi
  fi
fi

# --- Build output ---
if [ -n "$ERRORS" ] || [ -n "$WARNINGS" ]; then
  CONTEXT="🔍 Stop Quality Gate Results:"
  [ -n "$ERRORS" ] && CONTEXT="${CONTEXT}\n${ERRORS}"
  [ -n "$WARNINGS" ] && CONTEXT="${CONTEXT}\n${WARNINGS}"
  
  python3 -c "
import json
output = {
    'hookSpecificOutput': {
        'hookEventName': 'PostToolUse',
        'additionalContext': '''${CONTEXT}'''
    }
}
print(json.dumps(output))
"
else
  echo '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"✅ Stop quality gate passed — no type errors or lint issues."}}'
fi
