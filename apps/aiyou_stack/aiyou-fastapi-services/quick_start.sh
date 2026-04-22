#!/bin/bash
# Quick start script for local testing (no GCP credentials required)
set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Pnkln File Search - Quick Start (Mock Mode)                ║"
echo "║  No GCP credentials required!                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: python3 is required but not installed${NC}"
    exit 1
fi

echo -e "${BLUE}[1/5]${NC} Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

echo ""
echo -e "${BLUE}[2/5]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

echo ""
echo -e "${BLUE}[3/5]${NC} Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -e .
echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""
echo -e "${BLUE}[4/5]${NC} Creating mock environment configuration..."
cat > .env <<EOF
# Mock Mode Configuration (No GCP credentials needed)
MOCK_MODE=true
GCP_PROJECT_ID=mock-project
GCP_REGION=us-central1
GCP_STORAGE_BUCKET=gs://mock-bucket

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
LOG_LEVEL=INFO

# File Search Configuration
FILE_SEARCH_CHUNK_SIZE=512
FILE_SEARCH_CHUNK_OVERLAP=100
FILE_SEARCH_TOP_K=5

# Kill Switch Thresholds
KILL_SWITCH_FILE_SEARCH_P99_LATENCY=1000
KILL_SWITCH_CORPUS_SYNC_FAILURE_RATE=0.05
KILL_SWITCH_FALSE_POSITIVE_RATE=0.10

# Judge 6 Configuration
JUDGE_P99_LATENCY_TARGET=90
JUDGE_GEMINI_ALLOCATION=0.40
EOF
echo -e "${GREEN}✓${NC} Environment configured for mock mode"

echo ""
echo -e "${BLUE}[5/5]${NC} Starting service..."
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Service starting on http://localhost:8000${NC}"
echo ""
echo "Available endpoints:"
echo "  • http://localhost:8000/                    - Service info"
echo "  • http://localhost:8000/health              - Health check"
echo "  • http://localhost:8000/api/v1/verticals    - List verticals"
echo "  • http://localhost:8000/api/v1/query        - Process query"
echo "  • http://localhost:8000/metrics             - Prometheus metrics"
echo "  • http://localhost:8000/docs                - API documentation"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}NOTE: Running in MOCK MODE - no real GCP calls will be made${NC}"
echo ""
echo "To test the service, open another terminal and run:"
echo -e "  ${BLUE}./test_local.sh${NC}"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

# Run the service
python -m pnkln_file_search.main
