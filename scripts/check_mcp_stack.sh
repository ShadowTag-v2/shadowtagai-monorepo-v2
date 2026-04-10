#!/usr/bin/env bash
set -euo pipefail

fail() {
echo "ERROR: $1" >&2
exit 1
}

echo "[1/6] Checking Node..."
command -v node >/dev/null 2>&1 || fail "node not found"
NODE_VER="$(node -v)"
echo "Node: ${NODE_VER}"

echo "[2/6] Checking npm..."
command -v npm >/dev/null 2>&1 || fail "npm not found"
echo "npm: $(npm -v)"

echo "[3/6] Checking Chrome install..."
if [ -d "/Applications/Google Chrome.app" ]; then
echo "Chrome present"
else
fail "Google Chrome.app not found in /Applications"
fi

echo "[4/6] Checking Chrome DevTools MCP package resolution..."
npx -y chrome-devtools-mcp@latest --help >/dev/null 2>&1 || fail "chrome-devtools-mcp package did not resolve"
echo "chrome-devtools-mcp resolves"

echo "[5/6] Checking workspace root..."
ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
[ -d "${ROOT}" ] || fail "canonical monorepo root missing"
echo "Workspace root present: ${ROOT}"

echo "[6/6] Checking docs and config artifacts..."
[ -f "${ROOT}/docs/mcp-stack.md" ] || fail "docs/mcp-stack.md missing"
[ -f "${ROOT}/antigravity-mcp-config.json" ] || fail "antigravity-mcp-config.json missing"
echo "Artifacts present"

echo
echo "MCP prerequisite check passed."
echo "Next manual steps:"
echo "  1. Start Chrome with remote debugging on port 9222"
echo "  2. Export GOOGLE_OAUTH_ACCESS_TOKEN if using google-developer-knowledge"
echo "  3. Keep firebase-mcp-server, mcp-toolbox-for-databases, and sequential-thinking disabled until individually validated"
