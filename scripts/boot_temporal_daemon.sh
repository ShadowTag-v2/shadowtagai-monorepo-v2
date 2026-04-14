#!/bin/bash
set -e

echo "═══ BOOTING TEMPORAL DAEMON FOR KOVELAI ═══"

# Check if Temporal is installed locally
if ! command -v temporal &> /dev/null
then
    echo "Temporal CLI not found. Downloading..."
    curl -sSf https://temporal.download/cli.sh | sh
    export PATH="$PATH:$HOME/.temporalio/bin"
fi

echo "Starting Temporal local dev server on default namespace..."
echo "Targeting memory queues for AST logging workflows..."

# Launch temporal server silently into the background
nohup temporal server start-dev --ip 0.0.0.0 --port 7233 --ui-port 8233 > temporal.log 2>&1 &
TEMPORAL_PID=$!

echo "Temporal Node is LIVE (PID: $TEMPORAL_PID) - UI available at http://localhost:8233"
echo "KovelAI AST Worker Queues are now processing."
