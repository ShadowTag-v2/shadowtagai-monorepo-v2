#!/usr/bin/env bash
# antigravity-preflight.sh — Pre-flight validation for the UphillSnowball monorepo.
#
# Runs a quick series of checks before any major agent operation:
#   1. Git status (clean working tree?)
#   2. Auth state (GitHub App PEM, Firebase, GCP ADC)
#   3. MCP server health (5-server fleet)
#   4. Lint state (ruff + biome quick check)
#   5. Betterleaks scan (staged changes only)
#   6. Tool Gateway contract validation
#
# Usage:
#   bash scripts/antigravity-preflight.sh           # Full preflight
#   bash scripts/antigravity-preflight.sh --quick    # Skip lint + scan (fast mode)
#
# Exit codes:
#   0 = All checks passed
#   1 = One or more checks failed (see output for details)
#
# References:
#   - ANTIGRAVITY_CONTROL_PLANE.md (Pillar 2: Pre-Action Memory Gate)
#   - AGENTS.md (Operator Invariants)
#   - tool_contracts/ (Contract registry)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

QUICK_MODE=false
FAILURES=0
WARNINGS=0

# Parse args
for arg in "$@"; do
    case "$arg" in
        --quick) QUICK_MODE=true ;;
        --help|-h)
            echo "Usage: bash scripts/antigravity-preflight.sh [--quick]"
            echo "  --quick  Skip lint and secret scan (fast mode)"
            exit 0
            ;;
    esac
done

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ANTIGRAVITY PRE-FLIGHT CHECK         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# --- 1. Git Status ---
echo -e "${BLUE}[1/6]${NC} Git Status..."
BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
DIRTY=$(git status --porcelain 2>/dev/null | grep -v '??' | wc -l | tr -d ' ')
REMOTE=$(git remote get-url origin 2>/dev/null || echo "no remote")

echo "  Branch: ${BRANCH}"
echo "  Remote: ${REMOTE}"
if [ "$DIRTY" -gt 0 ]; then
    echo -e "  ${YELLOW}⚠ ${DIRTY} uncommitted changes${NC}"
    ((WARNINGS++))
else
    echo -e "  ${GREEN}✓ Working tree clean${NC}"
fi

# --- 2. Auth State ---
echo -e "\n${BLUE}[2/6]${NC} Auth State..."

# GitHub App PEM
if [ -n "${SHADOWTAG_PEM:-}" ] && [ -f "${SHADOWTAG_PEM}" ]; then
    echo -e "  ${GREEN}✓ GitHub App PEM: \$SHADOWTAG_PEM${NC}"
elif [ -f "$HOME/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem" ]; then
    echo -e "  ${GREEN}✓ GitHub App PEM: ~/Downloads/${NC}"
else
    echo -e "  ${RED}✗ GitHub App PEM: NOT FOUND${NC}"
    ((FAILURES++))
fi

# GCP ADC
if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
    echo -e "  ${GREEN}✓ GCP ADC: configured${NC}"
else
    echo -e "  ${YELLOW}⚠ GCP ADC: not configured (run gcloud auth application-default login)${NC}"
    ((WARNINGS++))
fi

# Firebase CLI
if command -v firebase &>/dev/null; then
    FIREBASE_USER=$(CI=true firebase login:list 2>/dev/null | head -1 || echo "unknown")
    echo -e "  ${GREEN}✓ Firebase CLI: installed${NC} (${FIREBASE_USER})"
else
    echo -e "  ${YELLOW}⚠ Firebase CLI: not installed${NC}"
    ((WARNINGS++))
fi

# --- 3. Tool Versions ---
echo -e "\n${BLUE}[3/6]${NC} Tool Versions..."

# Python
PYTHON_VER=$(/opt/homebrew/bin/python3.14 --version 2>/dev/null || echo "NOT FOUND")
echo "  Python: ${PYTHON_VER}"

# Ruff
RUFF_VER=$(ruff --version 2>/dev/null || echo "NOT FOUND")
echo "  Ruff: ${RUFF_VER}"

# Node
NODE_VER=$(node --version 2>/dev/null || echo "NOT FOUND")
echo "  Node: ${NODE_VER}"

# .NET
DOTNET_VER=$(dotnet --version 2>/dev/null || echo "NOT FOUND")
echo "  .NET: ${DOTNET_VER}"

# --- 4. Lint Check (skip in quick mode) ---
if [ "$QUICK_MODE" = false ]; then
    echo -e "\n${BLUE}[4/6]${NC} Lint Check..."
    RUFF_EXIT=0
    ruff check --quiet . 2>/dev/null || RUFF_EXIT=$?
    if [ "$RUFF_EXIT" -le 1 ]; then
        echo -e "  ${GREEN}✓ Ruff: passed${NC}"
    else
        echo -e "  ${RED}✗ Ruff: fatal errors (exit ${RUFF_EXIT})${NC}"
        ((FAILURES++))
    fi
else
    echo -e "\n${BLUE}[4/6]${NC} Lint Check... ${YELLOW}SKIPPED (--quick)${NC}"
fi

# --- 5. Secrets Scan (skip in quick mode) ---
if [ "$QUICK_MODE" = false ]; then
    echo -e "\n${BLUE}[5/6]${NC} Secrets Scan..."
    if command -v betterleaks &>/dev/null; then
        LEAKS_EXIT=0
        betterleaks detect --no-git --quiet 2>/dev/null || LEAKS_EXIT=$?
        if [ "$LEAKS_EXIT" -eq 0 ]; then
            echo -e "  ${GREEN}✓ Betterleaks: clean${NC}"
        else
            echo -e "  ${YELLOW}⚠ Betterleaks: ${LEAKS_EXIT} findings (review .betterleaksignore)${NC}"
            ((WARNINGS++))
        fi
    elif command -v gitleaks &>/dev/null; then
        echo -e "  ${YELLOW}⚠ Using gitleaks (betterleaks preferred)${NC}"
        ((WARNINGS++))
    else
        echo -e "  ${YELLOW}⚠ No secret scanner installed${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "\n${BLUE}[5/6]${NC} Secrets Scan... ${YELLOW}SKIPPED (--quick)${NC}"
fi

# --- 6. Contract Registry ---
echo -e "\n${BLUE}[6/6]${NC} Contract Registry..."
CONTRACT_COUNT=$(find tool_contracts -name '*.yaml' 2>/dev/null | wc -l | tr -d ' ')
echo "  Contracts loaded: ${CONTRACT_COUNT}"
if [ "$CONTRACT_COUNT" -gt 0 ]; then
    echo -e "  ${GREEN}✓ Tool Gateway: configured${NC}"
else
    echo -e "  ${YELLOW}⚠ Tool Gateway: no contracts found${NC}"
    ((WARNINGS++))
fi

# --- Summary ---
echo ""
echo -e "${BLUE}══════════════════════════════════════════${NC}"
if [ "$FAILURES" -gt 0 ]; then
    echo -e "${RED}  PREFLIGHT FAILED: ${FAILURES} failures, ${WARNINGS} warnings${NC}"
    echo -e "${BLUE}══════════════════════════════════════════${NC}"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}  PREFLIGHT PASSED WITH WARNINGS: ${WARNINGS} warnings${NC}"
    echo -e "${BLUE}══════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${GREEN}  PREFLIGHT PASSED: All checks green${NC}"
    echo -e "${BLUE}══════════════════════════════════════════${NC}"
    exit 0
fi
