#!/usr/bin/env bash
set -euo pipefail

DEST="${1:-external_support/public}"
mkdir -p "$DEST"
cd "$DEST"

clone_or_update() {
  local url="$1"
  local dir="$2"
  if [ -d "$dir/.git" ]; then
    echo "[update] $dir"
    git -C "$dir" pull --ff-only || true
  else
    echo "[clone] $dir"
    git clone "$url" "$dir"
  fi
}

clone_or_update https://github.com/google-gemini/gemini-cli.git gemini-cli
clone_or_update https://github.com/google/adk-python.git adk-python
clone_or_update https://github.com/google/adk-web.git adk-web
clone_or_update https://github.com/modelcontextprotocol/modelcontextprotocol.git mcp-spec
clone_or_update https://github.com/modelcontextprotocol/servers.git mcp-servers
clone_or_update https://github.com/modelcontextprotocol/python-sdk.git mcp-python-sdk
clone_or_update https://github.com/modelcontextprotocol/inspector.git mcp-inspector
clone_or_update https://github.com/ast-grep/ast-grep.git ast-grep
clone_or_update https://github.com/ast-grep/ast-grep-mcp.git ast-grep-mcp
clone_or_update https://github.com/microsoft/playwright.git playwright
# Optional GitLab support:
# git clone https://gitlab.com/fforster/gitlab-mcp.git gitlab-mcp

echo "[done] public support repos staged under $DEST"
