#!/bin/bash
set -e

echo "///▞ GIDEON OS :: Starting Deployment"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set up PYTHONPATH to include the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Ensure the deployment script exists
if [ ! -f "scripts/gideon_os/main_deployment.py" ]; then
    echo "❌ Error: scripts/gideon_os/main_deployment.py not found."
    exit 1
fi

echo "🚀 Executing main deployment..."
python3 scripts/gideon_os/main_deployment.py
