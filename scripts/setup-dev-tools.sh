#!/bin/bash
# PNKLN Dev Tools Setup - One-command installer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TOOLS_DIR="$PROJECT_ROOT/tools/dev-environment"

echo "///▞ PNKLN DEV TOOLS SETUP"
echo "═══════════════════════════════════════════════════════════════"
echo "This will set up:"
echo "  1. Antigravity Proxy ($0 Gemini API via your key)"
echo "  2. CACI (Claude Code AI Configuration)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check prerequisites
echo "[1/6] Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "ERROR: git not found. Install git first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Install Python 3 first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "WARNING: npm not found. CACI requires Node.js/npm."
fi

if ! command -v mitmproxy &> /dev/null; then
    echo "WARNING: mitmproxy not found. Installing..."
    pip3 install mitmproxy || echo "  (manual install: pip3 install mitmproxy)"
fi

echo "  Prerequisites OK"

# Initialize submodules
echo "[2/6] Initializing git submodules..."
cd "$PROJECT_ROOT"
git submodule update --init --recursive
echo "  Submodules initialized"

# Create .env templates
echo "[3/6] Creating .env templates..."

if [ ! -f "$TOOLS_DIR/antigravity-proxy/.env" ]; then
    cat > "$TOOLS_DIR/antigravity-proxy/.env" << 'EOF'
# Antigravity Proxy Configuration
# Your Gemini API key (from Google AI Studio or Vertex AI)
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Specific model to use
GEMINI_MODEL=gemini-2.0-flash-exp
EOF
    echo "  Created antigravity-proxy/.env (edit with your API key)"
fi

if [ ! -f "$TOOLS_DIR/claude-code-config/.env" ]; then
    cat > "$TOOLS_DIR/claude-code-config/.env" << 'EOF'
# CACI Configuration
# Google API key for Gemini 2.5 Pro (used for component recommendations)
GOOGLE_API_KEY=your-google-api-key-here
EOF
    echo "  Created claude-code-config/.env (edit with your API key)"
fi

# Make scripts executable
echo "[4/6] Setting permissions..."
chmod +x "$TOOLS_DIR/antigravity-proxy/pnkln/"*.sh 2>/dev/null || true
chmod +x "$TOOLS_DIR/claude-code-config/pnkln/"*.sh 2>/dev/null || true
echo "  Scripts made executable"

# Install CACI dependencies
echo "[5/6] Installing CACI..."
if command -v npm &> /dev/null; then
    cd "$TOOLS_DIR/claude-code-config"
    if [ -f "package.json" ]; then
        npm install 2>/dev/null || echo "  (npm install skipped)"
    fi
fi
echo "  CACI ready"

# Summary
echo "[6/6] Setup complete!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "NEXT STEPS:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Edit API keys in .env files:"
echo "   $TOOLS_DIR/antigravity-proxy/.env"
echo "   $TOOLS_DIR/claude-code-config/.env"
echo ""
echo "2. Enable Antigravity Proxy (optional):"
echo "   cd $TOOLS_DIR/antigravity-proxy/pnkln"
echo "   ./enable.sh"
echo ""
echo "3. Run CACI to configure Claude Code:"
echo "   cd $TOOLS_DIR/claude-code-config"
echo "   npx caci"
echo ""
echo "4. Use PNKLN components:"
echo "   npx caci --components ./pnkln/pnkln-components.json"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Security: Antigravity Proxy intercepts HTTPS - DEV ONLY!"
echo "Run ./disable.sh when done with proxy."
echo "═══════════════════════════════════════════════════════════════"
