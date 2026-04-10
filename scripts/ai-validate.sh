#!/usr/bin/env bash
# ==============================================================================
# ai-validate.sh — Portable Pre-Action Validation Hook
# Per Invariant #14: Portable hooks replace vendor-locked CI/CD.
# Per Invariant #38: The Compiler Guillotine (Anti-False-Claims)
# ==============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Directories to skip during scans (performance)
EXCLUDE_DIRS="--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=archive --exclude-dir=.venv --exclude-dir=target --exclude-dir=.lancedb --exclude-dir=data --exclude-dir=.gitnexus --exclude-dir=.mypy_cache --exclude-dir=.ruff_cache --exclude-dir=__pycache__"

echo -e "${YELLOW}═══ AI-VALIDATE GUILLOTINE ═══${NC}"

# 1. Check for conflict markers (fast — only staged files if available, else quick grep)
echo -n "  [1/5] Conflict markers... "
STAGED=$(git diff --cached --name-only 2>/dev/null || true)
if [ -n "$STAGED" ]; then
  # Only check staged files
  FOUND=$(echo "$STAGED" | xargs grep -l '<<<<<<' 2>/dev/null | head -1 || true)
else
  # Quick scan of key directories only
  FOUND=$(grep -rl '<<<<<<' $EXCLUDE_DIRS --include='*.py' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.json' --include='*.yaml' --include='*.yml' apps/ core/ tools/ scripts/ infrastructure/ 2>/dev/null | grep -v 'resolve_conflicts\|scan_files' | head -1 || true)
fi
if [ -n "$FOUND" ]; then
  echo -e "${RED}FAIL${NC} — Conflict markers found in: $FOUND"
  ERRORS=$((ERRORS + 1))
else
  echo -e "${GREEN}PASS${NC}"
fi

# 2. Check for secrets in staged files
echo -n "  [2/5] Secrets in staged files... "
SECRET_FILES=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(env|pem|key)$' | head -1 || true)
if [ -n "$SECRET_FILES" ]; then
  echo -e "${RED}FAIL${NC} — Secret files staged: $SECRET_FILES"
  ERRORS=$((ERRORS + 1))
else
  echo -e "${GREEN}PASS${NC}"
fi

# 3. Validate truth surface YAML syntax
echo -n "  [3/5] Truth surface YAML... "
if [ -f "monorepo_manifest.yaml" ]; then
  if python3 -c "import yaml; yaml.safe_load(open('monorepo_manifest.yaml'))" 2>/dev/null; then
    echo -e "${GREEN}PASS${NC}"
  else
    echo -e "${RED}FAIL${NC} — monorepo_manifest.yaml has invalid YAML"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo -e "${YELLOW}SKIP${NC} — not at repo root"
fi

# 4. Validate truth surface JSON syntax
echo -n "  [4/5] Truth surface JSON... "
if [ -f "antigravity-mcp-config.json" ]; then
  if python3 -c "import json; json.load(open('antigravity-mcp-config.json'))" 2>/dev/null; then
    echo -e "${GREEN}PASS${NC}"
  else
    echo -e "${RED}FAIL${NC} — antigravity-mcp-config.json has invalid JSON"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo -e "${YELLOW}SKIP${NC} — not at repo root"
fi

# 5. Check CLAUDE.md is thin shim (< 200 bytes per Invariant #12)
echo -n "  [5/5] CLAUDE.md thin shim... "
if [ -f "CLAUDE.md" ]; then
  SIZE=$(wc -c < CLAUDE.md | tr -d ' ')
  if [ "$SIZE" -gt 200 ]; then
    echo -e "${RED}FAIL${NC} — CLAUDE.md is ${SIZE} bytes (max 200). Must be thin shim."
    ERRORS=$((ERRORS + 1))
  else
    echo -e "${GREEN}PASS${NC} (${SIZE} bytes)"
  fi
else
  echo -e "${YELLOW}SKIP${NC} — not at repo root"
fi

echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo -e "${RED}═══ GUILLOTINE: ${ERRORS} VIOLATION(S) — BLOCKED ═══${NC}"
  exit 1
else
  echo -e "${GREEN}═══ GUILLOTINE: ALL CLEAR ═══${NC}"
  exit 0
fi
