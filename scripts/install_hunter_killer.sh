#!/bin/bash
# HUNTER-KILLER STACK INSTALLER
# Usage: ./scripts/install_hunter_killer.sh
# Installs: rg (ripgrep), ugrep, sg (ast-grep)

set -euo pipefail

echo "=== INSTALLING HUNTER-KILLER STACK ==="
echo "The Hunter (rg) | The Universal (ugrep) | The Killer (sg)"
echo ""

# Check for Homebrew
if ! command -v brew &>/dev/null; then
    echo "❌ Homebrew not found. Install: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# The Hunter: ripgrep
echo "[1/3] Installing ripgrep (The Hunter)..."
if command -v rg &>/dev/null; then
    echo "  ✅ ripgrep already installed: $(rg --version | head -1)"
else
    brew install ripgrep
    echo "  ✅ ripgrep installed: $(rg --version | head -1)"
fi

# The Universal: ugrep
echo "[2/3] Installing ugrep (The Universal)..."
if command -v ugrep &>/dev/null; then
    echo "  ✅ ugrep already installed: $(ugrep --version | head -1)"
else
    brew install ugrep
    echo "  ✅ ugrep installed: $(ugrep --version | head -1)"
fi

# The Killer: ast-grep
echo "[3/3] Installing ast-grep (The Killer)..."
if command -v sg &>/dev/null; then
    echo "  ✅ ast-grep already installed: $(sg --version 2>/dev/null || echo 'version unknown')"
else
    brew install ast-grep
    echo "  ✅ ast-grep installed: $(sg --version 2>/dev/null || echo 'version unknown')"
fi

echo ""
echo "=== HUNTER-KILLER STACK VERIFICATION ==="
echo "  rg: $(command -v rg 2>/dev/null && echo '✅' || echo '❌')"
echo "  ugrep: $(command -v ugrep 2>/dev/null && echo '✅' || echo '❌')"
echo "  sg: $(command -v sg 2>/dev/null && echo '✅' || echo '❌')"
echo ""
echo "=== INSTALLATION COMPLETE ==="
