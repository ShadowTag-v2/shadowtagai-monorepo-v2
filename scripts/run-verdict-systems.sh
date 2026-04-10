#!/bin/bash
# Verdict Systems - Quick Start Script

set -e

echo "========================================"
echo "Verdict Systems - Starting Services"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if PostgreSQL is running (optional for dev)
if command -v psql &> /dev/null; then
    echo "PostgreSQL detected"
else
    echo "Warning: PostgreSQL not detected. Using in-memory storage for development."
fi

# Start Verdict Systems API
echo "========================================"
echo "Starting Verdict Systems API on port 8001"
echo "========================================"
echo ""
echo "📚 API Documentation: http://localhost:8001/docs"
echo "📊 Dashboard: http://localhost:8001/"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"

uvicorn src.verdict_systems.api.main:app --host 0.0.0.0 --port 8001 --reload
