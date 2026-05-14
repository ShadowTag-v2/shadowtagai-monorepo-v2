#!/usr/bin/env bash
# apps/gitnexus/setup.sh
# One-time setup for GitNexus codebase knowledge graph on Monorepo-Uphillsnowball.
# After setup, the MCP server is available at: npx nexus mcp
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "[gitnexus] Installing dependencies..."
cd "$SCRIPT_DIR"
npm install

echo "[gitnexus] Indexing monorepo (tree-sitter AST analysis)..."
npx nexus analyze "$REPO_ROOT" \
  --output "$SCRIPT_DIR/.nexus" \
  --langs ts,tsx,py,js \
  --exclude "node_modules,data/drive_ingest,data/web_ingest,data/alphaxiv,artifacts/workspace_archive"

echo "[gitnexus] Registering repository in nexus registry..."
npx nexus setup "$REPO_ROOT" --output "$SCRIPT_DIR/.nexus"

echo "[gitnexus] Setup complete."
echo ""
echo "To start the MCP server:"
echo "  cd apps/gitnexus && npx nexus mcp"
echo ""
echo "To add to Claude Code, add to .mcp.json:"
echo '  "gitnexus": { "type": "stdio", "command": "npx", "args": ["nexus", "mcp"] }'
