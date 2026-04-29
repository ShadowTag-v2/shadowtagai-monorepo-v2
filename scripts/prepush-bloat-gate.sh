#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# scripts/prepush-bloat-gate.sh — Repository Bloat Gate
# Prevents accidental push of oversized files and binary blobs.
#
# Exit Codes:
#   0 — Repo passes all bloat checks
#   1 — Bloat detected, push blocked
#
# Usage: bash scripts/prepush-bloat-gate.sh [--fast]
# ═══════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

FAST=false
[[ "${1:-}" == "--fast" ]] && FAST=true

FAIL=0
WARN=0
gate_pass() { printf "  ✓ %s\n" "$1"; }
gate_fail() { FAIL=$((FAIL + 1)); printf "  ✗ %s\n" "$1"; }
gate_warn() { WARN=$((WARN + 1)); printf "  ⚠ %s\n" "$1"; }

echo "═══ Pre-Push Bloat Gate ═══"
echo ""

# ── Check 1: Large files staged (>5MB) ──
echo "── Check 1: Large Staged Files (>5MB) ──"
MAX_FILE_KB=5120  # 5MB
LARGE_FILES=0
while IFS= read -r staged_file; do
  [[ -z "$staged_file" ]] && continue
  if [ -f "$staged_file" ]; then
    FILE_KB=$(du -k "$staged_file" 2>/dev/null | cut -f1)
    FILE_KB=${FILE_KB:-0}
    if [ "$FILE_KB" -gt "$MAX_FILE_KB" ] 2>/dev/null; then
      gate_fail "Large file: $staged_file (${FILE_KB}KB)"
      LARGE_FILES=$((LARGE_FILES + 1))
    fi
  fi
done < <(git diff --cached --name-only 2>/dev/null || true)

if [ "$LARGE_FILES" -eq 0 ]; then
  gate_pass "No staged files exceed 5MB"
fi

# ── Check 2: Banned file extensions ──
echo "── Check 2: Banned Extensions ──"
BANNED_EXTS="\.zip$|\.tar\.gz$|\.tar\.bz2$|\.rar$|\.7z$|\.exe$|\.dll$|\.so$|\.dylib$|\.whl$|\.egg$|\.pkl$|\.h5$|\.hdf5$|\.onnx$|\.pt$|\.pth$|\.safetensors$|\.bin$|\.model$|\.ckpt$"
BANNED_FOUND=0

if $FAST; then
  # Fast mode: only check staged files
  BANNED_STAGED=$(git diff --cached --name-only 2>/dev/null | { grep -E "$BANNED_EXTS" || true; })
else
  # Full mode: check all tracked files
  BANNED_STAGED=$(git ls-files 2>/dev/null | { grep -E "$BANNED_EXTS" || true; })
fi

if [ -n "$BANNED_STAGED" ]; then
  while IFS= read -r bf; do
    [[ -z "$bf" ]] && continue
    gate_fail "Banned extension: $bf"
    BANNED_FOUND=$((BANNED_FOUND + 1))
  done <<< "$BANNED_STAGED"
fi

if [ "$BANNED_FOUND" -eq 0 ]; then
  gate_pass "No banned extensions detected"
fi

# ── Check 3: Bloated directories (>50MB) ──
echo "── Check 3: Bloated Directories ──"
BLOAT_DIRS=("node_modules" ".venv" "dist" "__pycache__" ".next" ".nuxt")
BLOAT_TRACKED=0
for bd in "${BLOAT_DIRS[@]}"; do
  TRACKED=$(git ls-files "$bd" 2>/dev/null | head -1)
  if [ -n "$TRACKED" ]; then
    gate_fail "Tracked bloat directory: $bd/"
    BLOAT_TRACKED=$((BLOAT_TRACKED + 1))
  fi
done

if [ "$BLOAT_TRACKED" -eq 0 ]; then
  gate_pass "No bloat directories tracked"
fi

# ── Check 4: Total repo size estimate ──
if ! $FAST; then
  echo "── Check 4: Repo Size ──"
  REPO_SIZE_MB=$(du -sm .git 2>/dev/null | cut -f1)
  REPO_SIZE_MB=${REPO_SIZE_MB:-0}
  if [ "$REPO_SIZE_MB" -gt 500 ]; then
    gate_warn "Git directory: ${REPO_SIZE_MB}MB (consider git gc)"
  else
    gate_pass "Git directory: ${REPO_SIZE_MB}MB"
  fi
fi

# ── Check 5: Unreasonably large single commit ──
echo "── Check 5: Commit Size ──"
STAGED_COUNT=$(git diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
STAGED_COUNT=${STAGED_COUNT:-0}
if [ "$STAGED_COUNT" -gt 200 ]; then
  gate_warn "Large commit: $STAGED_COUNT files staged (consider splitting)"
elif [ "$STAGED_COUNT" -gt 0 ]; then
  gate_pass "Staged file count: $STAGED_COUNT"
else
  gate_pass "No staged changes (dry-run mode)"
fi

# ── Summary ──
echo ""
echo "═══════════════════════════════"
if [ "$FAIL" -gt 0 ]; then
  printf "  Result: ❌ BLOAT DETECTED (%d failures, %d warnings)\n" "$FAIL" "$WARN"
  echo "═══════════════════════════════"
  exit 1
else
  printf "  Result: ✅ BLOAT GATE PASSED (%d warnings)\n" "$WARN"
  echo "═══════════════════════════════"
  exit 0
fi
