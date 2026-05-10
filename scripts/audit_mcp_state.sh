#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "${ROOT}"

echo "== MCP Stack Audit =="
echo

echo "== 1. Config files =="
for f in "docs/mcp-stack.md" "antigravity-mcp-config.json"; do
  if [ -f "$f" ]; then
    echo "present: $f"
  else
    echo "missing: $f"
  fi
done
echo

echo "== 2. Node / npm / Chrome =="
if command -v node >/dev/null 2>&1; then
  echo "node: $(node -v)"
else
  echo "node: MISSING"
fi

if command -v npm >/dev/null 2>&1; then
  echo "npm: $(npm -v)"
else
  echo "npm: MISSING"
fi

if [ -d "/Applications/Google Chrome.app" ]; then
  echo "chrome: present"
else
  echo "chrome: MISSING"
fi
echo

echo "== 3. MCP config enabled flags =="
if [ -f antigravity-mcp-config.json ]; then
  grep -n '"enabled"' antigravity-mcp-config.json || true
else
  echo "antigravity-mcp-config.json missing"
fi
echo

echo "== 4. Chrome remote debug port =="
if command -v curl >/dev/null 2>&1; then
  if curl -s http://127.0.0.1:9222/json/version >/dev/null 2>&1; then
    echo "chrome remote debug: reachable on 9222"
    curl -s http://127.0.0.1:9222/json/version | head -c 300; echo
  else
    echo "chrome remote debug: NOT reachable on 9222"
  fi
else
  echo "curl missing"
fi
echo

echo "== 5. chrome-devtools-mcp resolution =="
if command -v npx >/dev/null 2>&1; then
  if npx -y chrome-devtools-mcp@latest --help >/dev/null 2>&1; then
    echo "chrome-devtools-mcp: resolves"
  else
    echo "chrome-devtools-mcp: FAILED to resolve"
  fi
else
  echo "npx missing"
fi
echo

echo "== 6. Developer Knowledge token presence =="
if [ -n "${GOOGLE_OAUTH_ACCESS_TOKEN:-}" ]; then
  echo "GOOGLE_OAUTH_ACCESS_TOKEN: present in environment"
else
  echo "GOOGLE_OAUTH_ACCESS_TOKEN: NOT present"
fi
echo

echo "== 7. Known timeout-prone MCPs =="
for name in firebase-mcp-server mcp-toolbox-for-databases sequential-thinking; do
  echo "expected default state: disabled -> $name"
done
echo

echo "== 8. Recommended action =="
echo "Keep only chrome-devtools and google-developer-knowledge enabled by default until the timeout-prone MCPs are validated standalone."
