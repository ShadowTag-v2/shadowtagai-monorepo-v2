#!/usr/bin/env bash
# RULE 00 Compliance Test Script
# Verifies Immutable Infrastructure invariants are not violated
# Run: bash scripts/rule00_compliance_test.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass() { echo -e "${GREEN}✅ PASS${NC}: $1"; PASS=$((PASS+1)); }
fail() { echo -e "${RED}❌ FAIL${NC}: $1"; FAIL=$((FAIL+1)); }
warn() { echo -e "${YELLOW}⚠️  WARN${NC}: $1"; WARN=$((WARN+1)); }

echo "============================================"
echo "  RULE 00: Immutable Infrastructure Audit"
echo "============================================"
echo ""

# Test 1: RULE 00 file exists
if [ -f .agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md ]; then
  pass "RULE_00_IMMUTABLE_INFRASTRUCTURE.md exists"
else
  fail "RULE_00_IMMUTABLE_INFRASTRUCTURE.md missing"
fi

# Test 2: RULE 00 referenced in AGENTS.md
if grep -q "RULE 00" .ruler/AGENTS.md 2>/dev/null; then
  pass "RULE 00 referenced in AGENTS.md"
else
  fail "RULE 00 not referenced in AGENTS.md"
fi

# Test 3: RULE 00 referenced in GEMINI.md
if grep -q "RULE 00" GEMINI.md 2>/dev/null; then
  pass "RULE 00 referenced in GEMINI.md"
else
  fail "RULE 00 not referenced in GEMINI.md"
fi

# Test 4: operator-invariants exists (workspace)
if [ -f .agents/skills/operator-invariants/SKILL.md ]; then
  pass "operator-invariants exists (workspace)"
else
  fail "operator-invariants MISSING (workspace)"
fi

# Test 5: operator-invariants exists (global)
if [ -f ~/.gemini/antigravity/skills/operator-invariants/SKILL.md ]; then
  pass "operator-invariants exists (global)"
else
  fail "operator-invariants MISSING (global)"
fi

# Test 6: Archive directory has no empty skill folders
EMPTY_COUNT=0
if [ -d ~/.gemini/antigravity/skills/_archive_redundant_2026-04-25/ ]; then
  for dir in ~/.gemini/antigravity/skills/_archive_redundant_2026-04-25/*/; do
    if [ ! -f "$dir/SKILL.md" ]; then
      fail "Archived skill $(basename "$dir") has no SKILL.md"
      EMPTY_COUNT=$((EMPTY_COUNT+1))
    fi
  done
  if [ "$EMPTY_COUNT" -eq 0 ]; then
    pass "All 20 archived skills have intact SKILL.md files"
  fi
else
  warn "Archive directory does not exist"
fi

# Test 7: No rm commands in recent git staged changes
STAGED_RM=$(git diff --cached --unified=0 2>/dev/null | grep -c '^\+.*\brm\b' || true)
if [ "$STAGED_RM" -gt 0 ]; then
  fail "Staged changes contain $STAGED_RM lines with 'rm' commands"
else
  pass "No 'rm' commands in staged changes"
fi

# Test 8: No destructive > redirects on existing skill files in staged changes
STAGED_CLOBBER=$(git diff --cached --unified=0 2>/dev/null | grep -cE '^\+.*cat.*<<.*EOF.*>' || true)
if [ "$STAGED_CLOBBER" -gt 0 ]; then
  warn "Staged changes contain $STAGED_CLOBBER potential clobber patterns (cat > on existing files)"
else
  pass "No clobber patterns in staged changes"
fi

# Test 9: SKILL_PAYLOADS.md exists and has Payloads G+H
if [ -f ~/Antigravity-Vault/SKILL_PAYLOADS.md ]; then
  if grep -q "Payload G" ~/Antigravity-Vault/SKILL_PAYLOADS.md && grep -q "Payload H" ~/Antigravity-Vault/SKILL_PAYLOADS.md; then
    pass "SKILL_PAYLOADS.md contains Payloads G + H"
  else
    warn "SKILL_PAYLOADS.md missing Payload G or H"
  fi
else
  warn "SKILL_PAYLOADS.md not found at ~/Antigravity-Vault/"
fi

# Test 10: Pre-commit hook exists and blocks rm
if [ -f .git/hooks/pre-commit ]; then
  if grep -q "RULE.00\|rm.*--force\|unlink" .git/hooks/pre-commit 2>/dev/null; then
    pass "Pre-commit hook enforces RULE 00"
  else
    warn "Pre-commit hook exists but may not enforce RULE 00"
  fi
else
  warn "No pre-commit hook installed"
fi

echo ""
echo "============================================"
echo "  Results: ${PASS} passed, ${FAIL} failed, ${WARN} warnings"
echo "============================================"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
