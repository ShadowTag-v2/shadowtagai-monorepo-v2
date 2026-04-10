#!/bin/bash
# rkill_swarm.sh - The Antigravity Kill Switch
# IMMEDIATE TERMINATION of all Agentic Processes

echo "🚨 ACTIVATING KILL CHAIN PROTOCOL..."

# 1. Local Process Termination (The "Double Tap")
echo "🔫 Terminating Local Processes..."
pkill -9 -f "n-autoresearch/Kosmos/BioAgents"
pkill -9 -f "genkit"
pkill -9 -f "uvicorn"
pkill -9 -f "python3.*agents"

# 2. Docker Purge (The "Container Nuke")
echo "💥 Killing Docker Containers..."
if command -v docker &> /dev/null; then
    docker kill $(docker ps -q --filter "label=type=agent") 2>/dev/null
    docker rm -f $(docker ps -aq --filter "label=type=agent") 2>/dev/null
fi

# 3. Network Block (Optional - requires sudo)
# echo "🛡️ Blocking Agent Ports..."
# sudo lsof -ti:8600 | xargs kill -9 2>/dev/null

echo "✅ KILL CHAIN COMPLETE. Swarm neutralized."
echo "📝 Check logs in BigQuery for forensic analysis."
