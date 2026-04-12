#!/bin/bash

# Vertex AI Workbench Startup Script
# This script sets up the Code Refactorer service in a Vertex AI Workbench instance

set -e

echo "======================================"
echo "Vertex AI Workbench Setup"
echo "Code Refactorer Service"
echo "======================================"

# Update system packages
echo "[1/5] Updating system packages..."
sudo apt-get update -qq

# Install Python dependencies
echo "[2/5] Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Set up environment variables
echo "[3/5] Setting up environment..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Application Configuration
APP_NAME=AI Code Refactorer Service
DEBUG=false
HOST=0.0.0.0
PORT=8080

# Claude Configuration
ANTHROPIC_API_KEY=your-api-key-here
MODEL=claude-sonnet-4-5-20250929
MAX_TOKENS=4096

# Vertex AI Configuration
VERTEX_PROJECT_ID=your-project-id
VERTEX_LOCATION=us-central1
EOF
    echo "Created .env file - please update with your configuration"
fi

# Create logs directory
echo "[4/5] Creating logs directory..."
mkdir -p logs

# Start the service
echo "[5/5] Starting Code Refactorer service..."
echo ""
echo "To start the service, run:"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"
echo ""
echo "Or to run in the background:"
echo "  nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > logs/service.log 2>&1 &"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8080/docs"
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
