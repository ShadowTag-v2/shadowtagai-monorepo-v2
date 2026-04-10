#!/bin/bash
set -e

# CONFIG
PROJECT_ID="shadowtagai-current-project"
REGION="us-central1"
CLUSTER="agent-cluster"
CONFIG="agent-config"
WORKSTATION="brave-agent-workstation"
LOCAL_DIR="jetski-bridge"
REMOTE_DIR="/home/user/jetski-bridge"
BRIDGE_URL="https://bridge-server-227823808819.us-central1.run.app/control"

echo "📦 Zipping agent code..."
tar -czf agent_code.tar.gz -C "$LOCAL_DIR" .

echo "⏳ Waiting for workstation to be running..."
gcloud beta workstations start "$WORKSTATION" --cluster="$CLUSTER" --config="$CONFIG" --region="$REGION" --project="$PROJECT_ID" || true

# Wait a bit for SSH to be ready
echo "🔌 Connecting to workstation..."

# Copy files
echo "📤 Uploading code..."
# SCP replacement: Pipe tarball via SSH
cat agent_code.tar.gz | gcloud beta workstations ssh "$WORKSTATION" \
  --cluster="$CLUSTER" --config="$CONFIG" --region="$REGION" --project="$PROJECT_ID" \
  --command="cat > /home/user/agent_code.tar.gz"

# Setup remote
echo "🚀 Setting up remote environment..."
gcloud beta workstations ssh "$WORKSTATION" --cluster="$CLUSTER" --config="$CONFIG" --region="$REGION" --project="$PROJECT_ID" --command="
  mkdir -p $REMOTE_DIR
  tar -xzf agent_code.tar.gz -C $REMOTE_DIR
  cd $REMOTE_DIR
  
  echo '🛠️ Checking for Chrome...'
  if ! command -v google-chrome >/dev/null 2>&1; then
    echo '⚠️ Chrome not found. Installing...'
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt-get update && sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
    rm google-chrome-stable_current_amd64.deb
  fi

  echo '🌐 Starting Headless Chrome...'
  nohup google-chrome --headless=new --remote-debugging-port=9222 --no-sandbox --disable-gpu > chrome.log 2>&1 &
  sleep 5 # Wait for Chrome to warm up

  echo '📦 Installing dependencies...'
  npm install
  echo '✅ Agent deployed to $REMOTE_DIR'
  echo '🔑 Fetching Identity Token (via Metadata Server)...'
  export BRIDGE_CONTROL_URL="$BRIDGE_URL"
  # Audience must be the service root URL (strip /control)
  AUDIENCE="${BRIDGE_URL%/control}"
  export BRIDGE_TOKEN=\$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=\$AUDIENCE&format=full")

  echo '🚀 Starting Agent...'
  # Run in background or foreground? For now foreground to see logs.
  node agent.js
"

echo "🎉 Deployment Complete!"
rm agent_code.tar.gz
