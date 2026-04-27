#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$ROOT/workspace-mcp-config.json"
TOOLS_FILE="$ROOT/database_tools.yaml"

echo "[verify_mcp] root: $ROOT"
[[ -f "$CONFIG" ]] || { echo "[verify_mcp] missing $CONFIG"; exit 1; }
[[ -f "$TOOLS_FILE" ]] || { echo "[verify_mcp] missing $TOOLS_FILE"; exit 1; }
python3 -c 'import json,sys; json.load(open(sys.argv[1])); print("[verify_mcp] canonical json ok")' "$CONFIG"
echo "[verify_mcp] done"
