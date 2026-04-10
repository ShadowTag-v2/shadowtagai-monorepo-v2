#!/usr/bin/env bash
set -euo pipefail

# Default to 'code' if no argument, but allow 'cursor'
CLI=${1:-code}

echo "📦 Installing ShadowTag-v4 Stack v5 Extensions via $CLI..."

exts=(
  "dbaeumer.vscode-eslint"           # Linting
  "esbenp.prettier-vscode"           # Formatting
  "rust-lang.rust-analyzer"          # Rust Core
  "ms-python.python"                 # Python Core
  "streetsidesoftware.code-spell-checker"
  "usernamehw.errorlens"             # Instant Feedback
  "GitHub.vscode-pull-request-github"# GitHub Sync
  "eamodio.gitlens"                  # Blame/History
  "ms-azuretools.vscode-docker"      # Container Ops
  "rangav.vscode-thunder-client"     # API Testing
  "tamasfe.even-better-toml"         # Config Support
  "formulahendry.code-runner"        # Quick execution
  "naumovs.color-highlight"          # UI QoL
)

for e in "${exts[@]}"; do
  echo "➡️  Installing $e..."
  "$CLI" --install-extension "$e" || echo "⚠️  Failed to install $e"
done

echo "✅ Cognitive Environment Ready."
