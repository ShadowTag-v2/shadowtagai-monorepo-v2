#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
mkdir -p "$ROOT/.github/workflows" "$ROOT/.vscode" "$ROOT/docs" "$ROOT/scripts"
cd "$ROOT"

cat > docs/mcp-stack.md <<'EOF'
# MCP Stack

## Stable-first policy
Start with only the MCP servers that are grounded and validated.

### Enabled first
- chrome-devtools
- google-developer-knowledge

### Disabled until validated
- firebase-mcp-server
- mcp-toolbox-for-databases
- sequential-thinking

## Chrome DevTools MCP
Requirements:
- Node.js v20.19 or newer
- current stable Chrome
- npm

Antigravity config:
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222",
        "-y",
        "--no-usage-statistics"
      ]
    }
  }
}
```
Notes:
* Browser must already be running.
* If Antigravity uses built-in browser, open it first.
* If port is not 9222, adjust browser-url.

## Developer Knowledge MCP
Use environment-based auth only. Do not hardcode API keys into repo files. Prefer secret injection or user-local config.

Suggested shape:
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

## Timeouting MCPs
If a server returns context deadline exceeded:
1. disable it by default
2. validate its command standalone in terminal
3. add startup timeout if client supports it
4. only re-enable after health check passes
EOF

cat > scripts/check_mcp_stack.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "[1/4] Checking Node..."
node -v || { echo "Node missing"; exit 1; }
echo "[2/4] Checking npm..."
npm -v || { echo "npm missing"; exit 1; }
echo "[3/4] Checking Chrome..."
if [ -d "/Applications/Google Chrome.app" ]; then
echo "Chrome present"
else
echo "Chrome missing"
exit 1
fi
echo "[4/4] Checking Chrome DevTools MCP package resolution..."
npx -y chrome-devtools-mcp@latest --help >/dev/null && echo "chrome-devtools-mcp resolvable"
echo "MCP prerequisites look good."
EOF
chmod +x scripts/check_mcp_stack.sh

cat > .antigravity-system-prompt.txt <<'EOF'
ANTIGRAVITY WORKSPACE CONTAINMENT + MONOREPO DISCIPLINE
Canonical workspace root:
/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
Operate only within the canonical monorepo root.
Treat only canonical live paths as authoritative.
Fail closed on ambiguity, workspace drift, nested repo drift, or path escape.
MCP policy:
* Enable only validated MCP servers by default.
* Stable-first MCP order:
    1. chrome-devtools
    2. google-developer-knowledge
* Keep firebase-mcp-server, mcp-toolbox-for-databases, and sequential-thinking disabled until individually validated.
* Never trust timeouting MCP servers in production until they pass health checks.
Canonical namespace:
* apps/pnkln-stack_stack
Denied zones:
* archive/
* tools/legacy/
* docs/legacy_shadowtag_v2/
* apps/pnkln-stack_ecosystem/raw_ingest/
* **/_PRE_OMEGA_BACKUP_*/
* **/repos/*-legacy/
* **/ShadowTag-Omega/
* **/arsenal_recovered/
Use monorepo_manifest.yaml as law.
Never create a second source of truth.
EOF

cat > docs/monorepo-10x-command.txt <<'EOF'
/monorepo-10x
Use monorepo_manifest.yaml as the canonical source of truth.
Resolve every shared repo to canonical or archived.
Do not leave repos unresolved.
Do not modify denied zones except for archival or migration work.
Require bazel-build and bazel-test on main.
Require CODEOWNERS review on main.
Prefer canonicalization over ingestion.
Prefer archive-then-delete over indefinite coexistence.
EOF

cat > docs/monorepo-10x-checklist.md <<'EOF'
# Monorepo 10/10 Checklist
* Every shared repo is canonical or archived
* No unresolved repos remain in monorepo_manifest.yaml
* CODEOWNERS is active
* main requires bazel-build
* main requires bazel-test
* No backup/recovered/legacy/raw-ingest trees remain in live code paths
* Shared contract root exists
* third_party policy exists
* Workspace drift guard is active
* MCP stack is stable-first and validated
EOF

cat > docs/monorepo-weekly-scorecard.md <<'EOF'
# Monorepo Weekly Scorecard
## Week of
YYYY-MM-DD
## Overall score
* Current week score: __/100
* Last week score: __/100
* Delta: +/-__
## Examples to audit this week
* Example canonical repo:
* Example unresolved repo:
* Example denied-zone cleanup:
* Example green bazel-build:
* Example green bazel-test:
* Example MCP fixed:
* Example MCP still timing out:
## Categories
| Category | Weight | Score | Notes |
|----------|-------:|------:|-------|
| Canonical repo resolution | 20 | | |
| Live tree cleanliness | 20 | | |
| GitHub governance | 15 | | |
| Bazel / CI reliability | 15 | | |
| third_party discipline | 10 | | |
| Shared contracts | 10 | | |
| Workspace / tooling stability | 5 | | |
| MCP stack stability | 5 | | |

## Executive summary
* What improved:
* What regressed:
* Biggest blocker:
* Next-week priority:
EOF

echo
echo "Wrote bootstrap docs and MCP scaffold into $ROOT"
echo "Next:"
echo " ./scripts/check_mcp_stack.sh"
echo " open docs/mcp-stack.md"
