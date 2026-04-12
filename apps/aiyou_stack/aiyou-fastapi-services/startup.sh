#!/usr/bin/env bash
# startup.sh - The "Permanent" ShadowTag Boot Protocol
# Includes "Microsoft Jailbreak" and Auto-Extension Recovery

set -euo pipefail

echo ">>> 🛠️  SHADOWTAG BOOT PROTOCOL: INITIATED..."

# --- 1. THE "MICROSOFT JAILBREAK" (Persist Marketplace) ---
# We patch product.json every boot so you can access Pylance/HexEditor
PRODUCT_JSON="/usr/lib/code-server/lib/vscode/product.json" 
# Note: Path may vary slightly by image version; we try standard paths.
if [ ! -f "$PRODUCT_JSON" ]; then
    # Fallback for different base images
    PRODUCT_JSON=$(find /usr/lib -name product.json | grep "code-server" | head -n 1 || true)
fi

if [[ -n "$PRODUCT_JSON" ]] && [[ -f "$PRODUCT_JSON" ]]; then
    echo ">>> 🔓 Unlocking Microsoft Marketplace in $PRODUCT_JSON..."
    # Backup original
    cp -n "$PRODUCT_JSON" "$PRODUCT_JSON.bak"
    
    # Inject Microsoft Gallery URL
    sed -i 's/"serviceUrl": "https:\/\/open-vsx.org\/vscode\/gallery"/"serviceUrl": "https:\/\/marketplace.visualstudio.com\/_apis\/public\/gallery"/g' "$PRODUCT_JSON"
    sed -i 's/"itemUrl": "https:\/\/open-vsx.org\/vscode\/item"/"itemUrl": "https:\/\/marketplace.visualstudio.com\/items"/g' "$PRODUCT_JSON"
    # Clear cache to force reload
    rm -rf /home/user/.local/share/code-server/CachedExtensionVSIXs
else
    echo ">>> ⚠️ Could not find product.json. Marketplace patch skipped."
fi

# --- 2. MOUNT FILESTORE (The "Shared Drive") ---
mkdir -p /mnt/agent_share
echo "Mounting Filestore from ${FILESTORE_IP:-}..."

if [[ -n "${FILESTORE_IP:-}" ]]; then
    apt-get update && apt-get install -y nfs-common || true
    mount -o nolock "${FILESTORE_IP}:/${FILE_SHARE_NAME:-shadow_share}" /mnt/agent_share || echo "WARNING: Mount failed (Is Filestore Ready?)"
else
    echo "WARNING: FILESTORE_IP is not set. Skipping mount."
fi

# --- 3. INSTALL DEPENDENCIES (The "Environment") ---
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
        libgbm1 libasound2 libnss3-dev libgdk-pixbuf2.0-dev libgtk-3-dev libxss-dev \
        socat

    # Symlink Brave to Google Chrome for compatibility
    ln -sf /usr/bin/brave-browser /usr/bin/google-chrome
fi

# --- 4. DEPLOY AGENT CODE (The "Brain") ---
WORK_DIR="/home/user/agent-platform"
if [ ! -d "$WORK_DIR" ]; then
    REPO_URL="${AGENT_REPO_URL:-https://github.com/ehanc69/ShadowTag-v2-fastapi-services.git}"
    git clone "$REPO_URL" "$WORK_DIR"
else
    cd "$WORK_DIR" && git pull || true
fi

cd "$WORK_DIR"
# Install project deps
pip3 install -r requirements.txt || true
cd jetski-bridge && npm install || true

# --- 5. START THE BRIDGE & WORKER (The "Process") ---
# Kill old processes if restarting
pkill -f "uvicorn.*bridge_server" || true

# Start Xvfb (Virtual Display)
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Start Jetski Bridge
export PYTHONPATH="$WORK_DIR"
nohup python3 -m uvicorn libs.arsenal.jetski.bridge_server:app --host 0.0.0.0 --port 3025 > bridge.log 2>&1 &

# Port Forwarding (80 -> 3025) for Cloud Workstation Gateway
nohup socat TCP-LISTEN:80,fork TCP:127.0.0.1:3025 > socat.log 2>&1 &

# --- 6. INSTALL VS CODE EXTENSIONS (The Fix) ---
echo ">>> 🧩 Restoring Extensions..."
# Function to install as user
install_ext() {
    # We must run as 'user' because code-server runs as user
    if id "user" &>/dev/null; then
        su - user -c "code-server --install-extension $1 --force"
    else
        # Fallback if running as root in weird env
        code-server --install-extension $1 --force
    fi
}

# The "Must Haves" list
install_ext ms-python.python         # Pylance (Requires Jailbreak)
install_ext charliermarsh.ruff       # The Linter
install_ext ms-vscode.hexeditor      # Binary File Fix
install_ext golang.go                # Backend
install_ext redhat.vscode-yaml       # Terraform/YAML
install_ext googlecloudtools.cloudcode # Gemini Code Assist
install_ext vscjava.vscode-java-pack # Java

# --- 7. UPHILLSNOWBALL COCKPIT (CRD) ---
# ... (Leaving existing CRD setup logic if needed, but it's largely manual)

echo ">>> ✅ SHADOWTAG WORKSTATION READY."
