#!/usr/bin/env bash
set -e

# Check if mitmproxy is installed
if ! command -v mitmproxy &> /dev/null; then
    echo "mitmproxy could not be found. Please install it:"
    echo "brew install mitmproxy"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo ".env file not found!"
    exit 1
fi

echo "Starting Antigravity Proxy with Key Rotation..."
echo "Proxy listening on port 8080"
mitmproxy -s scripts/mitmproxy_rotation.py --listen-port 8080
