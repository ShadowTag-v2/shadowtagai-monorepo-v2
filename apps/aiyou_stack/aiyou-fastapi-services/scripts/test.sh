#!/bin/bash
# Test script for ShadowTag-v2 FastAPI Services

set -e

echo "======================================"
echo "Running Tests"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    print_status "Virtual environment activated"
fi

# Run tests with coverage
echo "Running pytest with coverage..."
if pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html; then
    print_status "All tests passed"
else
    print_error "Tests failed"
    exit 1
fi

# Display coverage summary
echo ""
echo "======================================"
echo "Coverage Report"
echo "======================================"
echo "HTML coverage report available at: htmlcov/index.html"
echo ""

# Run type checking
if command -v mypy &> /dev/null; then
    echo "Running type checks..."
    if mypy app --ignore-missing-imports; then
        print_status "Type checking passed"
    else
        print_error "Type checking found issues"
    fi
fi

echo ""
print_status "Testing completed!"
