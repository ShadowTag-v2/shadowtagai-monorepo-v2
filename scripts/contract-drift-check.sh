#!/usr/bin/env bash
# scripts/contract-drift-check.sh — Monorepo OS
# Checks tool contract drift and configuration consistency
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "▸ Checking tool contracts and configuration drift..."

ERRORS=0

# 1. Check if tool_contracts exist and have valid structure
if [ -d "$REPO_ROOT/tool_contracts" ]; then
    for contract in "$REPO_ROOT"/tool_contracts/*.yaml; do
        if ! grep -qE "^(tool_id|name|version):" "$contract"; then
            echo "  [ERROR] Contract $contract missing 'tool_id:', 'name:', or 'version:'"
            ERRORS=$((ERRORS + 1))
        fi
    done
else
    echo "  [ERROR] tool_contracts/ directory missing."
    ERRORS=$((ERRORS + 1))
fi

# 2. Check MCP Config exists
MCP_CONFIG="$REPO_ROOT/antigravity-mcp-config.json"
if [ ! -f "$MCP_CONFIG" ]; then
    echo "  [ERROR] antigravity-mcp-config.json missing."
    ERRORS=$((ERRORS + 1))
else
    # Simple check for required servers
    for server in "firebase-mcp-server" "chrome-devtools-mcp" "StitchMCP" "google-developer-knowledge" "sequential-thinking"; do
        if ! grep -q "\"$server\"" "$MCP_CONFIG"; then
            echo "  [ERROR] MCP Config missing required server: $server"
            ERRORS=$((ERRORS + 1))
        fi
    done
fi

if [ "$ERRORS" -gt 0 ]; then
    echo "▸ Contract drift detected! $ERRORS errors found."
    exit 1
else
    echo "▸ Contract drift check passed. Configurations are aligned."
fi
