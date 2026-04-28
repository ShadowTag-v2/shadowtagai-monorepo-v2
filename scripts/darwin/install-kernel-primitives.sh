#!/usr/bin/env bash
# ==============================================================================
# HUMAN HANDOFF: Install Darwin Kernel Primitives
# These require sudo — agent cannot execute autonomously.
# Run this script ONCE from your Mac Terminal.
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🛡️ Installing Antigravity Darwin Kernel Primitives..."

# 1. Sandbox Profile (Invariant #140)
echo "  [1/3] Installing read-only sandbox profile..."
sudo mkdir -p /etc/antigravity
sudo cp "$REPO_ROOT/scripts/darwin/readonly-probe.sb" /etc/antigravity/
sudo chown root:wheel /etc/antigravity/readonly-probe.sb
sudo chmod 444 /etc/antigravity/readonly-probe.sb

# 2. ag-probe wrapper (sandboxed executor)
echo "  [2/3] Installing ag-probe sandboxed executor..."
sudo bash -c 'cat << "WRAPPER" > /usr/local/bin/ag-probe
#!/bin/bash
# Executes the command inside the Darwin Read-Only Sandbox
sandbox-exec -f /etc/antigravity/readonly-probe.sb "$@"
WRAPPER'
sudo chmod +x /usr/local/bin/ag-probe
sudo chown root:wheel /usr/local/bin/ag-probe

# 3. STATE_B_CLUTCH location verification
echo "  [3/3] Verifying /etc/antigravity/ directory..."
if [ -d /etc/antigravity ]; then
    echo "    ✅ /etc/antigravity/ exists"
    ls -la /etc/antigravity/
else
    echo "    ❌ Failed to create /etc/antigravity/"
    exit 1
fi

echo ""
echo "✅ Darwin Kernel Primitives installed."
echo ""
echo "Usage:"
echo "  ag-probe python scripts/health_check.py   # Read-only sandboxed execution"
echo "  sudo touch /etc/antigravity/STATE_B_CLUTCH # Enable force-push temporarily"
echo "  sudo rm /etc/antigravity/STATE_B_CLUTCH    # Disengage force-push auth"
