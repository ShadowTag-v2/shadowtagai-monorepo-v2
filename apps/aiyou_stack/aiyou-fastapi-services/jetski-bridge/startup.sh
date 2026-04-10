#!/bin/bash

# startup.sh - The "Glue" that boots the Headless Agent

# 1. Install Dependencies (if not baked into image)
echo "Installing dependencies..."
# Assumes Node.js is available or handled by the environment
npm install

# 2. Start the Bridge Server in Background
echo "Starting Bridge Server..."
node bridge-server.js &
BRIDGE_PID=$!
echo "Bridge PID: $BRIDGE_PID"

# 3. Launch Chrome/Brave with Extension
# Note: In a real Cloud Workstation, this might be 'google-chrome'
echo "Launching Browser..."
/usr/bin/google-chrome-stable \
  --no-sandbox \
  --load-extension=$(pwd)/bridge-extension \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/agent-profile \
  --start-maximized &

# 4. Wait for Browser to Warm Up
sleep 5

# 5. Run the Agent (Self-Driving)
echo "Starting Agent Brain..."
node agent.js "$1"

# Cleanup on exit
kill $BRIDGE_PID
