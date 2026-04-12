#!/bin/bash
echo "🔍 Antigravity System Verification"
echo "================================"

# 1. Check Python Bridge Server
echo -n "Checking Bridge Server (Port 3025)... "
if curl -s http://localhost:3025/health | grep -q "ok"; then
    echo "✅ ONLINE"
else
    echo "❌ OFFLINE (Check 'bridge.log')"
fi

# 2. Check Chrome Remote Debugging
echo -n "Checking Chrome Debugger (Port 9222)... "
if curl -s http://localhost:9222/json/version | grep -q "Browser"; then
    echo "✅ ONLINE"
else
    echo "❌ OFFLINE (Is Chrome running?)"
fi

# 3. Test Bridge Connection
echo "Testing Bridge Command (GET_DOM)..."
RESPONSE=$(curl -s -X POST http://localhost:3025/command \
  -H "Content-Type: application/json" \
  -d '{"action": "GET_DOM", "payload": {}}')

if echo "$RESPONSE" | grep -q "tag"; then
    echo "✅ SUCCESS: DOM Received!"
    echo "Sample: $(echo $RESPONSE | colrm 80)..."
else
    echo "❌ FAILED: $RESPONSE"
    echo "Troubleshooting:"
    echo "1. Open Chrome in the VNC session."
    echo "2. Check if 'Antigravity Bridge' extension is active."
    echo "3. Click 'Inspect' on the extension backgound page to see errors."
fi
