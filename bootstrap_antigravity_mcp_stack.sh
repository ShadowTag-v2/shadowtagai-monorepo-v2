#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

mkdir -p "${ROOT}/docs" "${ROOT}/scripts"
cd "${ROOT}"

cat > docs/mcp-stack.md <<'EOF'
# MCP Stack

## Purpose
This document defines the stable-first MCP policy for Antigravity in `Monorepo-Uphillsnowball`.

## Canonical workspace root
`/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball`

## Stable-first policy
Only enable MCP servers by default if they are:
1. grounded in real config/docs
2. validated locally
3. not timing out during startup

### Enabled first
- `chrome-devtools`
- `google-developer-knowledge`

### Disabled until validated
- `firebase-mcp-server`
- `mcp-toolbox-for-databases`
- `sequential-thinking`

---

## Chrome DevTools MCP

### Requirements
- Node.js v20.19 or newer
- npm
- Current stable Google Chrome
- Chrome already running with remote debugging enabled

### Launch example
```bash
npx chrome-devtools-mcp@latest --browser-url=http://127.0.0.1:9222 -y --no-usage-statistics
```

### Notes

* The browser must already be running.
* If port `9222` is not correct, adjust `--browser-url`.
* This is the first MCP to keep enabled by default.

---

## Google Developer Knowledge MCP

### Policy

* Do not hardcode API keys or bearer tokens in repo-tracked config.
* Use user-local secrets or environment variables.
* Prefer OAuth bearer injection at runtime.

### Example config

```json
{
  "mcpServers": {
    "google-developer-knowledge": {
      "serverUrl": "https://developerknowledge.googleapis.com/mcp",
      "headers": {
        "Authorization": "Bearer ${GOOGLE_OAUTH_ACCESS_TOKEN}"
      }
    }
  }
}
```

---

## Timeouting MCP servers

If an MCP returns `context deadline exceeded`:

1. disable it in default config
2. validate its launch command standalone in terminal
3. confirm it responds locally before re-enabling
4. document:

   * status
   * last validated date
   * launch command
   * auth method
   * known failure mode

### Current timeout list

* `firebase-mcp-server`
* `mcp-toolbox-for-databases`
* `sequential-thinking`

### Current default policy

Disabled until individually validated.

---

## Validation checklist

### chrome-devtools

* [ ] `node -v` is >= 20.19
* [ ] `npm -v` works
* [ ] Chrome is installed
* [ ] Chrome is running with remote debug port
* [ ] `npx chrome-devtools-mcp@latest --help` works
* [ ] Antigravity can list tools from this server

### google-developer-knowledge

* [ ] OAuth token available in environment
* [ ] MCP endpoint reachable
* [ ] Antigravity can list tools from this server

### firebase-mcp-server

* [ ] launch command known
* [ ] auth method known
* [ ] server starts locally
* [ ] Antigravity can list tools
* [ ] no timeout

### mcp-toolbox-for-databases

* [ ] launch command known
* [ ] auth method known
* [ ] server starts locally
* [ ] Antigravity can list tools
* [ ] no timeout

### sequential-thinking

* [ ] launch command known
* [ ] server starts locally
* [ ] Antigravity can list tools
* [ ] no timeout

---

## Operating rule

Do not expand the default MCP stack until the current enabled stack is stable and boring.
EOF

cat > scripts/check_mcp_stack.sh <<'EOF'
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
EOF
chmod +x scripts/check_mcp_stack.sh

cat > antigravity-mcp-config.json <<'EOF'
{
"cwd": "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball",
"mcpServers": {
"chrome-devtools": {
"command": "npx",
"args": [
"chrome-devtools-mcp@latest",
"--browser-url=http://127.0.0.1:9222",
"-y",
"--no-usage-statistics"
],
"enabled": true
},
"google-developer-knowledge": {
"serverUrl": "https://developerknowledge.googleapis.com/mcp",
"headers": {
"Authorization": "Bearer ${GOOGLE_OAUTH_ACCESS_TOKEN}"
},
"enabled": true
},
"firebase-mcp-server": {
  "enabled": false,
  "notes": "Disabled by default due to timeout: context deadline exceeded. Validate standalone before enabling."
},
"mcp-toolbox-for-databases": {
  "enabled": false,
  "notes": "Disabled by default due to timeout: context deadline exceeded. Validate standalone before enabling."
},
"sequential-thinking": {
  "enabled": false,
  "notes": "Disabled by default due to timeout: context deadline exceeded. Validate standalone before enabling."
}
}
}
EOF

echo
echo "Wrote:"
echo "  ${ROOT}/docs/mcp-stack.md"
echo "  ${ROOT}/scripts/check_mcp_stack.sh"
echo "  ${ROOT}/antigravity-mcp-config.json"
echo
echo "Next:"
echo "  chmod +x ${ROOT}/scripts/check_mcp_stack.sh"
echo "  cd ${ROOT}"
echo "  ./scripts/check_mcp_stack.sh"
