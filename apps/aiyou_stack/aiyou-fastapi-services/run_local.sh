#!/bin/bash
# Quick start script for Mac local testing
# Usage: ./run_local.sh

set -e

echo "🚀 Omega Governance Service - Mac Local Quick Start"
echo "=================================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Install from https://www.python.org/downloads/"; exit 1; }

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "✓ Installing dependencies (this may take 2-3 minutes)..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "=================================================="
echo "🎯 Starting FastAPI server on http://127.0.0.1:8000"
echo "=================================================="
echo ""
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo "🏥 Health Check: http://127.0.0.1:8000/health"
echo "📖 ReDoc: http://127.0.0.1:8000/redoc"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Run the server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
