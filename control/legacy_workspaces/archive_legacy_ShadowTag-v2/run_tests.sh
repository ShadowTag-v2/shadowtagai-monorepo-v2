#!/bin/bash
# Test Runner for Judge #6 HITL System

set -e

echo "========================================"
echo "Judge #6 HITL System - Test Suite"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2 PASSED${NC}"
    else
        echo -e "${RED}✗ $2 FAILED${NC}"
    fi
}

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
pip install -q pytest pytest-cov pytest-asyncio httpx

echo ""

# Run unit tests
echo "========================================"
echo "Running Unit Tests"
echo "========================================"
pytest tests/unit/ -v --cov=src --cov-report=term-missing
UNIT_STATUS=$?
print_status $UNIT_STATUS "Unit Tests"
echo ""

# Run integration tests
echo "========================================"
echo "Running Integration Tests"
echo "========================================"
pytest tests/integration/ -v
INTEGRATION_STATUS=$?
print_status $INTEGRATION_STATUS "Integration Tests"
echo ""

# Run latency validation
echo "========================================"
echo "Running Latency Validation (p99 ≤90ms)"
echo "========================================"
python tests/performance/latency_validation.py --samples 1000
LATENCY_STATUS=$?
print_status $LATENCY_STATUS "Latency Validation"
echo ""

# Run performance benchmarks (optional)
if [ "$1" = "--full" ]; then
    echo "========================================"
    echo "Running Performance Benchmarks"
    echo "========================================"
    python tests/performance/benchmark.py
    BENCHMARK_STATUS=$?
    print_status $BENCHMARK_STATUS "Performance Benchmarks"
    echo ""
fi

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"
print_status $UNIT_STATUS "Unit Tests"
print_status $INTEGRATION_STATUS "Integration Tests"
print_status $LATENCY_STATUS "Latency Validation"

if [ "$1" = "--full" ]; then
    print_status $BENCHMARK_STATUS "Performance Benchmarks"
fi

echo ""

# Exit with failure if any test failed
if [ $UNIT_STATUS -ne 0 ] || [ $INTEGRATION_STATUS -ne 0 ] || [ $LATENCY_STATUS -ne 0 ]; then
    echo -e "${RED}Some tests failed. See output above for details.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
