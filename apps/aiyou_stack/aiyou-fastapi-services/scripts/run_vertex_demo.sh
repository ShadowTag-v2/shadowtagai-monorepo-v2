#!/bin/bash
set -e

# Setup script for Vertex AI Live API Demo
# Handles directory navigation, dependency installation, and running the demo.

# Ensure we are in the project root
cd "$(dirname "$0")/.."

echo "🚀 Starting Vertex AI Live API Demo Setup..."

# Check for Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python 3 not found."
    exit 1
fi

echo "✅ Using python: $PYTHON_CMD"

# Install dependency if missing
echo "📦 Checking dependencies..."
$PYTHON_CMD -m pip install google-genai --quiet
echo "✅ Dependencies ready."

# Run Demo
echo "▶️ Running examples/vertex_live_api_demo.py..."
$PYTHON_CMD examples/vertex_live_api_demo.py
