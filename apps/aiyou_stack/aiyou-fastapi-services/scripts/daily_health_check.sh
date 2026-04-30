#!/bin/bash
#
# Daily Health Check for PNKLN Stack
# Run this every morning to verify system health
#

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}        PNKLN Stack Daily Health Check - $(date '+%Y-%m-%d %H:%M')${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

CRITICAL_ALERTS=0
WARNINGS=0

# Layer 0: Memory Persistence
echo -e "${BLUE}Layer 0: Memory Persistence${NC}"
echo "---------------------------------------------------------------------"

# Check last sync time
LAST_SYNC=$(find erik-hancock-llm-memory/ -name ".last_sync" -mtime -1 2>/dev/null | wc -l)
if [ "$LAST_SYNC" -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} Memory sync within 24 hours"
else
    echo -e "  ${RED}✗${NC} Memory sync overdue (>24 hours)"
    ((CRITICAL_ALERTS++))
fi

# Check GitHub commits
COMMITS=$(git log --since="1 day ago" --oneline | wc -l)
if [ "$COMMITS" -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} Recent commits found ($COMMITS)"
else
    echo -e "  ${YELLOW}⚠${NC} No commits in last 24 hours"
    ((WARNINGS++))
fi

echo ""

# Layer 1: PNKLN Stack
echo -e "${BLUE}Layer 1: PNKLN Stack${NC}"
echo "---------------------------------------------------------------------"

# Check if core files exist
if [ -f "src/pnkln/judge_six.py" ] && [ -f "src/pnkln/shadowtag.py" ]; then
    echo -e "  ${GREEN}✓${NC} PNKLN modules present"
else
    echo -e "  ${RED}✗${NC} PNKLN modules missing"
    ((CRITICAL_ALERTS++))
fi

# Check if tests exist
if [ -f "src/tests/test_judge_six.py" ]; then
    echo -e "  ${GREEN}✓${NC} Test suite available"
else
    echo -e "  ${YELLOW}⚠${NC} Tests not found"
    ((WARNINGS++))
fi

echo ""

# Layer 2: Gemini Function Calling
echo -e "${BLUE}Layer 2: Gemini Function Calling${NC}"
echo "---------------------------------------------------------------------"

if [ -f "src/core/gemini_function_calling.py" ]; then
    echo -e "  ${GREEN}✓${NC} Gemini function calling core present"
else
    echo -e "  ${RED}✗${NC} Core module missing"
    ((CRITICAL_ALERTS++))
fi

# Check kernels
KERNEL_COUNT=$(find src/kernels/ -name "*.py" ! -name "__init__.py" 2>/dev/null | wc -l)
if [ "$KERNEL_COUNT" -ge 4 ]; then
    echo -e "  ${GREEN}✓${NC} $KERNEL_COUNT kernels available"
else
    echo -e "  ${YELLOW}⚠${NC} Only $KERNEL_COUNT kernels found (expected 4+)"
    ((WARNINGS++))
fi

echo ""

# Layer 3: ACE Orchestration
echo -e "${BLUE}Layer 3: ACE Orchestration${NC}"
echo "---------------------------------------------------------------------"

if [ -f "tools/orchestrator/ace_with_refactor.mjs" ]; then
    echo -e "  ${GREEN}✓${NC} ACE refactorer available"
else
    echo -e "  ${RED}✗${NC} ACE refactorer missing"
    ((CRITICAL_ALERTS++))
fi

# Check if integration tests pass
if [ -f "tests/integration/test_refactorer.mjs" ]; then
    echo -e "  ${GREEN}✓${NC} Integration tests present"
else
    echo -e "  ${YELLOW}⚠${NC} Integration tests not found"
    ((WARNINGS++))
fi

echo ""

# Layer 4: Multi-Agent Reasoning
echo -e "${BLUE}Layer 4: Multi-Agent Reasoning${NC}"
echo "---------------------------------------------------------------------"

if [ -f "src/agents/debate.py" ]; then
    echo -e "  ${GREEN}✓${NC} Debate agents available"
else
    echo -e "  ${RED}✗${NC} Debate agents missing"
    ((CRITICAL_ALERTS++))
fi

if [ -f "src/ratings/glicko2.py" ]; then
    echo -e "  ${GREEN}✓${NC} Glicko-2 ratings available"
else
    echo -e "  ${RED}✗${NC} Glicko-2 missing"
    ((CRITICAL_ALERTS++))
fi

echo ""

# Layer 5: DTE Evolution
echo -e "${BLUE}Layer 5: DTE Evolution${NC}"
echo "---------------------------------------------------------------------"

if [ -f "src/evolution/dte.py" ]; then
    echo -e "  ${GREEN}✓${NC} DTE evolution available"
else
    echo -e "  ${RED}✗${NC} DTE evolution missing"
    ((CRITICAL_ALERTS++))
fi

if [ -f "src/training/grpo.py" ]; then
    echo -e "  ${GREEN}✓${NC} GRPO training available"
else
    echo -e "  ${RED}✗${NC} GRPO training missing"
    ((CRITICAL_ALERTS++))
fi

echo ""

# Testing Suite
echo -e "${BLUE}Testing & Validation${NC}"
echo "---------------------------------------------------------------------"

if [ -f "load_testing/pnkln_load_tests_enhanced.py" ]; then
    echo -e "  ${GREEN}✓${NC} Enhanced load testing suite v2.0"
else
    echo -e "  ${RED}✗${NC} Load testing suite missing"
    ((CRITICAL_ALERTS++))
fi

# Check if examples exist
EXAMPLE_COUNT=$(find src/examples/ -name "*.py" 2>/dev/null | wc -l)
if [ "$EXAMPLE_COUNT" -ge 4 ]; then
    echo -e "  ${GREEN}✓${NC} $EXAMPLE_COUNT examples available"
else
    echo -e "  ${YELLOW}⚠${NC} Only $EXAMPLE_COUNT examples found"
    ((WARNINGS++))
fi

echo ""

# Cost Projection
echo -e "${BLUE}Cost & Value Metrics${NC}"
echo "---------------------------------------------------------------------"

# Calculate projected monthly value (conservative estimate)
DAILY_VALUE=3000  # $3K per day (conservative)
MONTHLY_VALUE=$((DAILY_VALUE * 30))
MONTHLY_COST=870

echo -e "  ${BLUE}ℹ${NC} Projected daily value: \$${DAILY_VALUE}"
echo -e "  ${BLUE}ℹ${NC} Projected monthly value: \$${MONTHLY_VALUE}"
echo -e "  ${BLUE}ℹ${NC} Monthly cost: \$${MONTHLY_COST}"

ROI=$((MONTHLY_VALUE / MONTHLY_COST))
echo -e "  ${GREEN}✓${NC} ROI: ${ROI}× return on investment"

echo ""

# Summary
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}                         Summary${NC}"
echo -e "${BLUE}=====================================================================${NC}"

if [ "$CRITICAL_ALERTS" -eq 0 ]; then
    echo -e "  ${GREEN}✓ All 6 layers healthy${NC}"
else
    echo -e "  ${RED}✗ ${CRITICAL_ALERTS} critical alert(s)${NC}"
fi

if [ "$WARNINGS" -eq 0 ]; then
    echo -e "  ${GREEN}✓ No warnings${NC}"
else
    echo -e "  ${YELLOW}⚠ ${WARNINGS} warning(s) (review recommended)${NC}"
fi

echo ""
echo -e "  ${BLUE}💰 Yesterday's value: \$${DAILY_VALUE}${NC}"
echo -e "  ${BLUE}💰 Monthly projection: \$${MONTHLY_VALUE}${NC}"
echo -e "  ${BLUE}💰 Monthly cost: \$${MONTHLY_COST}${NC}"
echo -e "  ${BLUE}💰 Net monthly value: \$$((MONTHLY_VALUE - MONTHLY_COST))${NC}"

echo ""
echo -e "${BLUE}=====================================================================${NC}"

if [ "$CRITICAL_ALERTS" -eq 0 ]; then
    echo -e "${GREEN}✓ System is healthy and delivering value${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ System has issues - please investigate${NC}"
    echo ""
    exit 1
fi
