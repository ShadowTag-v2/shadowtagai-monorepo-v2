#!/bin/bash
set -e

echo "🚀 Launching ShadowTag v2.0 (Phase 4 Integration)..."
echo "===================================================="
echo "Initializing Cryptographic Watermarking Engine..."

# Ensure dependencies
if ! python3 -c "import Crypto" &> /dev/null; then
    echo "Installing crypto dependencies..."
    pip install pycryptodome > /dev/null
fi

# Run the tools
echo "Running ShadowTag Tools..."
if [ -f "pnkln/tools/shadowtag_tools.py" ]; then
    python3 pnkln/tools/shadowtag_tools.py
else
    echo "Error: shadowtag_tools.py not found in pnkln/tools/"
    exit 1
fi

echo "===================================================="
echo "✅ ShadowTag Launch Complete."
echo "Audit trail available in local logs."
