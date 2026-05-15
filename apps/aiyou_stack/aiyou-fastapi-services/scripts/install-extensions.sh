#!/usr/bin/env bash
#
# install-extensions.sh
# Install all recommended VS Code/Cursor extensions for ShadowTag-v2 development
#
# Usage:
#   bash scripts/install-extensions.sh           # uses 'code' CLI
#   bash scripts/install-extensions.sh cursor    # uses 'cursor' CLI
#

set -euo pipefail

# Determine CLI to use (default: code, override with first arg)
CLI=${1:-code}

echo "📦 Installing VS Code/Cursor extensions using CLI: $CLI"
echo ""

# Core development extensions
exts=(
  # Linting & Formatting
  "dbaeumer.vscode-eslint"
  "esbenp.prettier-vscode"
  "ms-python.python"
  "ms-python.vscode-pylance"
  "charliermarsh.ruff"

  # Language support
  "rust-lang.rust-analyzer"
  "ms-vscode.vscode-typescript-next"
  "golang.go"
  "redhat.java"
  "ms-vscode.cpptools"

  # Code quality & assistance
  "streetsidesoftware.code-spell-checker"
  "usernamehw.errorlens"
  "VisualStudioExptTeam.vscodeintellicode"
  "GitHub.copilot"
  "GitHub.copilot-chat"

  # Git & GitHub
  "GitHub.vscode-pull-request-github"
  "eamodio.gitlens"
  "mhutchie.git-graph"

  # Docker & Kubernetes
  "ms-azuretools.vscode-docker"
  "ms-kubernetes-tools.vscode-kubernetes-tools"

  # File formats
  "redhat.vscode-yaml"
  "tamasfe.even-better-toml"
  "yzhang.markdown-all-in-one"
  "mechatroner.rainbow-csv"

  # API & Testing
  "rangav.vscode-thunder-client"
  "humao.rest-client"
  "hbenl.vscode-test-explorer"

  # Build tools
  "ms-vscode.makefile-tools"
  "ms-vscode.cmake-tools"

  # Utilities
  "formulahendry.code-runner"
  "naumovs.color-highlight"
  "christian-kohler.path-intellisense"
  "oderwat.indent-rainbow"
  "PKief.material-icon-theme"
  "zhuangtongfa.material-theme"

  # Database
  "mtxr.sqltools"
  "mongodb.mongodb-vscode"

  # Remote development
  "ms-vscode-remote.remote-ssh"
  "ms-vscode-remote.remote-containers"
  "ms-vscode-remote.remote-wsl"

  # Jupyter
  "ms-toolsai.jupyter"
  "ms-toolsai.jupyter-keymap"
  "ms-toolsai.vscode-jupyter-cell-tags"

  # AI/ML specific
  "ms-python.debugpy"
  "njpwerner.autodocstring"

  # Live share (collaboration)
  "ms-vsliveshare.vsliveshare"
)

echo "Installing ${#exts[@]} extensions..."
echo ""

installed=0
failed=0

for ext in "${exts[@]}"; do
  printf "Installing %-50s ... " "$ext"
  if "$CLI" --install-extension "$ext" --force > /dev/null 2>&1; then
    echo "✅"
    ((installed++))
  else
    echo "❌"
    ((failed++))
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Installation complete!"
echo "  ✅ Installed: $installed"
echo "  ❌ Failed:    $failed"
echo "  📦 Total:     ${#exts[@]}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$failed" -gt 0 ]; then
  echo "⚠️  Some extensions failed to install."
  echo "   This may be due to:"
  echo "   - Extension marketplace connectivity"
  echo "   - Extension already installed"
  echo "   - CLI version incompatibility"
  echo ""
  echo "   Try running manually with: $CLI --install-extension <extension-id>"
fi

echo ""
echo "🔄 Restart VS Code/Cursor to activate all extensions."
