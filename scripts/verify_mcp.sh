#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
CONFIG="$ROOT/antigravity-mcp-config.json"
SECRETS_LOADER="$ROOT/scripts/load_mcp_secrets.sh"
TOOLS_FILE="$ROOT/database_tools.yaml"

echo "[verify_mcp] root: $ROOT"

[[ -f "$CONFIG" ]] || { echo "[verify_mcp] missing $CONFIG"; exit 1; }
# NOTE: .env is BANNED per secrets_manager_doctrine (2026-04-22).
# Secrets are loaded via load_mcp_secrets.sh or GCP Secret Manager.
if [[ -f "$SECRETS_LOADER" ]]; then
  echo "[verify_mcp] loading secrets via load_mcp_secrets.sh"
  set -a
  source "$SECRETS_LOADER"
  set +a
else
  echo "[verify_mcp] WARN: load_mcp_secrets.sh not found; relying on env injection"
fi
[[ -f "$TOOLS_FILE" ]] || { echo "[verify_mcp] WARN: $TOOLS_FILE missing (non-fatal)"; }

required_vars=(
  STITCH_API_KEY
  DEVELOPER_KNOWLEDGE_API_KEY
  GEMINI_API_KEY
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "[verify_mcp] missing env var: $var"
    exit 1
  fi
done

echo "[verify_mcp] validating canonical JSON"
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json")
json.loads(p.read_text())
print("[verify_mcp] canonical json ok")
PY

echo "[verify_mcp] validating YAML"
python3 - <<'PY'
import pathlib, sys
try:
    import yaml
except Exception:
    print("[verify_mcp] pyyaml missing; install with: python3 -m pip install pyyaml")
    sys.exit(1)

p = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/database_tools.yaml")
yaml.safe_load(p.read_text())
print("[verify_mcp] yaml ok")
PY

echo "[verify_mcp] checking canonical server entries"
# Verify all 5 canonical MCP servers are present
for server in "sequential-thinking" "firebase-mcp-server" "google-developer-knowledge" "StitchMCP" "chrome-devtools-mcp"; do
  grep -q "\"$server\"" "$CONFIG" || { echo "[verify_mcp] missing server: $server"; exit 1; }
done
echo "[verify_mcp] all 5 canonical servers present"

echo "[verify_mcp] optional adapter presence only"
test -f "/Users/pikeymickey/.gemini/antigravity/mcp_config.json" && echo "[verify_mcp] retired adapter present"
test -f "$ROOT/.vscode/cline_mcp_settings.json" && echo "[verify_mcp] vscode adapter present"

echo "[verify_mcp] done"
