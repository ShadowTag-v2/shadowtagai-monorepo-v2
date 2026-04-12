#!/usr/bin/env bash
# ==============================================================================
# ai-test-changed.sh — Portable Test Hook (Affected Tests Only)
# Per Invariant #14: Portable hooks replace vendor-locked CI/CD.
# Per AGENTS.md: Testing: scripts/ai-test-changed.sh (Affected tests only)
# ==============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO_ROOT="$(git rev-parse --show-toplevel)"

echo -e "${YELLOW}═══ AI-TEST-CHANGED ═══${NC}"

# Determine changed files (staged > working > diff against main)
CHANGED=$(git diff --cached --name-only 2>/dev/null || true)
if [ -z "$CHANGED" ]; then
  CHANGED=$(git diff --name-only 2>/dev/null || true)
fi
if [ -z "$CHANGED" ]; then
  CHANGED=$(git diff --name-only origin/main...HEAD 2>/dev/null || true)
fi

if [ -z "$CHANGED" ]; then
  echo -e "  ${GREEN}No changed files detected. Nothing to test.${NC}"
  exit 0
fi

echo -e "  ${YELLOW}Changed files:${NC}"
echo "$CHANGED" | head -20 | sed 's/^/    /'
TOTAL=$(echo "$CHANGED" | wc -l | tr -d ' ')
if [ "$TOTAL" -gt 20 ]; then
  echo "    ... and $((TOTAL - 20)) more"
fi

ERRORS=0

# --- Python Tests ---
PY_CHANGED=$(echo "$CHANGED" | grep '\.py$' || true)
if [ -n "$PY_CHANGED" ]; then
  echo ""
  echo -e "  ${YELLOW}[Python] Running affected tests...${NC}"

  # Find corresponding test files
  TEST_FILES=""
  for f in $PY_CHANGED; do
    base=$(basename "$f" .py)
    dir=$(dirname "$f")
    # Check for test_<name>.py in same dir
    candidate="${dir}/test_${base}.py"
    if [ -f "$REPO_ROOT/$candidate" ]; then
      TEST_FILES="$TEST_FILES $candidate"
    fi
    # Check for tests/ sibling
    candidate="${dir}/tests/test_${base}.py"
    if [ -f "$REPO_ROOT/$candidate" ]; then
      TEST_FILES="$TEST_FILES $candidate"
    fi
    # If the changed file IS a test, include it directly
    if echo "$f" | grep -q 'test_'; then
      TEST_FILES="$TEST_FILES $f"
    fi
  done

  if [ -n "$TEST_FILES" ]; then
    # Deduplicate
    TEST_FILES=$(echo "$TEST_FILES" | tr ' ' '\n' | sort -u | tr '\n' ' ')
    echo "    Test files: $TEST_FILES"
    if python3 -m pytest $TEST_FILES --tb=short -q 2>/dev/null; then
      echo -e "    ${GREEN}Python tests: PASS${NC}"
    else
      echo -e "    ${RED}Python tests: FAIL${NC}"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo -e "    ${YELLOW}No matching test files found. Running syntax check...${NC}"
    for f in $PY_CHANGED; do
      if [ -f "$REPO_ROOT/$f" ]; then
        if python3 -m py_compile "$REPO_ROOT/$f" 2>/dev/null; then
          echo -e "    ${GREEN}✓ $f${NC}"
        else
          echo -e "    ${RED}✗ $f (compile error)${NC}"
          ERRORS=$((ERRORS + 1))
        fi
      fi
    done
  fi
fi

# --- TypeScript/JS Tests ---
TS_CHANGED=$(echo "$CHANGED" | grep -E '\.(ts|tsx|js|jsx)$' | grep -v 'node_modules' || true)
if [ -n "$TS_CHANGED" ]; then
  echo ""
  echo -e "  ${YELLOW}[TypeScript] Checking changed files...${NC}"
  if [ -f "$REPO_ROOT/tsconfig.json" ]; then
    # Type-check only — no full build
    if npx tsc --noEmit 2>/dev/null; then
      echo -e "    ${GREEN}TypeScript type-check: PASS${NC}"
    else
      echo -e "    ${RED}TypeScript type-check: FAIL${NC}"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo -e "    ${YELLOW}No tsconfig.json found. Skipping type-check.${NC}"
  fi
fi

# --- JSON/YAML Syntax ---
JSON_CHANGED=$(echo "$CHANGED" | grep '\.json$' | grep -v 'node_modules\|package-lock\|.lock' || true)
if [ -n "$JSON_CHANGED" ]; then
  echo ""
  echo -e "  ${YELLOW}[JSON] Validating syntax...${NC}"
  for f in $JSON_CHANGED; do
    if [ -f "$REPO_ROOT/$f" ]; then
      if python3 -c "import json; json.load(open('$REPO_ROOT/$f'))" 2>/dev/null; then
        echo -e "    ${GREEN}✓ $f${NC}"
      else
        echo -e "    ${RED}✗ $f (invalid JSON)${NC}"
        ERRORS=$((ERRORS + 1))
      fi
    fi
  done
fi

echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo -e "${RED}═══ TEST-CHANGED: ${ERRORS} FAILURE(S) ═══${NC}"
  exit 1
else
  echo -e "${GREEN}═══ TEST-CHANGED: ALL CLEAR ═══${NC}"
  exit 0
fi
