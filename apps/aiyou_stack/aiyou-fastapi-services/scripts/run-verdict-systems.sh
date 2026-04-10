#!/bin/bash
# Verdict Systems - Quick Start Script

set -e

echo "========================================"
echo "Verdict Systems - Starting Services"
echo "========================================"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn not found. Please install requirements."
    echo "pip install -r requirements.txt"
    exit 1
fi

# Set python path to include src
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

echo "Starting API Server on port 8001..."
# Run with reload for development
uvicorn src.verdict_systems.api.main:app --reload --port 8001
