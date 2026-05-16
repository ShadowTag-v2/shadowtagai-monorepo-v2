#!/usr/bin/env bash
# Sovereign State Protocol — Hunter-Killer Stack Installation
# The Hunter: rg (ripgrep) — blazing fast text search
# The Universal: ugrep — interactive + fuzzy matching
# The Killer: sg (ast-grep) — structural/AST search
set -euo pipefail

echo "=== HUNTER-KILLER STACK INSTALL ==="

# Detect package manager
if command -v brew &>/dev/null; then
  PKG="brew install"
else
  echo "ERROR: Homebrew not found. Install from https://brew.sh"
  exit 1
fi

# 1. ripgrep (rg)
if command -v rg &>/dev/null; then
  echo "[rg] Already installed: $(rg --version | head -1)"
else
  echo "[rg] Installing ripgrep..."
  $PKG ripgrep
fi

# 2. ugrep
if command -v ugrep &>/dev/null; then
  echo "[ugrep] Already installed: $(ugrep --version | head -1)"
else
  echo "[ugrep] Installing ugrep..."
  $PKG ugrep
fi

# 3. ast-grep (sg)
if command -v sg &>/dev/null; then
  echo "[sg] Already installed: $(sg --version)"
else
  echo "[sg] Installing ast-grep..."
  $PKG ast-grep
fi

echo ""
echo "=== HUNTER-KILLER STACK READY ==="
echo "  rg  → ripgrep (fast text search):        rg 'pattern' ."
echo "  ug  → ugrep (interactive/fuzzy):          ug -Q 'pattern'"
echo "  sg  → ast-grep (structural/AST search):   sg run -p 'console.log(\$X)'"
