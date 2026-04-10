#!/usr/bin/env bash
# CodePMCS Scan — Quality + Security gate for shadowtag-omega-v4
set -euo pipefail

MONO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$MONO_ROOT/artifacts/codepmcs-reports"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/scan-$(date +%Y%m%d-%H%M%S).txt"

echo "=== CodePMCS Scan ===" | tee "$REPORT"
echo "Root: $MONO_ROOT" | tee -a "$REPORT"
echo "Date: $(date)" | tee -a "$REPORT"
echo "" | tee -a "$REPORT"

# 1. Ruff lint
echo "--- ruff lint ---" | tee -a "$REPORT"
if command -v ruff &>/dev/null; then
  ruff check "$MONO_ROOT" --select=E9,F,I \
    --exclude="$MONO_ROOT/docs/bundles,$MONO_ROOT/apps/ShadowTag-v2_stack/cosmic-crab-payload" \
    --output-format=full 2>&1 | tee -a "$REPORT" || true
else
  echo "ruff not found — skipping" | tee -a "$REPORT"
fi

# 2. Detect hardcoded secrets (simple pattern scan)
echo "" | tee -a "$REPORT"
echo "--- secret scan ---" | tee -a "$REPORT"
if grep -rn --include="*.py" --include="*.ts" --include="*.js" \
    -E "(sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36}|AIzaSy[a-zA-Z0-9_-]{33})" \
    "$MONO_ROOT/apps" "$MONO_ROOT/scripts" "$MONO_ROOT/src" 2>/dev/null \
    | grep -v ".pyc" | tee -a "$REPORT"; then
  echo "WARNING: potential secrets found above" | tee -a "$REPORT"
else
  echo "No obvious secrets found" | tee -a "$REPORT"
fi

# 3. Dead symlinks
echo "" | tee -a "$REPORT"
echo "--- dead symlinks ---" | tee -a "$REPORT"
find "$MONO_ROOT" -xtype l 2>/dev/null | grep -v node_modules | grep -v .git | tee -a "$REPORT" || true

echo "" | tee -a "$REPORT"
echo "=== SCAN COMPLETE ===" | tee -a "$REPORT"
echo "Report: $REPORT"
