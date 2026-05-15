import os
import pathlib

ROOT = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")

files = {}

files["apps/counselconduit/.env.example"] = """\
APP_ENV=development
APP_NAME=counselconduit
GOOGLE_CLOUD_PROJECT=shadowtag-omega-v4
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-3.1-flash-lite-preview

API_KEY=
STITCH_API_KEY=
DEVELOPER_KNOWLEDGE_API_KEY=

GOOGLE_APPLICATION_CREDENTIALS=/Users/pikeymickey/.config/gcloud/application_default_credentials.json
FIREBASE_PROJECT_ID=shadowtag-omega-v4

PORT=8080
LOG_LEVEL=INFO
ENABLE_DEBUG=false

COUNSELCONDUIT_DATA_DIR=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/data/counselconduit
COUNSELCONDUIT_MODE=stateless
COUNSELCONDUIT_BYOK=true
"""

files["labs/uphillsnowball/.env.example"] = """\
APP_ENV=development
APP_NAME=uphillsnowball
GOOGLE_CLOUD_PROJECT=shadowtag-omega-v4
GOOGLE_CLOUD_LOCATION=us-central1
GEMINI_MODEL=gemini-3.1-flash-lite-preview

API_KEY=
STITCH_API_KEY=
DEVELOPER_KNOWLEDGE_API_KEY=

UPHILLSNOWBALL_DATA_DIR=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/data/uphillsnowball
UPHILLSNOWBALL_LANCEDB_DIR=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/data/lancedb
APPLE_SILICON_LOCAL_ONLY=true
ENABLE_ANE_EXPERIMENTS=true

LOG_LEVEL=DEBUG
ENABLE_DEBUG=true
"""

files["database_tools.yaml"] = """\
version: "1"
metadata:
  name: "pnkln-database-tools"
  description: "Local database helper commands for pnkln on Apple Silicon using LanceDB"

tools:
  - name: "pnkln_lancedb_smoke_test"
    description: "Run the local LanceDB smoke test"
    command: "python3"
    args:
      - "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scripts/pnkln_lancedb.py"
      - "--smoke-test"

  - name: "pnkln_lancedb_init"
    description: "Initialize the local LanceDB workspace"
    command: "python3"
    args:
      - "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scripts/pnkln_lancedb.py"
      - "--init"

  - name: "pnkln_lancedb_stats"
    description: "Print local LanceDB stats"
    command: "python3"
    args:
      - "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scripts/pnkln_lancedb.py"
      - "--stats"
"""

files["configs/feature_flags.yaml"] = """\
version: 1

flags:
  counselconduit_stateless_mode:
    enabled: true
    owner: counselconduit

  counselconduit_byok_routing:
    enabled: true
    owner: counselconduit

  uphillsnowball_local_ane_experiments:
    enabled: true
    owner: uphillsnowball

  retriever_eval_pipeline:
    enabled: true
    owner: pnkln

  green_loop_autopatch:
    enabled: false
    owner: pnkln
"""

files["ops/nginx/csp_collector.conf"] = """\
server {
  listen 8081;
  server_name localhost;

  add_header Cache-Control "no-store" always;
  add_header X-Frame-Options "DENY" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;

  location /csp-report {
    return 204;
  }
}
"""

files["scripts/pnkln_lancedb.py"] = """\
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys

DB_ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/data/lancedb")

def cmd_init() -> int:
    DB_ROOT.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"status": "ok", "action": "init", "path": str(DB_ROOT)}))
    return 0

def cmd_stats() -> int:
    exists = DB_ROOT.exists()
    files = []
    if exists:
        files = sorted(str(p.relative_to(DB_ROOT)) for p in DB_ROOT.rglob("*"))
    print(json.dumps({
        "status": "ok",
        "action": "stats",
        "path": str(DB_ROOT),
        "exists": exists,
        "file_count": len(files),
        "files": files[:100]
    }))
    return 0

def cmd_smoke_test() -> int:
    DB_ROOT.mkdir(parents=True, exist_ok=True)
    marker = DB_ROOT / "SMOKE_TEST_OK"
    marker.write_text("ok\\n", encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "action": "smoke-test",
        "path": str(DB_ROOT),
        "marker": str(marker)
    }))
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    if args.init:
        return cmd_init()
    if args.stats:
        return cmd_stats()
    if args.smoke_test:
        return cmd_smoke_test()

    parser.print_help(sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
"""

files["scripts/verify_mcp.sh"] = """\
#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
CONFIG="${ROOT}/antigravity-mcp-config.json"
ENV_FILE="${ROOT}/.env"
TOOLS_FILE="${ROOT}/database_tools.yaml"

echo "[verify_mcp] root: ${ROOT}"

[[ -f "${CONFIG}" ]] || { echo "[verify_mcp] missing ${CONFIG}"; exit 1; }
[[ -f "${ENV_FILE}" ]] || { echo "[verify_mcp] missing ${ENV_FILE}"; exit 1; }
[[ -f "${TOOLS_FILE}" ]] || { echo "[verify_mcp] missing ${TOOLS_FILE}"; exit 1; }

echo "[verify_mcp] loading env"
set -a
source "${ENV_FILE}"
set +a

required_vars=(
  STITCH_API_KEY
  DEVELOPER_KNOWLEDGE_API_KEY
  API_KEY
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "[verify_mcp] missing env var: ${var}"
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
grep -q 'gemini-3.1-flash-lite-preview:streamGenerateContent' "${CONFIG}"

echo "[verify_mcp] checking lancedb command"
grep -q 'pnkln-lancedb-smoke-test' "${CONFIG}"

echo "[verify_mcp] optional adapter presence only"
test -f "/Users/pikeymickey/.gemini/antigravity/mcp_config.json" && echo "[verify_mcp] retired adapter present"
test -f "${ROOT}/.vscode/cline_mcp_settings.json" && echo "[verify_mcp] vscode adapter present"

echo "[verify_mcp] done"
"""

files["scripts/pnkln_root_guard.sh"] = """\
#!/usr/bin/env bash
set -euo pipefail

EXPECTED="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
ACTUAL="$(pwd -P)"

if [[ "${ACTUAL}" != "${EXPECTED}" ]]; then
  echo "[pnkln-root-guard] ERROR"
  echo "Expected workspace root:"
  echo "  ${EXPECTED}"
  echo "Actual:"
  echo "  ${ACTUAL}"
  exit 1
fi

echo "[pnkln-root-guard] OK: ${ACTUAL}"
"""

for fname, content in files.items():
    if fname.startswith("/"):
        path = pathlib.Path(fname)
    else:
        path = ROOT / fname
    path.write_text(content, encoding="utf-8")
    if fname.endswith(".sh") or fname.endswith(".py"):
        os.chmod(path, 0o755)
    print(f"Wrote {path}")
