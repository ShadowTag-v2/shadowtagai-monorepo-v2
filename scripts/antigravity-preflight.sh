#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# scripts/antigravity-preflight.sh — Monorepo OS Pre-Flight Check
# Hydrates truth surfaces before any nontrivial task.
# ═══════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
ERRORS=0

echo "═══════════════════════════════════════════════════════════"
echo "  ANTIGRAVITY MONOREPO OS — PRE-FLIGHT CHECK"
echo "  $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "═══════════════════════════════════════════════════════════"

# 1. Truth surfaces exist
echo ""
echo "▸ Checking truth surfaces..."
for f in truth_surfaces.yaml monorepo_manifest.yaml AGENTS.md operator_invariants.json; do
  if [ -f "$REPO_ROOT/$f" ]; then
    printf "  ${GREEN}✓${NC} %s\n" "$f"
  else
    printf "  ${RED}✗${NC} %s MISSING\n" "$f"
    ERRORS=$((ERRORS + 1))
  fi
done

# 2. Beads ledger
echo ""
echo "▸ Checking work truth..."
if [ -f "$REPO_ROOT/.beads/issues.jsonl" ]; then
  BEAD_COUNT=$(wc -l < "$REPO_ROOT/.beads/issues.jsonl" | tr -d ' ')
  printf "  ${GREEN}✓${NC} .beads/issues.jsonl (%s entries)\n" "$BEAD_COUNT"
else
  printf "  ${RED}✗${NC} .beads/issues.jsonl MISSING\n"
  ERRORS=$((ERRORS + 1))
fi

# 3. Memory infrastructure
echo ""
echo "▸ Checking operational memory..."
for d in atoms/decisions atoms/constraints atoms/procedures atoms/facts views; do
  if [ -d "$REPO_ROOT/.memory/$d" ]; then
    printf "  ${GREEN}✓${NC} .memory/%s/\n" "$d"
  else
    printf "  ${YELLOW}△${NC} .memory/%s/ (not created yet)\n" "$d"
  fi
done

# 4. Knowledge vault
echo ""
echo "▸ Checking research knowledge..."
if [ -d "$REPO_ROOT/knowledge/vault" ]; then
  VAULT_COUNT=$(find "$REPO_ROOT/knowledge/vault" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  printf "  ${GREEN}✓${NC} knowledge/vault/ (%s documents)\n" "$VAULT_COUNT"
else
  printf "  ${YELLOW}△${NC} knowledge/vault/ (not populated yet)\n"
fi

# 5. Evidence ledger
echo ""
echo "▸ Checking evidence ledger..."
if [ -f "$REPO_ROOT/.agent/evidence/index.ndjson" ]; then
  printf "  ${GREEN}✓${NC} .agent/evidence/index.ndjson\n"
else
  printf "  ${YELLOW}△${NC} .agent/evidence/index.ndjson (not initialized)\n"
fi

# 6. Tool contracts
echo ""
echo "▸ Checking tool contracts..."
if [ -d "$REPO_ROOT/tool_contracts" ]; then
  CONTRACT_COUNT=$(find "$REPO_ROOT/tool_contracts" -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')
  printf "  ${GREEN}✓${NC} tool_contracts/ (%s contracts)\n" "$CONTRACT_COUNT"
else
  printf "  ${RED}✗${NC} tool_contracts/ MISSING\n"
  ERRORS=$((ERRORS + 1))
fi

# 7. Git status
echo ""
echo "▸ Checking git state..."
BRANCH=$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || echo "detached")
HEAD=$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")
DIRTY=$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
printf "  Branch: %s | HEAD: %s | Dirty files: %s\n" "$BRANCH" "$HEAD" "$DIRTY"

# 8. Upload policy
echo ""
echo "▸ Checking upload policy..."
if [ -f "$REPO_ROOT/upload_policy.yaml" ]; then
  printf "  ${GREEN}✓${NC} upload_policy.yaml\n"
else
  printf "  ${YELLOW}△${NC} upload_policy.yaml (not configured)\n"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════"
if [ "$ERRORS" -gt 0 ]; then
  printf "  ${RED}PRE-FLIGHT FAILED${NC} — %d critical errors\n" "$ERRORS"
  exit 1
else
  printf "  ${GREEN}PRE-FLIGHT PASSED${NC} — Monorepo OS ready\n"
fi
echo "═══════════════════════════════════════════════════════════"
