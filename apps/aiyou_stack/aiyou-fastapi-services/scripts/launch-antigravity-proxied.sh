#!/bin/bash
#==============================================================================
# Launch Antigravity IDE through Load-Balancing Proxy
#==============================================================================
# This script starts mitmproxy with multi-key rotation and launches Antigravity
# through the proxy to avoid rate limiting with 14 license credentials.
#
# Prerequisites:
#   1. brew install mitmproxy
#   2. Copy keys.json.template to keys.json and fill in API keys
#   3. Trust mitmproxy CA cert (one-time): run mitmproxy once, then:
#      - Open Keychain Access
#      - Find "mitmproxy" certificate
#      - Right-click → Get Info → Trust → Always Trust
#
# Usage:
#   ./scripts/launch-antigravity-proxied.sh
#==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
PROXY_DIR="$BASE_DIR/tools/antigravity-proxy"
PROXY_PORT=8080
STATS_URL="http://localhost:$PROXY_PORT/__proxy_stats__"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ANTIGRAVITY LOAD BALANCER PROXY                             ║${NC}"
echo -e "${BLUE}║  Round-robin across 14 Gemini licenses                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# Check for keys.json
if [ ! -f "$PROXY_DIR/keys.json" ]; then
    echo -e "${YELLOW}WARNING: keys.json not found${NC}"
    echo "Creating from template..."
    if [ -f "$PROXY_DIR/keys.json.template" ]; then
        cp "$PROXY_DIR/keys.json.template" "$PROXY_DIR/keys.json"
        echo -e "${YELLOW}Please edit $PROXY_DIR/keys.json with your API keys${NC}"
        echo "Then run this script again."
        exit 1
    else
        echo -e "${RED}ERROR: keys.json.template not found${NC}"
        exit 1
    fi
fi

# Count keys
KEY_COUNT=$(grep -c '"api_key"' "$PROXY_DIR/keys.json" 2>/dev/null || echo "0")
echo -e "${GREEN}>>> Loaded $KEY_COUNT API keys for rotation${NC}"


# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}>>> Cleanup complete${NC}"
}
trap cleanup EXIT

# Check for Antigravity app
ANTIGRAVITY_PATH="/Applications/Antigravity.app/Contents/MacOS/Antigravity"
if [ ! -x "$ANTIGRAVITY_PATH" ]; then
    # Try alternate locations
    ANTIGRAVITY_PATH=$(mdfind "kMDItemCFBundleIdentifier == 'dev.antigravity.Antigravity'" 2>/dev/null | head -1)
    if [ -n "$ANTIGRAVITY_PATH" ]; then
        ANTIGRAVITY_PATH="$ANTIGRAVITY_PATH/Contents/MacOS/Antigravity"
    fi
fi

if [ -x "$ANTIGRAVITY_PATH" ]; then
  echo "Launching Antigravity (proxy removed)"
  "$ANTIGRAVITY_PATH" &
  wait $!
else
  echo "Antigravity not found; proxy removed."
fi
