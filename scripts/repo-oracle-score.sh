#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# scripts/repo-oracle-score.sh — Repo Oracle Truth Scoring
# Computes a confidence score for the monorepo's governance
# health by verifying the existence and integrity of all
# canonical truth surfaces.
#
# Usage: bash scripts/repo-oracle-score.sh [--json]
# ═══════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

JSON_MODE=false
[[ "${1:-}" == "--json" ]] && JSON_MODE=true

SCORE=0
MAX_SCORE=0
RESULTS=()

check() {
  local label="$1"
  local weight="$2"
  local condition="$3"

  MAX_SCORE=$((MAX_SCORE + weight))
  if eval "$condition" >/dev/null 2>&1; then
    SCORE=$((SCORE + weight))
    RESULTS+=("{\"check\":\"$label\",\"weight\":$weight,\"pass\":true}")
    $JSON_MODE || printf "  ✓ [%2d] %s\n" "$weight" "$label"
  else
    RESULTS+=("{\"check\":\"$label\",\"weight\":$weight,\"pass\":false}")
    $JSON_MODE || printf "  ✗ [%2d] %s\n" "$weight" "$label"
  fi
}

$JSON_MODE || echo "═══ Repo Oracle Truth Score ═══"
$JSON_MODE || echo ""

# ── Core Truth Files (30 pts) ──
check "AGENTS.md exists"              5 "[ -f AGENTS.md ]"
check "GEMINI.md exists"              3 "[ -f GEMINI.md ]"
check "monorepo_manifest.yaml"        5 "[ -f monorepo_manifest.yaml ]"
check "BUSINESS_CONTEXT_LOCKED.md"    3 "[ -f BUSINESS_CONTEXT_LOCKED.md ]"
check "RISK_REGISTER.md"              3 "[ -f RISK_REGISTER.md ]"
check "MONOREPO_OS.md"                3 "[ -f docs/MONOREPO_OS.md ]"
check "antigravity-mcp-config.json"   3 "[ -f antigravity-mcp-config.json ]"
check "operator_invariants.json"      5 "[ -f operator_invariants.json ]"

# ── Governance Surfaces (25 pts) ──
check "operator_invariants_atoms.json"     5 "[ -f operator_invariants_atoms.json ]"
check "upload_policy.yaml"                 3 "[ -f upload_policy.yaml ]"
check "index_policy.yaml"                  3 "[ -f index_policy.yaml ]"
check "tool_contracts/ dir exists"         5 "[ -d tool_contracts ]"
check "tool_contracts/tool.gateway.yaml"   5 "[ -f tool_contracts/tool.gateway.yaml ]"
check "tool_contracts >= 5 files"          4 "[ \$(find tool_contracts -name '*.yaml' | wc -l) -ge 5 ]"

# ── Memory Architecture (15 pts) ──
check ".beads/issues.jsonl"                5 "[ -f .beads/issues.jsonl ]"
check ".memory/events.ndjson"              5 "[ -f .memory/events.ndjson ]"
check ".memory/atoms/ dir"                 5 "[ -d .memory/atoms ]"

# ── CI/CD (15 pts) ──
check "monorepo-os-gates.yml"              5 "[ -f .github/workflows/monorepo-os-gates.yml ]"
check "skillops-audit.yml"                 3 "[ -f .github/workflows/skillops-audit.yml ]"
check "omni-ci.yml"                        4 "[ -f .github/workflows/omni-ci.yml ]"
check "pre-commit-config.yaml"             3 "[ -f .pre-commit-config.yaml ]"

# ── External References (10 pts) ──
check "upstream_manifest.yaml"             5 "[ -f external_repos/upstream_manifest.yaml ]"
check "external_repos/README.md"           3 "[ -f external_repos/README.md ]"
check "clone-external-reference-repos.sh"  2 "[ -x scripts/clone-external-reference-repos.sh ]"

# ── Security (5 pts) ──
check "secret-scan.sh executable"          3 "[ -x scripts/secret-scan.sh ]"
check ".gitleaksignore"                    2 "[ -f .gitleaksignore ]"

# ── Output ──
$JSON_MODE || echo ""

PERCENTAGE=$((SCORE * 100 / MAX_SCORE))

if $JSON_MODE; then
  RESULTS_JSON=$(IFS=,; echo "[${RESULTS[*]}]")
  cat <<EOF
{
  "score": $SCORE,
  "max_score": $MAX_SCORE,
  "percentage": $PERCENTAGE,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": $RESULTS_JSON
}
EOF
else
  echo "═══════════════════════════════"
  printf "  Score: %d/%d (%d%%)\n" "$SCORE" "$MAX_SCORE" "$PERCENTAGE"

  if [ "$PERCENTAGE" -ge 95 ]; then
    echo "  Grade: A+ — Self-Verifying OS"
  elif [ "$PERCENTAGE" -ge 85 ]; then
    echo "  Grade: A  — Governed"
  elif [ "$PERCENTAGE" -ge 70 ]; then
    echo "  Grade: B  — Structured"
  elif [ "$PERCENTAGE" -ge 50 ]; then
    echo "  Grade: C  — Partial"
  else
    echo "  Grade: F  — Ungoverned"
  fi
  echo "═══════════════════════════════"
fi
