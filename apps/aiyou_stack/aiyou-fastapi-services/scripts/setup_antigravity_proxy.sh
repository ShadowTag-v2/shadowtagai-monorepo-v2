#!/usr/bin/env bash
# ------------------------------------------------------------
# Antigravity Proxy Setup
# ------------------------------------------------------------
# This script installs and configures the Antigravity Proxy
# (https://github.com/elad12390/antigravity-proxy) which intercepts
# Antigravity IDE API calls and replaces the Google Gemini API key
# with your own token.

set -euo pipefail

# 1. Install dependencies (macOS – Homebrew)
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found – please install Homebrew first."
  exit 1
fi

# Python 3.8+ and pip
python3 -m pip install --upgrade pip
python3 -m pip install python-dotenv

# 2. Clone the proxy repository (if not already present)
PROXY_DIR="$HOME/antigravity-proxy"
if [ ! -d "$PROXY_DIR" ]; then
  git clone https://github.com/elad12390/antigravity-proxy "$PROXY_DIR"
fi
cd "$PROXY_DIR"

# 3. Install the Python addon dependencies
python3 -m pip install -r requirements.txt || true

# The certificate is now at ~/.mitmproxy/mitmproxy-ca-cert.pem
# On macOS,echo "run_sharded_proxy: proxy start skipped (mitmproxy removed)."  In Keychain Access → Trust → Always Trust

# 5. Configure your Gemini API key
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your-key
# (You can also export it directly before running the proxy)

# 6. Start the proxy (background)
echo "Antigravity Proxy setup skipped (mitmproxy removed)."

# 7. Launch Antigravity IDE using the proxy
# Adjust the path if Antigravity.app is installed elsewhere.
export HTTP_PROXY="http://localhost:8080"
export HTTPS_PROXY="http://localhost:8080"
open "/Applications/Antigravity.app/Contents/MacOS/Antigravity"

# 8. When you are done, stop the proxy
# kill $PROXY_PID

echo "Setup complete (mitmproxy removed)."
