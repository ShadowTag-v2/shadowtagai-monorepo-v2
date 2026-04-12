#!/bin/bash
# VS Code Fleet Launcher - 5 optimized instances for AI Development Factory
set -e

BASE_DIR="$HOME/ShadowTag-v2-fastapi-services"
VSCODE_BASE="$HOME/.vscode-fleet"

# Find VS Code binary
if command -v code &> /dev/null; then
    CODE_CMD="code"
elif [ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]; then
    CODE_CMD="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
elif [ -x "/usr/local/bin/code" ]; then
    CODE_CMD="/usr/local/bin/code"
else
    echo "ERROR: VS Code not found. Install VS Code or add 'code' to PATH"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  VS CODE FLEET LAUNCHER - AI Development Factory             ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Create isolated VS Code data directories
mkdir -p "$VSCODE_BASE/python/extensions"
mkdir -p "$VSCODE_BASE/k8s/extensions"
mkdir -p "$VSCODE_BASE/frontend/extensions"
mkdir -p "$VSCODE_BASE/data/extensions"
mkdir -p "$VSCODE_BASE/test/extensions"

echo ">>> Launching VS Code Fleet (5 instances)"

# Instance 1: Python/FastAPI (Judge#6, ATP_519_scan)
echo "  [1/5] Python/FastAPI instance..."
"$CODE_CMD" "$BASE_DIR/pnkln/" \
  --user-data-dir "$VSCODE_BASE/python" \
  --extensions-dir "$VSCODE_BASE/python/extensions" &

# Instance 2: K8s/DevOps (GKE deployment)
echo "  [2/5] K8s/DevOps instance..."
"$CODE_CMD" "$BASE_DIR/k8s/" \
  --user-data-dir "$VSCODE_BASE/k8s" \
  --extensions-dir "$VSCODE_BASE/k8s/extensions" &

# Instance 3: Frontend (React dashboards)
echo "  [3/5] Frontend instance..."
"$CODE_CMD" "$BASE_DIR/public/" \
  --user-data-dir "$VSCODE_BASE/frontend" \
  --extensions-dir "$VSCODE_BASE/frontend/extensions" &

# Instance 4: Data/Analytics (BigQuery, SQL)
echo "  [4/5] Data/Analytics instance..."
"$CODE_CMD" "$BASE_DIR/analytics/" \
  --user-data-dir "$VSCODE_BASE/data" \
  --extensions-dir "$VSCODE_BASE/data/extensions" &

# Instance 5: Testing (pytest, integration)
echo "  [5/5] Testing instance..."
"$CODE_CMD" "$BASE_DIR/tests/" \
  --user-data-dir "$VSCODE_BASE/test" \
  --extensions-dir "$VSCODE_BASE/test/extensions" &

sleep 2

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  FLEET LAUNCHED                                              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Instance 1: Python/FastAPI  → pnkln/                        ║"
echo "║  Instance 2: K8s/DevOps      → k8s/                          ║"
echo "║  Instance 3: Frontend        → public/                       ║"
echo "║  Instance 4: Data/Analytics  → analytics/                    ║"
echo "║  Instance 5: Testing         → tests/                        ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Each instance has independent Gemini Code Assist license    ║"
echo "║  n-autoresearch/Kosmos/BioAgents API: http://localhost:8600                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
