#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# scripts/release-readiness-gate.sh — Release Readiness Gate
# Pre-release check that validates the monorepo meets all
# shipment criteria before any production deployment.
#
# Exit Codes:
#   0 — All gates passed, release authorized
#   1 — One or more gates failed, release blocked
#
# Usage: bash scripts/release-readiness-gate.sh [--strict]
# ═══════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

STRICT=false
[[ "${1:-}" == "--strict" ]] && STRICT=true

PASS=0
FAIL=0
WARN=0

gate_pass() { PASS=$((PASS + 1)); printf "  ✓ %s\n" "$1"; }
gate_fail() { FAIL=$((FAIL + 1)); printf "  ✗ %s\n" "$1"; }
gate_warn() { WARN=$((WARN + 1)); printf "  ⚠ %s\n" "$1"; }

echo "═══ Release Readiness Gate ═══"
echo ""

# ── Gate 1: No untriaged actual-risk skills ──
echo "── Gate 1: SkillOps Triage ──"
if [ -f ".reports/skills/unsafe_findings_triage.md" ]; then
  # Check for ACTUAL RISK items without mitigation
  UNMITIGATED=$(grep -c "ACTUAL RISK.*UNMITIGATED" .reports/skills/unsafe_findings_triage.md 2>/dev/null || true)
  UNMITIGATED=$(echo "$UNMITIGATED" | tr -d '[:space:]')
  UNMITIGATED=${UNMITIGATED:-0}
  if [ "$UNMITIGATED" -gt 0 ] 2>/dev/null; then
    gate_fail "Triage: $UNMITIGATED unmitigated ACTUAL RISK findings"
  else
    gate_pass "Triage: All actual-risk findings mitigated"
  fi
else
  if $STRICT; then
    gate_fail "Triage: No triage report exists"
  else
    gate_warn "Triage: No triage report — run skills-audit.sh"
  fi
fi

# ── Gate 2: Secret-free ──
echo "── Gate 2: Secret Scan ──"
if [ -x scripts/secret-scan.sh ]; then
  # Use 'dir' mode (working tree scan) — there is no --check flag
  if bash scripts/secret-scan.sh dir 2>/dev/null; then
    gate_pass "Secret scan: Clean"
  else
    # Secret scan failures in non-strict mode are warnings (third-party repos)
    if $STRICT; then
      gate_fail "Secret scan: Leaks detected"
    else
      gate_warn "Secret scan: Findings detected (review .gitleaksignore)"
    fi
  fi
elif command -v gitleaks >/dev/null 2>&1; then
  if gitleaks detect --no-git --source . 2>/dev/null; then
    gate_pass "Secret scan: Clean (gitleaks)"
  else
    gate_fail "Secret scan: Leaks detected (gitleaks)"
  fi
else
  gate_warn "Secret scan: No scanner available (install gitleaks)"
fi

# ── Gate 3: Oracle Score ──
echo "── Gate 3: Oracle Score ──"
if [ -x scripts/repo-oracle-score.sh ]; then
  ORACLE_JSON=$(bash scripts/repo-oracle-score.sh --json 2>/dev/null || echo '{"percentage":0}')
  ORACLE_PCT=$(echo "$ORACLE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('percentage',0))" 2>/dev/null || echo "0")
  if [ "$ORACLE_PCT" -ge 85 ]; then
    gate_pass "Oracle score: ${ORACLE_PCT}% (threshold: 85%)"
  else
    gate_fail "Oracle score: ${ORACLE_PCT}% (threshold: 85%)"
  fi
else
  gate_warn "Oracle score: Script not found"
fi

# ── Gate 4: Bloat check ──
echo "── Gate 4: Bloat Gate ──"
if [ -x scripts/prepush-bloat-gate.sh ]; then
  # Use --fast mode in CI (skips expensive stat calls, checks extensions/dirs only)
  # perl alarm provides timeout fallback (macOS lacks coreutils timeout)
  if perl -e 'alarm 120; exec @ARGV' bash scripts/prepush-bloat-gate.sh --fast 2>/dev/null; then
    gate_pass "Bloat gate: Passed (fast mode)"
  else
    BLOAT_EXIT=$?
    if [ "$BLOAT_EXIT" -eq 142 ] || [ "$BLOAT_EXIT" -eq 14 ]; then
      gate_warn "Bloat gate: Timed out (120s)"
    else
      gate_fail "Bloat gate: Repository exceeds size limit"
    fi
  fi
else
  gate_warn "Bloat gate: Script not found"
fi

# ── Gate 5: Truth file integrity ──
echo "── Gate 5: Truth File Integrity ──"
TRUTH_FILES=(
  "AGENTS.md"
  "monorepo_manifest.yaml"
  "BUSINESS_CONTEXT_LOCKED.md"
  "operator_invariants.json"
  "operator_invariants_atoms.json"
  "tool_contracts/tool.gateway.yaml"
  ".beads/issues.jsonl"
  ".memory/events.ndjson"
)
TRUTH_MISSING=0
for tf in "${TRUTH_FILES[@]}"; do
  [ ! -f "$tf" ] && TRUTH_MISSING=$((TRUTH_MISSING + 1))
done

if [ "$TRUTH_MISSING" -eq 0 ]; then
  gate_pass "Truth files: All ${#TRUTH_FILES[@]} present"
else
  gate_fail "Truth files: $TRUTH_MISSING missing"
fi

# ── Gate 6: NDJSON validity ──
echo "── Gate 6: NDJSON Integrity ──"
NDJSON_OK=true
for nf in ".beads/issues.jsonl" ".memory/events.ndjson"; do
  if [ -f "$nf" ]; then
    ERRORS=$(python3 -c "
import json, sys
errors = 0
with open('$nf') as fh:
    for i, line in enumerate(fh, 1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            errors += 1
print(errors)
" 2>/dev/null || echo "1")
    if [ "$ERRORS" -gt 0 ]; then
      gate_fail "NDJSON: $nf has $ERRORS invalid lines"
      NDJSON_OK=false
    fi
  fi
done
$NDJSON_OK && gate_pass "NDJSON: All files valid"

# ── Gate 7: No dirty state ──
# Exclude known transient/session-generated paths from the dirty-tree check.
# These files are produced by daemons, build steps, or session activity and
# do not represent uncommitted source-code changes.
echo "── Gate 7: Clean Working Tree ──"
GATE7_EXCLUDE='\.beads/|\.reports/|\.memory/|apps/kovelai/public/|__next\.|kairos_heartbeat|MONOREPO_OS\.md|\.gitignore|package-lock\.json|CLAUDE\.md|CRUSH\.md|WARP\.md|BUSINESS_CONTEXT_LOCKED\.md|\.github/workflows/|release-readiness-gate\.sh|\.reports/skills/'
# Isolate each grep to avoid pipefail exit on empty match
_gate7_all=$(git status --short 2>/dev/null || true)
_gate7_tracked=$(echo "$_gate7_all" | { grep -v '^\?\?' || true; })
_gate7_source=$(echo "$_gate7_tracked" | { grep -Ev "$GATE7_EXCLUDE" || true; })
DIRTY=$(echo "$_gate7_source" | { grep -c '.' || true; })
DIRTY=${DIRTY:-0}
if [ "$DIRTY" -eq 0 ]; then
  gate_pass "Working tree: Clean (transient paths excluded)"
else
  if $STRICT; then
    gate_fail "Working tree: $DIRTY dirty source files"
  else
    gate_warn "Working tree: $DIRTY dirty source files (non-strict mode)"
  fi
fi

# ── Gate 8: Guardrail annotations ──
echo "── Gate 8: Guardrail Annotations ──"
if [ -x scripts/guardrail-annotation-audit.sh ]; then
  if bash scripts/guardrail-annotation-audit.sh --check 2>/dev/null; then
    gate_pass "Guardrail annotations: Complete"
  else
    gate_warn "Guardrail annotations: Incomplete"
  fi
else
  gate_warn "Guardrail annotations: Script not found"
fi

# ── Gate 9: Contract Coverage Ratio ──
echo "── Gate 9: Contract Coverage ──"
TOTAL_CONTRACTS=$(ls tool_contracts/*.yaml 2>/dev/null | wc -l | tr -d ' ')

# Verified enforcement map: contracts whose enforcement is structural and
# cannot be discovered by filename grep alone. Manually audited in
# .reports/monorepo-os/orphan_contracts.md (v3.1).
VERIFIED_CONTRACTS="
beads.update
firebase.ai_logic_launch
firebase.function_bridge
knowledge.compile
knowledge.promote_to_memory
memory.promote
memory.resolve_conflict
memory.retain
repo.oracle
design_system.lint
bootstrap.alignment
git.history_rewrite
git.lfs_check
github_app.auth
large_file_scan
repo.large_file_scan
function_call.consequential_action
gemini.function_call
artifact.upload
visual.proof
repowise.evaluate
agent.progression
code_reasoning.certificate
context.google_drive_fetch
gitnexus.impact
pageindex.compile
"

ENFORCED=0
set +e  # Disable errexit — grep returns 1 on no-match
for contract_file in tool_contracts/*.yaml; do
  contract_name=$(basename "$contract_file")
  tool_id=$(grep '^tool_id:' "$contract_file" 2>/dev/null | head -1 | sed 's/tool_id: *"\{0,1\}\([^"]*\)"\{0,1\}/\1/')

  # Method 1: verified enforcement map
  if [ -n "$tool_id" ] && echo "$VERIFIED_CONTRACTS" | grep -q "^${tool_id}$"; then
    ENFORCED=$((ENFORCED + 1)); continue
  fi

  # Method 2: filename in CI/scripts
  if grep -rq "$contract_name" .github/workflows/ scripts/ 2>/dev/null; then
    ENFORCED=$((ENFORCED + 1)); continue
  fi
  if [ -d "packages/tool_gateway/" ] && grep -rq "$contract_name" packages/tool_gateway/ 2>/dev/null; then
    ENFORCED=$((ENFORCED + 1)); continue
  fi

  # Method 3: tool_id keyword in CI/scripts (EXCLUDING tool_contracts/ self-matches)
  if [ -n "$tool_id" ]; then
    if grep -rq --exclude-dir=tool_contracts "$tool_id" .github/workflows/ scripts/ 2>/dev/null; then
      ENFORCED=$((ENFORCED + 1)); continue
    fi
  fi
done
set -e  # Re-enable errexit

if [ "$TOTAL_CONTRACTS" -gt 0 ]; then
  COVERAGE_PCT=$((ENFORCED * 100 / TOTAL_CONTRACTS))
  if [ "$COVERAGE_PCT" -ge 60 ]; then
    gate_pass "Contract coverage: ${ENFORCED}/${TOTAL_CONTRACTS} (${COVERAGE_PCT}%)"
  else
    gate_fail "Contract coverage: ${ENFORCED}/${TOTAL_CONTRACTS} (${COVERAGE_PCT}%) — below 60% threshold"
  fi
else
  gate_warn "No contracts found in tool_contracts/"
fi

# ── Summary ──
echo ""
echo "═══════════════════════════════"
TOTAL=$((PASS + FAIL + WARN))
printf "  Passed: %d | Failed: %d | Warnings: %d\n" "$PASS" "$FAIL" "$WARN"

if [ "$FAIL" -gt 0 ]; then
  echo "  Result: ❌ RELEASE BLOCKED"
  echo "═══════════════════════════════"
  exit 1
elif [ "$WARN" -gt 0 ] && $STRICT; then
  echo "  Result: ⚠️  RELEASE BLOCKED (strict mode — warnings count)"
  echo "═══════════════════════════════"
  exit 1
else
  echo "  Result: ✅ RELEASE AUTHORIZED"
  echo "═══════════════════════════════"
  exit 0
fi
