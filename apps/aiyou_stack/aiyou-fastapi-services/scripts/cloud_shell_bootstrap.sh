#!/bin/bash
# n-autoresearch/Kosmos/BioAgents Bootstrap for Google Cloud Shell
# Run this to enable n-autoresearch/Kosmos/BioAgents as Gemini's agent backend

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  n-autoresearch/Kosmos/BioAgents CLOUD SHELL BOOTSTRAP                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Clone or update repo
if [ -d "$HOME/ShadowTag-v2-fastapi-services" ]; then
    echo ">>> Updating existing repo..."
    cd "$HOME/ShadowTag-v2-fastapi-services"
    git pull --quiet 2>/dev/null || true
else
    echo ">>> Cloning ShadowTag-v2-fastapi-services..."
    cd "$HOME"
    git clone https://github.com/ShadowTag-v2-stack/ShadowTag-v2-fastapi-services.git
    cd "$HOME/ShadowTag-v2-fastapi-services"
fi

# Install dependencies
echo ">>> Installing dependencies..."
pip install --quiet --upgrade \
    fastapi \
    uvicorn \
    pydantic \
    google-generativeai \
    anthropic \
    httpx

# Check for existing server
if curl -s http://localhost:8600/health > /dev/null 2>&1; then
    echo ">>> n-autoresearch/Kosmos/BioAgents already running!"
    curl -s http://localhost:8600/health | python3 -m json.tool
    exit 0
fi

# Start server
echo ">>> Starting n-autoresearch/Kosmos/BioAgents server..."
cd "$HOME/ShadowTag-v2-fastapi-services"
nohup python3 bin/n-autoresearch/Kosmos/BioAgents-server > /tmp/n-autoresearch/Kosmos/BioAgents.log 2>&1 &
SERVER_PID=$!

# Wait for startup
echo ">>> Waiting for server startup..."
for i in {1..10}; do
    if curl -s http://localhost:8600/health > /dev/null 2>&1; then
        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║  n-autoresearch/Kosmos/BioAgents READY                                         ║"
        echo "║  ─────────────────────────────────────────────────────────── ║"
        echo "║  Server: http://localhost:8600                               ║"
        echo "║  PID: $SERVER_PID                                            ║"
        echo "║  Log: /tmp/n-autoresearch/Kosmos/BioAgents.log                                 ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
        echo "Endpoints:"
        echo "  POST /task       - Run task (JURA auto-routing)"
        echo "  POST /governance - High-stakes decisions (PRO tier)"
        echo "  GET  /health     - Health check"
        echo "  GET  /jura/stats - Cost tracking"
        echo ""
        echo "Example:"
        echo '  curl -X POST http://localhost:8600/task \'
        echo '    -H "Content-Type: application/json" \'
        echo '    -d '"'"'{"prompt": "analyze this code", "agents": 3}'"'"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "ERROR: Server failed to start. Check /tmp/n-autoresearch/Kosmos/BioAgents.log"
cat /tmp/n-autoresearch/Kosmos/BioAgents.log
exit 1
