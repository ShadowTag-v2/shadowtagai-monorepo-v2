#!/usr/bin/env bash
set -euo pipefail

# Best-effort install of common Cursor/VS Code extensions
code() { command -v code >/dev/null 2>&1 && command code "$@" || true; }

extensions=(
  ms-vscode.vscode-typescript-next
  dbaeumer.vscode-eslint
  esbenp.prettier-vscode
  rust-lang.rust-analyzer
  tamasfe.even-better-toml
  ms-azuretools.vscode-docker
)

for ext in "${extensions[@]}"; do
  code --install-extension "$ext" || true
done

echo "Extensions install attempted."

