#!/usr/bin/env bash
set -euo pipefail

# --- 1. MOUNT FILESTORE (The "Shared Drive") ---
# We use the IP we injected via Terraform env vars
if [ -z "${FILESTORE_IP:-}" ]; then
    echo "WARNING: FILESTORE_IP not set. Skipping mount."
else
    mkdir -p /mnt/agent_share
    echo "Mounting Filestore from $FILESTORE_IP..."
    if ! command -v mount &> /dev/null; then
        apt-get update && apt-get install -y nfs-common || true
    fi
    mount -o nolock "$FILESTORE_IP":/${FILE_SHARE_NAME:-monorepo} /mnt/agent_share || echo "WARNING: Mount failed (Is Filestore Ready?)"
fi

# --- 2. INSTALL DEPENDENCIES (The "Environment") ---
# Check if Node is installed, if not, set it up (Idempotent)
if ! command -v node &> /dev/null; then
    echo "Installing Brave, Node.js, and Antigravity Dependencies..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

    # Brave Browser Repo
    curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list

    apt-get update && apt-get install -y \
        nodejs \
        brave-browser \
        xvfb \
        git \
        libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
        libgbm1 libasound2 libnss3-dev libgdk-pixbuf2.0-dev libgtk-3-dev libxss-dev

    # Symlink Brave to Google Chrome for compatibility
    ln -sf /usr/bin/brave-browser /usr/bin/google-chrome
fi

# --- 3. DEPLOY AGENT CODE (The "Brain") ---
# Clone or Pull your repo to the persistent home directory
WORK_DIR="/home/user/agent-platform"
if [ ! -d "$WORK_DIR" ]; then
    # INSTRUCTION: Update this URL to your actual repository
    # Using placeholder as explicit in original script
    git clone https://github.com/YOUR_ORG/agent-repo.git "$WORK_DIR" || echo "Git clone failed (check repo URL)"
else
    cd "$WORK_DIR" && git pull || echo "Git pull failed"
fi

# Ensure bridge directory
if [ -d "$WORK_DIR/jetski-bridge" ]; then
    cd "$WORK_DIR/jetski-bridge" && npm install
fi

# --- 4. START THE BRIDGE & WORKER (The "Process") ---
# Kill old processes if restarting
pkill -f "uvicorn.*bridge_server" || true
pkill -f "antigravity-worker" || true

# Install Python Bridge Dependencies
pip3 install fastapi uvicorn websockets pydantic || true

# Start Xvfb (Virtual Display) for Headless Chrome
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Start the Python Jetski Bridge Server (Port 3025)
# We run from module path
if [ -d "$WORK_DIR" ]; then
    export PYTHONPATH="$WORK_DIR"
    nohup python3 -m uvicorn libs.arsenal.jetski.bridge_server:app --host 0.0.0.0 --port 3025 > bridge.log 2>&1 &
fi

# Start the Antigravity Worker (if applicable)
# nohup python3 libs/worker.py > agent.log 2>&1 &

# --- 5. ANTIGRAVITY WORKSTATION FIXES (The "502" Prevention) ---
# Fix 1: Install Socat and GPU libs if missing (Headless support)
apt-get update && apt-get install -y socat libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 || true

# Fix 2: Port Forwarding (Gateway 80 -> Internal 8080)
# Cloud Workstation Gateway usually sends traffic to port 80.
# We forward this to our Antigravity/Bridge server on 8080.
echo ">>> 🔗 Starting Socat Port Forwarder (80 -> 8080)..."
nohup socat TCP-LISTEN:80,fork TCP:127.0.0.1:8080 > socat.log 2>&1 &

# Fix 3: Force Antigravity to Bind 0.0.0.0 (If running)
# We kill the default instance (which might bind to 127.0.0.1) and restart it.
if pgrep -f "antigravity-server" > /dev/null; then
    echo ">>> 🔄 Restarting Antigravity Server on 0.0.0.0..."
    pkill -f antigravity-server || true
    sleep 2
    # Re-launch with the "Headless Patch" flags
    nohup antigravity-server \
      --host 0.0.0.0 \
      --port 8080 \
      --without-connection-token \
      --no-sandbox \
      --disable-gpu-sandbox \
      --disable-dev-shm-usage \
      --enable-features=UseOzonePlatform \
      --ozone-platform=wayland > antigravity.log 2>&1 &
fi

# --- 6. UPHILLSNOWBALL COCKPIT (Chrome Remote Desktop) ---
# See: https://medium.com/google-cloud/using-chrome-remote-desktop-to-run-antigravity
echo "🖥️  Installing UphillSnowball GUI (XFCE + Chrome Remote Desktop)..."

# Install Desktop Environment (Lightweight XFCE)
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xfce4 \
    xfce4-goodies \
    xserver-xorg-video-dummy \
    xbase-clients \
    chrome-remote-desktop || echo "Failed to install Desktop Environment"

# Configure Session
echo "xfce4-session" > /root/.chrome-remote-desktop-session
# Also for the 'user' if running as non-root (Cloud Workstations default user is 'user')
if id "user" &>/dev/null; then
    echo "xfce4-session" > /home/user/.chrome-remote-desktop-session
    chown user:user /home/user/.chrome-remote-desktop-session
fi

# Disable LightDM/GDM to save resources (we use CRD)

# --- 7. ANTIGRAVITY BRIDGE EXTENSION (Custom Browser Automation) ---
BRIDGE_DIR="/opt/antigravity/bridge"
mkdir -p "$BRIDGE_DIR"

# 7.1 Create Manifest
cat > "$BRIDGE_DIR/manifest.json" <<EOF
{
  "manifest_version": 3,
  "name": "Antigravity Bridge",
  "version": "1.0",
  "description": "Bridge for custom browser automation via CDP",
  "permissions": [
    "debugger",
    "tabs",
    "scripting",
    "activeTab"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "background": {
    "service_worker": "background.js"
  }
}
EOF

# 7.2 Create Background Script
cat > "$BRIDGE_DIR/background.js" <<EOF
/* global chrome, console, WebSocket */
// Antigravity Bridge - Background Service Worker
// Connected to Jetski Bridge via WebSocket

const BRIDGE_URL = "ws://127.0.0.1:3025/ws";
let socket = null;
let retryInterval = 1000;

console.log("Antigravity Bridge: Loaded");

function connect() {
    console.log(\`Connecting to \${BRIDGE_URL}...\`);
    socket = new WebSocket(BRIDGE_URL);

    socket.onopen = () => {
        console.log("Antigravity Bridge: Connected to Jetski");
        retryInterval = 1000; // Reset retry interval
    };

    socket.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        console.log("Received command:", message);

        try {
            const result = await handleCommand(message);
            sendResponse(message.id, "success", result);
        } catch (error) {
            console.error("Command failed:", error);
            sendResponse(message.id, "error", null, error.message);
        }
    };

    socket.onclose = () => {
        console.log("Antigravity Bridge: Disconnected. Retrying...");
        socket = null;
        setTimeout(connect, retryInterval);
        retryInterval = Math.min(retryInterval * 2, 30000);
    };

    socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        socket.close();
    };
}

function sendResponse(id, status, result, error = null) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const response = { id, status, result, error };
        socket.send(JSON.stringify(response));
    }
}

async function handleCommand(cmd) {
    switch (cmd.action) {
        case "EXECUTE_SCRIPT":
            return await executeScript(cmd.payload);
        case "NAVIGATE":
            return await navigate(cmd.payload);
        case "GET_DOM":
            return await getDOM(cmd.payload);
        case "PING":
            return "PONG";
        default:
            throw new Error(\`Unknown action: \${cmd.action}\`);
    }
}

async function navigate(payload) {
    const url = payload.url;
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
        await chrome.tabs.update(tab.id, { url: url });
        return { tabId: tab.id, url: url };
    } else {
         const newTab = await chrome.tabs.create({ url: url });
         return { tabId: newTab.id, url: url };
    }
}

async function executeScript(payload) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error("No active tab");

    const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (code) => {
             try {
                 const result = new Function(code)();
                 return result;
             } catch (e) {
                 return "Error: " + e.message;
             }
        },
        args: [payload.code]
    });

    return result[0].result;
}

async function getDOM(payload) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error("No active tab");

    const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
             function serialize(node) {
                 if (node.nodeType === 1) {
                     const obj = {
                         tag: node.tagName.toLowerCase(),
                         attrs: {},
                         children: []
                     };
                     for (let i = 0; i < node.attributes.length; i++) {
                         const attr = node.attributes[i];
                         obj.attrs[attr.name] = attr.value;
                     }
                     for (let child of node.childNodes) {
                         const childObj = serialize(child);
                         if (childObj) obj.children.push(childObj);
                     }
                     return obj;
                 }
                 else if (node.nodeType === 3) {
                     const text = node.textContent.trim();
                     if (text) return text;
                 }
                 return null;
             }
             return serialize(document.body);
         }
    });

    return result[0].result;
}

// Start connection
connect();
EOF

# 7.3 Wrap Chrome Binary to Force Flags
CHROME_BIN="/usr/bin/google-chrome"
CHROME_REAL="/usr/bin/google-chrome.real"

# Ensure diversion exists (idempotent)
if [ ! -f "$CHROME_REAL" ]; then
    dpkg-divert --add --rename --divert "$CHROME_REAL" "$CHROME_BIN"
fi

# Write Wrapper
cat > "$CHROME_BIN" <<EOF
#!/bin/bash
exec "$CHROME_REAL" \\
    --no-sandbox \\
    --no-zygote \\
    --disable-gpu \\
    --disable-dev-shm-usage \\
    --remote-debugging-port=9222 \\
    --load-extension="$BRIDGE_DIR" \\
    "\$@"
EOF
chmod +x "$CHROME_BIN"

# --- 8. CLEANUP & FINISH ---


echo "✅ UphillSnowball GUI Installed."
echo "👉 Remote Desktop requires manual authentication. Run 'setup_workstation.sh' inside the workstation to link it."
# DISPLAY= /opt/google/chrome-remote-desktop/start-host --code="STALE_CODE" --redirect-url="https://remotedesktop.google.com/_/oauthredirect" --name=$(hostname)
