#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
CONFIG="$ROOT/antigravity-mcp-config.json"
ENV_FILE="$ROOT/.env"
TOOLS_FILE="$ROOT/database_tools.yaml"

echo "[verify_mcp] root: $ROOT"

[[ -f "$CONFIG" ]] || { echo "[verify_mcp] missing $CONFIG"; exit 1; }
[[ -f "$ENV_FILE" ]] || { echo "[verify_mcp] missing $ENV_FILE"; exit 1; }
[[ -f "$TOOLS_FILE" ]] || { echo "[verify_mcp] missing $TOOLS_FILE"; exit 1; }

echo "[verify_mcp] loading env"
set -a
source "$ENV_FILE"
set +a

required_vars=(
  STITCH_API_KEY
  DEVELOPER_KNOWLEDGE_API_KEY
  API_KEY
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

echo "[verify_mcp] checking canonical stream command"
grep -q 'gemini-3.1-flash-lite-preview:streamGenerateContent' "$CONFIG"

echo "[verify_mcp] checking lancedb command"
grep -q 'pnkln-lancedb-smoke-test' "$CONFIG"

echo "[verify_mcp] optional adapter presence only"
test -f "/Users/pikeymickey/.gemini/antigravity/mcp_config.json" && echo "[verify_mcp] retired adapter present"
test -f "$ROOT/.vscode/cline_mcp_settings.json" && echo "[verify_mcp] vscode adapter present"

echo "[verify_mcp] done"
