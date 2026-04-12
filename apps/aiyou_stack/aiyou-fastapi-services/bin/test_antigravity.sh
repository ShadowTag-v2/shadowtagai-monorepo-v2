#!/bin/bash

echo "🔹 ANTIGRAVITY INTEGRATION TEST 🔹"
echo "==================================="

# 1. Check MCP Config
if [ -f "/Users/pikeymickey/.gemini/antigravity/mcp_config.json" ]; then
    echo "✅ [PASS] mcp_config.json exists."
    # Optional: Basic JSON check (requires jq, using grep for simplicity)
    if grep -q "chrome-devtools-mcp" "/Users/pikeymickey/.gemini/antigravity/mcp_config.json"; then
         echo "   ├── Content verification: OK"
    else
         echo "   └── ❌ Content verification: MISSING 'chrome-devtools-mcp'"
    fi
else
    echo "❌ [FAIL] mcp_config.json NOT found."
fi

# 2. Check GEMINI.md Protocols
if [ -f "ShadowTag-Omega/GEMINI.md" ]; then
    echo "✅ [PASS] GEMINI.md exists."
    if grep -q "VIBE CODING PROTOCOLS" "ShadowTag-Omega/GEMINI.md"; then
        echo "   ├── Vibe Protocols: OK"
    else
        echo "   └── ❌ Vibe Protocols: MISSING"
    fi
    if grep -q "DOE FRAMWORK" "ShadowTag-Omega/GEMINI.md"; then
        echo "   ├── DOE Framework: OK"
    else
        echo "   └── ❌ DOE Framework: MISSING"
    fi
else
    echo "❌ [FAIL] GEMINI.md NOT found in ShadowTag-Omega/."
fi

# 3. Check Memory Structure
if [ -f "ShadowTag-Omega/.gemini/memory/beads_structure.md" ]; then
    echo "✅ [PASS] Beads Memory Structure exists."
else
    echo "❌ [FAIL] Beads Memory Structure NOT found."
fi

# 4. Check Chrome Debugging Port (MacOS specific)
echo "Checking for Chrome Debugging Port (9222)..."
if lsof -i :9222 > /dev/null; then
    echo "✅ [PASS] Port 9222 is ACTIVE (Chrome is likely running)."
else
    echo "⚠️ [WARN] Port 9222 is CLOSED."
    echo "   👉 Run: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222"
fi

echo "==================================="
echo "Test Complete."
