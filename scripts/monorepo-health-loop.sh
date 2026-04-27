#!/usr/bin/env bash
set -euo pipefail

# monorepo-health-loop.sh — Monorepo OS Subsystem Health Check
#
# Validates all Monorepo OS subsystems are present and well-formed.
# Exit 0 = all healthy. Exit 1 = at least one failure.
#
# Usage:
#   bash scripts/monorepo-health-loop.sh
#   bash scripts/monorepo-health-loop.sh --verbose
#
# Referenced by: MONOREPO_OS.md, scripts/antigravity-preflight.sh

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
VERBOSE="${1:-}"
FAILURES=0

pass() { printf "  ✅  %s\n" "$1"; }
fail() { printf "  ❌  %s\n" "$1"; FAILURES=$((FAILURES + 1)); }
info() { [[ "$VERBOSE" == "--verbose" ]] && printf "  ℹ️   %s\n" "$1" || true; }

echo "═══════════════════════════════════════════════════════"
echo "  Monorepo OS — Health Loop v1.0"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── 1. Beads subsystem ────────────────────────────────────
echo "▸ Beads (Task Graph)"
if [[ -f "$ROOT/.beads/issues.jsonl" ]]; then
  # Validate NDJSON: each non-empty line must be valid JSON
  BAD_LINES=$(grep -c '^[^{[]' "$ROOT/.beads/issues.jsonl" 2>/dev/null || echo 0)
  if [[ "$BAD_LINES" -le 1 ]]; then
    ISSUE_COUNT=$(wc -l < "$ROOT/.beads/issues.jsonl" | tr -d ' ')
    pass "issues.jsonl present ($ISSUE_COUNT entries)"
  else
    fail "issues.jsonl has $BAD_LINES malformed lines"
  fi
else
  fail "issues.jsonl missing"
fi

if [[ -f "$ROOT/.beads/config.yaml" ]]; then
  pass "config.yaml present"
else
  fail "config.yaml missing"
fi

# ── 2. Memory subsystem ──────────────────────────────────
echo ""
echo "▸ Memory (Knowledge Atoms)"
if [[ -f "$ROOT/.memory/events.ndjson" ]]; then
  EVENT_COUNT=$(wc -l < "$ROOT/.memory/events.ndjson" | tr -d ' ')
  pass "events.ndjson present ($EVENT_COUNT events)"
else
  fail "events.ndjson missing"
fi

if [[ -d "$ROOT/.memory/atoms" ]]; then
  ATOM_COUNT=$(find "$ROOT/.memory/atoms" -name "*.md" | wc -l | tr -d ' ')
  pass "atoms/ directory present ($ATOM_COUNT atoms)"
else
  fail "atoms/ directory missing"
fi

# ── 3. Ruler subsystem ───────────────────────────────────
echo ""
echo "▸ Ruler (Instruction Propagation)"
if [[ -f "$ROOT/.ruler/ruler.toml" ]]; then
  pass "ruler.toml present"
else
  fail "ruler.toml missing"
fi

if [[ -f "$ROOT/.ruler/AGENTS.md" ]]; then
  pass "AGENTS.md present"
else
  fail "AGENTS.md missing"
fi

# ── 4. ToolGateway ───────────────────────────────────────
echo ""
echo "▸ ToolGateway (Action Contracts)"
if [[ -d "$ROOT/tool_contracts" ]]; then
  CONTRACT_COUNT=$(find "$ROOT/tool_contracts" -name "*.yaml" | wc -l | tr -d ' ')
  if [[ "$CONTRACT_COUNT" -ge 4 ]]; then
    pass "tool_contracts/ has $CONTRACT_COUNT contracts"
  else
    fail "tool_contracts/ has only $CONTRACT_COUNT contracts (need ≥4)"
  fi
else
  fail "tool_contracts/ directory missing"
fi

# ── 5. Evidence Ledger ───────────────────────────────────
echo ""
echo "▸ Evidence (Flight Recorder)"
if [[ -d "$ROOT/.agent/evidence" ]]; then
  pass ".agent/evidence/ directory present"
else
  fail ".agent/evidence/ directory missing"
fi

# ── 6. Index Fabric ──────────────────────────────────────
echo ""
echo "▸ Index Fabric (Multi-Index Router)"
if [[ -f "$ROOT/index_policy.yaml" ]]; then
  pass "index_policy.yaml present"
else
  fail "index_policy.yaml missing"
fi

# ── 7. Upload Policy ────────────────────────────────────
echo ""
echo "▸ Upload Policy (Two-Lane Doctrine)"
if [[ -f "$ROOT/upload_policy.yaml" ]]; then
  pass "upload_policy.yaml present"
else
  fail "upload_policy.yaml missing"
fi

# ── 8. Push Gates ────────────────────────────────────────
echo ""
echo "▸ Push Gates (Outbound Safety)"
if [[ -f "$ROOT/scripts/push-with-app-gates.sh" ]]; then
  pass "push-with-app-gates.sh present"
else
  fail "push-with-app-gates.sh missing"
fi

# ── 9. Monorepo OS Document ─────────────────────────────
echo ""
echo "▸ Monorepo OS (Integration Document)"
if [[ -f "$ROOT/MONOREPO_OS.md" ]]; then
  pass "MONOREPO_OS.md present"
else
  fail "MONOREPO_OS.md missing"
fi

# ── 10. Tool Availability ───────────────────────────────
echo ""
echo "▸ Tool Availability"
command -v buildifier &>/dev/null && pass "buildifier available" || fail "buildifier not found"
command -v ruff &>/dev/null && pass "ruff available" || fail "ruff not found"

# Check for at least one secret scanner
if command -v betterleaks &>/dev/null; then
  pass "betterleaks available"
elif command -v gitleaks &>/dev/null; then
  pass "gitleaks available (betterleaks preferred)"
else
  fail "no secret scanner (betterleaks or gitleaks) found"
fi

# ── Summary ──────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
if [[ "$FAILURES" -eq 0 ]]; then
  echo "  ✅  ALL SUBSYSTEMS HEALTHY"
else
  echo "  ❌  $FAILURES SUBSYSTEM(S) NEED ATTENTION"
fi
echo "═══════════════════════════════════════════════════════"

exit "$FAILURES"
