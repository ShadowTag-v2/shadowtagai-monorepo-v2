#!/bin/bash
# Run Plan Mode Service locally for development and testing

set -e

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Error: ANTHROPIC_API_KEY environment variable not set"
  echo "Usage: export ANTHROPIC_API_KEY='your-key' && ./run-local.sh"
  exit 1
fi

# Configuration
export PORT="${PORT:-8000}"
export PLAN_MODE_TEMPLATE_PATH="${PLAN_MODE_TEMPLATE_PATH:-../../PLAN_MODE_TEMPLATE.md}"

echo "Starting Plan Mode Service locally..."
echo "Port: $PORT"
echo "Template: $PLAN_MODE_TEMPLATE_PATH"

# Install dependencies if needed
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "Starting server..."
echo "API available at: http://localhost:$PORT"
echo "Docs available at: http://localhost:$PORT/docs"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
