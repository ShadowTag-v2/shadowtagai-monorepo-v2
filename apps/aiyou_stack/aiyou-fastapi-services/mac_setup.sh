#!/bin/bash
#
# Pnkln Agent Platform - Mac Local Setup
# v0.2.0 - Collection → Enforcement Pipeline
#
# Usage: ./mac_setup.sh

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "  PNKLN AGENT PLATFORM - MAC LOCAL SETUP"
echo "  Version: 0.2.0 (Collection → Enforcement)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}[1/7] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗ Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    echo "  Install with: brew install python@3.11"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Create virtual environment
echo -e "${YELLOW}[2/7] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "  Virtual environment exists, removing..."
    rm -rf venv
fi
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate virtual environment
echo -e "${YELLOW}[3/7] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}[4/7] Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel --quiet
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Install dependencies
echo -e "${YELLOW}[5/7] Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Install package in development mode
echo -e "${YELLOW}[6/7] Installing pnkln_agents in development mode...${NC}"
pip install -e . --quiet
echo -e "${GREEN}✓ Package installed${NC}"

# Run validation tests
echo -e "${YELLOW}[7/7] Running validation tests...${NC}"
python -c "
from pnkln_agents import (
    IntelligenceAgent,
    ComplianceSDRAgent,
    GeminiIngestionLayer,
    JREngine,
    JudgeSixLite,
    DEFAULT_SOURCES,
    DEFAULT_CONSTRAINTS,
)
print('✓ All core imports successful')
print('✓ IntelligenceAgent: OK')
print('✓ ComplianceSDRAgent: OK')
print('✓ GeminiIngestionLayer: OK')
print('✓ JREngine: OK')
print('✓ JudgeSixLite: OK')
print('✓ DEFAULT_SOURCES: {} sources'.format(len(DEFAULT_SOURCES)))
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Validation tests passed${NC}"
else
    echo -e "${RED}✗ Validation tests failed${NC}"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}  ✓ SETUP COMPLETE${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run demo: python examples/mac_local_demo.py"
echo "  3. Run tests: pytest tests/"
echo ""
echo "Deactivate venv: deactivate"
echo ""
