#!/bin/bash
set -e

# Configuration
export BRIDGE_URL="https://bridge-server-227823808819.us-central1.run.app/control"
export CHROME_DEBUG_URL="http://127.0.0.1:9222"
export BRIDGE_CONTROL_URL="$BRIDGE_URL"

echo "🔑 Generating Identity Token..."
# Audience must be the service root URL (strip /control)
AUDIENCE="${BRIDGE_URL%/control}"
export BRIDGE_TOKEN=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=$AUDIENCE&format=full")

echo "🔑 Generating API Token..."
API_AUD="https://seatjudge-api-poaakxhkkq-uc.a.run.app"
export API_TOKEN=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=$API_AUD&format=full")

echo "🌐 Starting Chrome..."
pkill chrome || true
nohup google-chrome --headless=new --remote-debugging-port=9222 --no-sandbox --disable-gpu > /home/user/chrome.log 2>&1 &

echo "⏳ Waiting for Chrome..."
for i in {1..15}; do
  if curl -s http://127.0.0.1:9222/json/version >/dev/null; then
    echo "✅ Chrome is ready!"
    break
  fi
  sleep 1
done

cd /home/user/jetski-bridge
echo "🚀 Running Agent..."
node agent.js
