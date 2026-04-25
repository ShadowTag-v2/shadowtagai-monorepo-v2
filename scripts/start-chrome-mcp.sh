#!/usr/bin/env bash
# scripts/start-chrome-mcp.sh — Launch Chrome with DevTools debug port for MCP
#
# WHY THIS EXISTS:
# macOS Chrome has two bugs that break the chrome-devtools-mcp connection:
#   1. Session Restore Merge: If Chrome is already running, `open -a` merges
#      the new instance into the existing process, silently dropping the
#      --remote-debugging-port flag. Fix: use --user-data-dir to force isolation.
#   2. WebSocket Origin Rejection: Chrome 147+ enforces strict WebSocket origin
#      security. Without --remote-allow-origins=*, Chrome drops the MCP server's
#      connection attempt, causing the Node process to crash with EOF.
#
# USAGE:
#   bash scripts/start-chrome-mcp.sh          # Start Chrome on port 9222
#   bash scripts/start-chrome-mcp.sh 9223     # Start Chrome on custom port
#   bash scripts/start-chrome-mcp.sh stop     # Kill the debug Chrome instance
#
# After starting, reload the IDE (Cmd+Shift+P → Developer: Reload Window)
# so the chrome-devtools-mcp server re-establishes its WebSocket connection.
#
# Reference: .beads/issues.jsonl entry from 2026-04-25

set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DEBUG_PROFILE="/tmp/chrome-debug-profile"
PORT="${1:-9222}"

# ─── Stop mode ───
if [[ "${1:-}" == "stop" ]]; then
  echo "Killing Chrome debug instance (profile: $DEBUG_PROFILE)..."
  pkill -9 -f "user-data-dir=$DEBUG_PROFILE" 2>/dev/null && echo "Killed." || echo "No debug instance found."
  exit 0
fi

# ─── Pre-flight: kill any existing debug Chrome on this port ───
if lsof -i :"$PORT" -P -n 2>/dev/null | grep -q LISTEN; then
  echo "Port $PORT already in use. Killing existing listener..."
  pkill -9 -f "remote-debugging-port=$PORT" 2>/dev/null || true
  sleep 2
fi

# ─── Ensure profile directory exists ───
mkdir -p "$DEBUG_PROFILE"

# ─── Launch Chrome detached with all required flags ───
echo "Launching Chrome on debug port $PORT..."
nohup "$CHROME" \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$DEBUG_PROFILE" \
  --remote-allow-origins="*" \
  --no-first-run \
  --no-default-browser-check \
  > /dev/null 2>&1 &

CHROME_PID=$!
echo "Chrome PID: $CHROME_PID"

# ─── Wait and verify ───
echo "Waiting for debug port to bind..."
for i in {1..10}; do
  sleep 1
  if curl -s "http://localhost:$PORT/json/version" > /dev/null 2>&1; then
    echo ""
    echo "✅ Chrome DevTools debug port $PORT is ACTIVE"
    curl -s "http://localhost:$PORT/json/version" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:$PORT/json/version"
    echo ""
    echo "Next: Reload your IDE (Cmd+Shift+P → Developer: Reload Window)"
    exit 0
  fi
  printf "."
done

echo ""
echo "❌ Chrome started (PID $CHROME_PID) but debug port $PORT did not respond in 10s."
echo "Check: lsof -i :$PORT"
exit 1
