#!/bin/bash
set -e

# Start Uvicorn in the background
echo "🚀 Starting n-autoresearch/Kosmos/BioAgents Server (Uvicorn) on port $PORT..."
uvicorn src.main:app --host 0.0.0.0 --port $PORT &

# Start ttyd in the foreground on port 7681
# --writable allows clients to type in the terminal
echo "🐞 Starting ttyd Debug Shell on port $TTYD_PORT..."
exec ttyd --port $TTYD_PORT --writable bash
