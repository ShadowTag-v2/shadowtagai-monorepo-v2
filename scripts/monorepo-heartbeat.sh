#!/usr/bin/env bash
# scripts/monorepo-heartbeat.sh — Monorepo OS Health Verification
# Checks all 10 subsystems for structural integrity.
# Exit 0 = all healthy. Non-zero = failures found.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
WARN=0

check() {
  local name="$1" result="$2"
  if [ "$result" -eq 0 ]; then
    echo "  ✅ $name"
    PASS=$((PASS + 1))
  else
    echo "  ❌ $name"
    FAIL=$((FAIL + 1))
  fi
}

warn() {
  local name="$1"
  echo "  ⚠️  $name"
  WARN=$((WARN + 1))
}

echo "▸ Monorepo OS Heartbeat — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# ── 1. Task Truth (Beads) ──
echo "  [1/9] Task Truth — .beads/"
[ -f "$REPO_ROOT/.beads/issues.jsonl" ] && \
  python3 -c "
import json, sys
with open('$REPO_ROOT/.beads/issues.jsonl') as f:
  for i, line in enumerate(f, 1):
    line = line.strip()
    if not line: continue
    json.loads(line)
print(f'  Valid NDJSON: {i} entries')
" 2>/dev/null
check "issues.jsonl exists and is valid NDJSON" $?

# ── 2. Memory Truth ──
echo "  [2/9] Memory Truth — .memory/"
[ -d "$REPO_ROOT/.memory/atoms" ]
check ".memory/atoms/ directory exists" $?

ATOM_COUNT=$(find "$REPO_ROOT/.memory/atoms" -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
echo "        Atoms: $ATOM_COUNT"

# ── 3. ToolGateway ──
echo "  [3/9] Safety Truth — tool_contracts/"
CONTRACT_COUNT=$(find "$REPO_ROOT/tool_contracts" -name '*.yaml' -type f 2>/dev/null | wc -l | tr -d ' ')
[ "$CONTRACT_COUNT" -ge 5 ]
check "tool_contracts/ has $CONTRACT_COUNT contracts (≥5 required)" $?

# ── 4. Ruler ──
echo "  [4/9] Agent Doctrine — .ruler/"
[ -f "$REPO_ROOT/.ruler/ruler.toml" ] || [ -f "$REPO_ROOT/ruler.toml" ]
check "ruler.toml exists" $?

RULER_COUNT=$(find "$REPO_ROOT/.ruler" -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
echo "        Ruler rules: $RULER_COUNT"

# ── 5. Index Fabric ──
echo "  [5/9] Index Fabric"
[ -f "$REPO_ROOT/index_policy.yaml" ]
check "index_policy.yaml exists" $?

# ── 6. Upload Policy ──
echo "  [6/9] Upload Policy"
[ -f "$REPO_ROOT/upload_policy.yaml" ]
check "upload_policy.yaml exists" $?

# ── 7. Evidence Truth ──
echo "  [7/9] Evidence Truth — .agent/evidence/"
[ -f "$REPO_ROOT/.agent/evidence/index.ndjson" ]
check ".agent/evidence/index.ndjson exists" $?

# ── 8. Build Truth ──
echo "  [8/9] Build Truth — Bazel"
if command -v bazel &>/dev/null || command -v bazelisk &>/dev/null; then
  [ -f "$REPO_ROOT/MODULE.bazel" ]
  check "MODULE.bazel exists" $?
else
  warn "Bazel not installed — skipping build truth check"
fi

# ── 9. Push Truth ──
echo "  [9/9] Push Truth — GitHub App + Gates"
[ -f "$REPO_ROOT/scripts/push-with-app-gates.sh" ] || [ -f "$REPO_ROOT/scripts/auth_github_app.py" ]
check "Push gate script exists" $?

if command -v betterleaks &>/dev/null; then
  check "Betterleaks available" 0
elif command -v gitleaks &>/dev/null; then
  warn "Using gitleaks fallback (betterleaks preferred)"
else
  warn "No secret scanner available"
fi

# ── Git State ──
echo ""
echo "  [Git] Working tree status"
DIRTY=$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [ "$DIRTY" -eq 0 ]; then
  check "Working tree clean" 0
else
  warn "Working tree has $DIRTY dirty entries"
fi

LOCAL_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null)
REMOTE_SHA=$(git -C "$REPO_ROOT" rev-parse origin/main 2>/dev/null || echo "unknown")
if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
  check "HEAD = origin/main ($LOCAL_SHA)" 0
else
  warn "HEAD ($LOCAL_SHA) ≠ origin/main ($REMOTE_SHA)"
fi

# ── 10. SkillOps Health ──
echo ""
echo "  [10/10] SkillOps — skills-audit.sh"
if [ -x "$REPO_ROOT/scripts/skills-audit.sh" ] || [ -f "$REPO_ROOT/scripts/skills-audit.sh" ]; then
  AUDIT_JSON=$(bash "$REPO_ROOT/scripts/skills-audit.sh" --json 2>/dev/null || echo '{"unsafe_findings":0}')
  UNSAFE_COUNT=$(echo "$AUDIT_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('unsafe_findings', 0))" 2>/dev/null || echo "0")
  TOTAL_ACTIVE=$(echo "$AUDIT_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total_active', 0))" 2>/dev/null || echo "0")
  echo "        Active skills: $TOTAL_ACTIVE"
  echo "        Unsafe findings: $UNSAFE_COUNT"
  if [ "$UNSAFE_COUNT" -le 50 ]; then
    check "SkillOps unsafe findings within threshold (≤50)" 0
  else
    check "SkillOps unsafe findings within threshold (≤50)" 1
  fi
else
  warn "scripts/skills-audit.sh not found"
fi

# ── Summary ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PASS: $PASS  |  FAIL: $FAIL  |  WARN: $WARN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$FAIL" -gt 0 ]; then
  echo "  ❌ UNHEALTHY — $FAIL subsystem(s) failed"
  exit 1
else
  echo "  ✅ HEALTHY — All subsystems operational"
  exit 0
fi
