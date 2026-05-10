#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

echo "[pre-push] running startup relock"
bash scripts/startup_relock.sh >/tmp/startup_relock.out 2>/tmp/startup_relock.err || {
  echo "[pre-push] FAIL: startup_relock.sh failed"
  cat /tmp/startup_relock.out 2>/dev/null || true
  cat /tmp/startup_relock.err 2>/dev/null || true
  exit 1
}

echo "[pre-push] running adapter-only hardening audit"
bash scripts/adapter_only_hardening_audit.sh >/tmp/adapter_audit.out 2>/tmp/adapter_audit.err || {
  echo "[pre-push] FAIL: adapter_only_hardening_audit.sh failed"
  cat /tmp/adapter_audit.out 2>/dev/null || true
  cat /tmp/adapter_audit.err 2>/dev/null || true
  exit 1
}

REPORT="$ROOT/docs/ADAPTER_ONLY_HARDENING_REPORT.md"
if [[ ! -f "$REPORT" ]]; then
  echo "[pre-push] FAIL: missing audit report: $REPORT"
  exit 1
fi

echo "[pre-push] checking final verdict"
if rg -n '\*\*COMPLETE_WITH_BLOCKERS\*\*|\- \*\*COMPLETE_WITH_BLOCKERS\*\*' "$REPORT" >/dev/null 2>&1; then
  echo "[pre-push] FAIL: audit verdict is COMPLETE_WITH_BLOCKERS"
  echo "[pre-push] blockers:"
  awk '
    BEGIN {in_blockers=0}
    /^## Blockers/ {in_blockers=1; next}
    /^## / && in_blockers==1 {exit}
    in_blockers==1 {print}
  ' "$REPORT" || true
  exit 1
fi

if ! rg -n '\*\*COMPLETE\*\*|\- \*\*COMPLETE\*\*' "$REPORT" >/dev/null 2>&1; then
  echo "[pre-push] FAIL: audit report missing explicit COMPLETE verdict"
  exit 1
fi

echo "[pre-push] PASS"
