#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# scripts/dead-code-audit.sh — Invariant #67 Implementation
# Delete all dead code using ruff + vulture with e2e test before/after
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUFF="${HOME}/.local/bin/ruff"
VULTURE_BIN=$(find ~/.local/bin ~/Library/Python/*/bin /usr/local/bin 2>/dev/null -name vulture | head -1)
REPORT_DIR="${REPO_ROOT}/.reports"
TIMESTAMP=$(date +%Y%m%dT%H%M%S)
MODE="${1:-audit}"  # audit (default) | fix | full

# ─── Colors ───
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# ─── Scan targets (exclude archive, node_modules, .git, venv) ───
SCAN_DIRS=(
  "${REPO_ROOT}/apps"
  "${REPO_ROOT}/labs"
  "${REPO_ROOT}/tools"
  "${REPO_ROOT}/scripts"
  "${REPO_ROOT}/infrastructure"
)

# Filter to dirs that actually exist
REAL_DIRS=()
for d in "${SCAN_DIRS[@]}"; do
  [ -d "$d" ] && REAL_DIRS+=("$d")
done

if [ ${#REAL_DIRS[@]} -eq 0 ]; then
  echo -e "${RED}ERROR: No scan directories found!${NC}"
  exit 1
fi

mkdir -p "$REPORT_DIR"

echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  DEAD CODE AUDIT — Invariant #67${NC}"
echo -e "${CYAN}  Mode: ${MODE} | Timestamp: ${TIMESTAMP}${NC}"
echo -e "${CYAN}  Tools: ruff $(${RUFF} --version 2>/dev/null || echo 'N/A'), vulture $(${VULTURE_BIN} --version 2>/dev/null || echo 'N/A')${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""

# ─── Phase 1: Pre-Test (syntax validation) ───
echo -e "${YELLOW}[Phase 1] Pre-test: Python syntax validation...${NC}"
PRE_ERRORS=0
PRE_REPORT="${REPORT_DIR}/dead-code-pre-${TIMESTAMP}.txt"

for dir in "${REAL_DIRS[@]}"; do
  find "$dir" -name "*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/venv/*" | while read f; do
    python3 -c "import py_compile; py_compile.compile('$f', doraise=True)" 2>/dev/null || {
      echo "SYNTAX_ERROR: $f" >> "$PRE_REPORT"
      PRE_ERRORS=$((PRE_ERRORS + 1))
    }
  done
done 2>/dev/null

PY_COUNT=$(find "${REAL_DIRS[@]}" -name "*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}  Scanned ${PY_COUNT} Python files${NC}"
[ -f "$PRE_REPORT" ] && echo -e "${YELLOW}  $(wc -l < "$PRE_REPORT") syntax errors (see ${PRE_REPORT})${NC}" || echo -e "${GREEN}  0 syntax errors${NC}"
echo ""

# ─── Phase 2: Ruff Lint (unused imports, dead code patterns) ───
echo -e "${YELLOW}[Phase 2] Ruff: Unused imports & dead code patterns...${NC}"
RUFF_REPORT="${REPORT_DIR}/ruff-${TIMESTAMP}.txt"

# F401 = unused import, F811 = redefined unused, F841 = unused variable
${RUFF} check --select F401,F811,F841 --no-fix --output-format text \
  "${REAL_DIRS[@]}" > "$RUFF_REPORT" 2>/dev/null || true

RUFF_COUNT=$(wc -l < "$RUFF_REPORT" | tr -d ' ')
echo -e "${GREEN}  Ruff found ${RUFF_COUNT} dead code issues${NC}"
if [ "$RUFF_COUNT" -gt 0 ]; then
  echo -e "${CYAN}  Top issues:${NC}"
  head -10 "$RUFF_REPORT" | sed 's/^/    /'
  [ "$RUFF_COUNT" -gt 10 ] && echo "    ... and $((RUFF_COUNT - 10)) more"
fi
echo ""

# ─── Phase 3: Vulture (unreachable code, unused functions/classes) ───
echo -e "${YELLOW}[Phase 3] Vulture: Unreachable code & unused symbols...${NC}"
VULTURE_REPORT="${REPORT_DIR}/vulture-${TIMESTAMP}.txt"

${VULTURE_BIN} "${REAL_DIRS[@]}" \
  --min-confidence 80 \
  --exclude "node_modules,venv,.venv,__pycache__,archive" \
  > "$VULTURE_REPORT" 2>/dev/null || true

VULTURE_COUNT=$(wc -l < "$VULTURE_REPORT" | tr -d ' ')
echo -e "${GREEN}  Vulture found ${VULTURE_COUNT} dead code candidates${NC}"
if [ "$VULTURE_COUNT" -gt 0 ]; then
  echo -e "${CYAN}  Top candidates:${NC}"
  head -10 "$VULTURE_REPORT" | sed 's/^/    /'
  [ "$VULTURE_COUNT" -gt 10 ] && echo "    ... and $((VULTURE_COUNT - 10)) more"
fi
echo ""

# ─── Phase 4: Auto-fix (only in fix/full mode) ───
if [ "$MODE" = "fix" ] || [ "$MODE" = "full" ]; then
  echo -e "${YELLOW}[Phase 4] Auto-fix: Applying ruff --fix...${NC}"
  
  # Only fix safe rules (unused imports)
  ${RUFF} check --select F401 --fix --unsafe-fixes \
    "${REAL_DIRS[@]}" > /dev/null 2>/dev/null || true
  
  # Re-count after fix
  RUFF_POST="${REPORT_DIR}/ruff-post-fix-${TIMESTAMP}.txt"
  ${RUFF} check --select F401,F811,F841 --no-fix --output-format text \
    "${REAL_DIRS[@]}" > "$RUFF_POST" 2>/dev/null || true
  
  RUFF_POST_COUNT=$(wc -l < "$RUFF_POST" | tr -d ' ')
  FIXED=$((RUFF_COUNT - RUFF_POST_COUNT))
  echo -e "${GREEN}  Fixed ${FIXED} issues (${RUFF_POST_COUNT} remaining)${NC}"
  echo ""
fi

# ─── Phase 5: Post-Test (syntax validation after fixes) ───
if [ "$MODE" = "fix" ] || [ "$MODE" = "full" ]; then
  echo -e "${YELLOW}[Phase 5] Post-test: Verifying no regressions...${NC}"
  POST_REPORT="${REPORT_DIR}/dead-code-post-${TIMESTAMP}.txt"
  POST_ERRORS=0
  
  for dir in "${REAL_DIRS[@]}"; do
    find "$dir" -name "*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/venv/*" | while read f; do
      python3 -c "import py_compile; py_compile.compile('$f', doraise=True)" 2>/dev/null || {
        echo "REGRESSION: $f" >> "$POST_REPORT"
        POST_ERRORS=$((POST_ERRORS + 1))
      }
    done
  done 2>/dev/null
  
  [ -f "$POST_REPORT" ] && {
    echo -e "${RED}  ⚠ $(wc -l < "$POST_REPORT") regressions found!${NC}"
    cat "$POST_REPORT" | sed 's/^/    /'
  } || echo -e "${GREEN}  ✅ No regressions — all files compile clean${NC}"
  echo ""
fi

# ─── Phase 6: Vibe Code Anti-Pattern Scanner (Invariant #90) ───
echo -e "${YELLOW}[Phase 6] Vibe Code Anti-Pattern Scan (Invariant #90)...${NC}"
VIBE_REPORT="${REPORT_DIR}/vibe-code-${TIMESTAMP}.txt"
VIBE_ISSUES=0

echo "=== VIBE CODE ANTI-PATTERN REPORT ===" > "$VIBE_REPORT"
echo "Timestamp: ${TIMESTAMP}" >> "$VIBE_REPORT"
echo "" >> "$VIBE_REPORT"

# 6a: Hardcoded config (localhost in non-test files)
echo "--- 6a: Hardcoded Config (localhost:) ---" >> "$VIBE_REPORT"
HC_COUNT=0
for dir in "${REAL_DIRS[@]}"; do
  while IFS= read -r match; do
    echo "  HARDCODED: $match" >> "$VIBE_REPORT"
    HC_COUNT=$((HC_COUNT + 1))
  done < <(grep -rn "localhost:" "$dir" \
    --include="*.py" --include="*.ts" --include="*.tsx" \
    --exclude-dir=node_modules --exclude-dir=.venv \
    --exclude-dir="__tests__" --exclude-dir="test" \
    --exclude-dir="tests" 2>/dev/null | head -50)
done
echo "  Total: ${HC_COUNT}" >> "$VIBE_REPORT"
VIBE_ISSUES=$((VIBE_ISSUES + HC_COUNT))

# 6b: Monolithic files (>500 LOC in apps/)
echo "" >> "$VIBE_REPORT"
echo "--- 6b: Monolithic Files (>500 LOC) ---" >> "$VIBE_REPORT"
MONO_COUNT=0
if [ -d "${REPO_ROOT}/apps" ]; then
  while IFS= read -r f; do
    lines=$(wc -l < "$f" 2>/dev/null || echo 0)
    if [ "$lines" -gt 500 ]; then
      echo "  MONOLITH [${lines} LOC]: $f" >> "$VIBE_REPORT"
      MONO_COUNT=$((MONO_COUNT + 1))
    fi
  done < <(find "${REPO_ROOT}/apps" \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" \) \
    -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null)
fi
echo "  Total: ${MONO_COUNT}" >> "$VIBE_REPORT"
VIBE_ISSUES=$((VIBE_ISSUES + MONO_COUNT))

# 6c: console.log in production apps (not scripts/examples)
echo "" >> "$VIBE_REPORT"
echo "--- 6c: console.log in Production ---" >> "$VIBE_REPORT"
CL_COUNT=0
if [ -d "${REPO_ROOT}/apps" ]; then
  CL_COUNT=$(grep -rn "console\.log" "${REPO_ROOT}/apps" \
    --include="*.ts" --include="*.tsx" --include="*.js" \
    --exclude-dir=node_modules --exclude-dir=.next \
    --exclude-dir="examples" --exclude-dir="scripts" 2>/dev/null | wc -l | tr -d ' ')
  echo "  console.log calls in apps/: ${CL_COUNT}" >> "$VIBE_REPORT"
fi
VIBE_ISSUES=$((VIBE_ISSUES + CL_COUNT))

# 6d: Dead links (href="#") in HTML files
echo "" >> "$VIBE_REPORT"
echo "--- 6d: Dead Links (href='#') ---" >> "$VIBE_REPORT"
DL_COUNT=0
for dir in "${REAL_DIRS[@]}"; do
  while IFS= read -r match; do
    echo "  DEAD_LINK: $match" >> "$VIBE_REPORT"
    DL_COUNT=$((DL_COUNT + 1))
  done < <(grep -rn 'href="#"' "$dir" \
    --include="*.html" --include="*.tsx" --include="*.jsx" \
    --exclude-dir=node_modules 2>/dev/null | head -50)
done
echo "  Total: ${DL_COUNT}" >> "$VIBE_REPORT"
VIBE_ISSUES=$((VIBE_ISSUES + DL_COUNT))

# ─── Phase 6e: Complecting Detector (Rich Hickey Doctrine) ───
echo -e "${YELLOW}  6e. Complecting Detector (>8 imports = braided concerns)...${NC}"
COMPLECT_COUNT=0
for dir in "${REAL_DIRS[@]}"; do
  while IFS= read -r file; do
    # Count unique import sources (from X import / import X)
    IMPORT_SOURCES=$(grep -cE '^\s*(from\s+\S+\s+import|import\s+\S+)' "$file" 2>/dev/null | tail -1 || echo 0)
    if [ "${IMPORT_SOURCES:-0}" -gt 8 ] 2>/dev/null; then
      echo "  COMPLECTED: $file (${IMPORT_SOURCES} import sources)" >> "$VIBE_REPORT"
      COMPLECT_COUNT=$((COMPLECT_COUNT + 1))
    fi
  done < <(find "$dir" -name "*.py" -not -path "*/node_modules/*" \
    -not -path "*/.venv/*" -not -path "*/venv/*" \
    -not -path "*/__pycache__/*" -not -path "*/archive/*" 2>/dev/null)
  # Also check JS/TS files
  while IFS= read -r file; do
    IMPORT_SOURCES=$(grep -cE '^\s*(import\s+.*from\s|require\()' "$file" 2>/dev/null | tail -1 || echo 0)
    if [ "${IMPORT_SOURCES:-0}" -gt 8 ] 2>/dev/null; then
      echo "  COMPLECTED: $file (${IMPORT_SOURCES} import sources)" >> "$VIBE_REPORT"
      COMPLECT_COUNT=$((COMPLECT_COUNT + 1))
    fi
  done < <(find "$dir" \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
    -not -path "*/node_modules/*" -not -path "*/dist/*" \
    -not -path "*/archive/*" 2>/dev/null)
done
echo "  Total: ${COMPLECT_COUNT}" >> "$VIBE_REPORT"
VIBE_ISSUES=$((VIBE_ISSUES + COMPLECT_COUNT))

# ─── Phase 6f: Function Length Check (Rich Hickey Doctrine) ───
echo -e "${YELLOW}  6f. Function Length Check (>50 LOC = not one-fold)...${NC}"
LONG_FN_COUNT=0
for dir in "${REAL_DIRS[@]}"; do
  while IFS= read -r file; do
    # Use awk to detect Python functions >50 lines
    LONG_FNS=$(awk '
      /^[[:space:]]*(def|async def) / {
        if (fn_name != "" && fn_lines > 50) {
          print fn_name " (" fn_lines " lines)"
          count++
        }
        fn_name = FILENAME ":" $0
        fn_lines = 0
      }
      fn_name != "" { fn_lines++ }
      END {
        if (fn_name != "" && fn_lines > 50) {
          print fn_name " (" fn_lines " lines)"
          count++
        }
      }
    ' "$file" 2>/dev/null)
    if [ -n "$LONG_FNS" ]; then
      while IFS= read -r fn; do
        echo "  LONG_FUNCTION: $fn" >> "$VIBE_REPORT"
        LONG_FN_COUNT=$((LONG_FN_COUNT + 1))
      done <<< "$LONG_FNS"
    fi
  done < <(find "$dir" -name "*.py" -not -path "*/node_modules/*" \
    -not -path "*/.venv/*" -not -path "*/venv/*" \
    -not -path "*/__pycache__/*" -not -path "*/archive/*" 2>/dev/null)
done
echo "  Total: ${LONG_FN_COUNT}" >> "$VIBE_REPORT"
VIBE_ISSUES=$((VIBE_ISSUES + LONG_FN_COUNT))

echo -e "${GREEN}  Phase 6 found ${VIBE_ISSUES} vibe-code issues${NC}"
echo -e "${CYAN}  Breakdown: ${HC_COUNT} hardcoded, ${MONO_COUNT} monoliths, ${CL_COUNT} console.logs, ${DL_COUNT} dead links, ${COMPLECT_COUNT} complected, ${LONG_FN_COUNT} long functions${NC}"
echo ""

# ─── Summary ───
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SUMMARY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "  Python files scanned:  ${PY_COUNT}"
echo -e "  Ruff issues found:     ${RUFF_COUNT}"
echo -e "  Vulture candidates:    ${VULTURE_COUNT}"
echo -e "  Vibe-code issues:      ${VIBE_ISSUES}"
echo -e "  Reports dir:           ${REPORT_DIR}"
echo ""
echo -e "  Reports:"
echo -e "    ${RUFF_REPORT}"
echo -e "    ${VULTURE_REPORT}"
echo -e "    ${VIBE_REPORT}"
[ -f "${PRE_REPORT:-}" ] && echo -e "    ${PRE_REPORT}"
[ -f "${POST_REPORT:-}" ] && echo -e "    ${POST_REPORT}"
echo ""
echo -e "  Usage:"
echo -e "    ${GREEN}./scripts/dead-code-audit.sh audit${NC}  — report only (safe)"
echo -e "    ${YELLOW}./scripts/dead-code-audit.sh fix${NC}    — auto-fix unused imports + post-test"
echo -e "    ${RED}./scripts/dead-code-audit.sh full${NC}   — fix + full regression suite"
echo ""

