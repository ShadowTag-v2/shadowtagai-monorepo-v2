#!/bin/bash
# Run n-autoresearch/Kosmos/BioAgents v8 API Server

cd "$(dirname "$0")"

# Set API key if not already set
# export ANTHROPIC_API_KEY="your-key-here"

echo "🐵 Starting n-autoresearch/Kosmos/BioAgents v8 API..."
echo "   Server: http://localhost:8888"
echo "   Docs:   http://localhost:8888/docs"
echo ""

python3 -m uvicorn api.n-autoresearch/Kosmos/BioAgents_api:app --host 0.0.0.0 --port 8888 --reload
