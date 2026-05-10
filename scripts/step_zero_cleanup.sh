#!/usr/bin/env bash
# step_zero_cleanup.sh — AST Nullifier
# Rich Hickey doctrine: Step 0 of any refactor is DELETION.
# V22 Pruned Singularity: vulture removed. ruff F401/F841 handles dead code.
# Run this BEFORE editing any file >300 LOC.
#
# Usage: ./scripts/step_zero_cleanup.sh [file_or_directory]
# If no argument, runs on entire repo Python + JS/TS.

set -euo pipefail

TARGET="${1:-.}"

echo "═══════════════════════════════════════════════"
echo "  STEP ZERO — AST Nullifier (V22 Pruned)"
echo "  Target: ${TARGET}"
echo "  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "═══════════════════════════════════════════════"

# --- Phase 1: Python dead code (ruff) ---
echo ""
echo "▶ Phase 1: ruff --fix (Python dead code + style)"
if command -v ruff &>/dev/null; then
    ruff check --fix --unsafe-fixes --select F401,F811,F841 "${TARGET}" 2>&1 || true
    echo "  ✓ ruff dead-code pass complete"
else
    echo "  ⚠ ruff not found — skipping"
fi

# --- Phase 2: JS/TS dead code (biome) ---
echo ""
echo "▶ Phase 2: biome check (JS/TS)"
if command -v biome &>/dev/null; then
    biome check --apply "${TARGET}" 2>&1 || true
    echo "  ✓ biome pass complete"
elif [ -f "node_modules/.bin/biome" ]; then
    node_modules/.bin/biome check --apply "${TARGET}" 2>&1 || true
    echo "  ✓ biome (local) pass complete"
else
    echo "  ⚠ biome not found — skipping JS/TS cleanup"
fi

# --- Phase 3: Large file warning ---
echo ""
echo "▶ Phase 3: Large file audit (>300 LOC Python)"
if [ -d "${TARGET}" ]; then
    LARGE_FILES=$(find "${TARGET}" -name "*.py" -not -path "*/.*" -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/venv/*" -exec awk 'END { if (NR > 300) print FILENAME ": " NR " lines" }' {} \; 2>/dev/null || true)
else
    LINE_COUNT=$(wc -l < "${TARGET}" 2>/dev/null || echo "0")
    if [ "${LINE_COUNT}" -gt 300 ]; then
        LARGE_FILES="${TARGET}: ${LINE_COUNT} lines"
    else
        LARGE_FILES=""
    fi
fi

if [ -n "${LARGE_FILES}" ]; then
    echo "  ⚠ Files exceeding 300 LOC ceiling:"
    echo "${LARGE_FILES}" | sed 's/^/    /'
    echo ""
    echo "  → Consider splitting before editing."
else
    echo "  ✓ No files exceed 300 LOC ceiling"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "  STEP ZERO COMPLETE (V22 Pruned Triad)"
echo "═══════════════════════════════════════════════"
