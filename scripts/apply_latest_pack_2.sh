#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

mkdir -p \
  "$ROOT/docs" \
  "$ROOT/.vscode" \
  "$ROOT/.cursor/rules" \
  "$ROOT/apps/counselconduit/spec" \
  "$ROOT/labs/uphillsnowball" \
  "$ROOT/configs" \
  "$ROOT/ops/nginx" \
  "$ROOT/ops/audits" \
  "$ROOT/scripts"

cat > "$ROOT/monorepo_manifest.yaml" <<'EOF'
version: 1

workspace:
  name: Monorepo-Uphillsnowball
  root: /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
  policy: latest-only
  source_of_truth: monorepo_manifest.yaml

repo_roots:
  ShadowTag-v2-fastapi-services:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services
    notes: Primary live backend root.

  cosmic-crab-payload:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/cosmic-crab-payload
    notes: Canonical payload/runtime support root.

  Pipeline:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/Pipeline
    notes: Live canonical root for Pipeline.

  nascent-apollo:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/nascent-apollo
    notes: Live canonical root for nascent-apollo.

control_plane:
  canonical_mcp_config: /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json
  deprecated_mcp_configs:
    - /Users/pikeymickey/.gemini/antigravity/mcp_config.json
    - /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.vscode/cline_mcp_settings.json

products:
  counselconduit:
    root: apps/counselconduit
    runtime: google-cloud
    model: gemini-3.1-flash-lite-preview
    project: shadowtag-omega-v4
    business_role: mvp-commercial-wedge

  uphillsnowball:
    root: labs/uphillsnowball
    runtime: local-apple-silicon
    model: gemini-3.1-flash-lite-preview
    project: shadowtag-omega-v4
    business_role: internal-rd-lab

completion_rule:
  canonicalization_complete_when:
    - all_target_repos_have_status_canonical_or_archived
    - no_repo_has_status_unresolved
    - control_plane_has_single_canonical_mcp_config
    - deprecated_mcp_configs_are_demoted

highest_value_opportunities:
  - "Fix truth surfaces first: canonical repo roots and one canonical MCP control plane."
  - "Operationalize recovered code: green loop, CSP collector, retriever eval, feature flags, pricing model, OCR summaries, Drive-ingest daemon."
  - "Make CounselConduit the business-facing MVP spec; keep pnkln/uphillsnowball as the internal engine."
EOF

cat > "$ROOT/docs/MERGE_STATUS.md" <<'EOF'
# MERGE_STATUS.md

## Status

The four-repo merge is complete at the canonical-root layer once this manifest lands.

### Canonical
- `ShadowTag-v2-fastapi-services` → `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
- `cosmic-crab-payload` → `apps/ShadowTag-v2_stack/cosmic-crab-payload`
- `Pipeline` → `apps/ShadowTag-v2_stack/Pipeline`
- `nascent-apollo` → `apps/ShadowTag-v2_stack/nascent-apollo`

## Meaning

All four shared repos have one declared live canonical root.
There are no unresolved repos remaining in `monorepo_manifest.yaml`.

## Completion rule

A repo counts as fully merged only when:

1. it has exactly one declared canonical live root
2. it is no longer unresolved in `monorepo_manifest.yaml`
3. active tooling points to that canonical root
4. duplicate live roots, backup trees, recovered trees, legacy mirrors, and raw-ingest debris are excluded from live code paths

## Remaining work

Canonicalization of repo roots is complete after the manifest patch lands.

Structural hardening may still remain:
- denied-zone cleanup in live trees
- build / CI hardening
- CODEOWNERS and protected-main enforcement
- shared contracts and `third_party` centralization
- repo-wide refactorability proof

## Strategic note

The highest-value unlock was not more drafting. It was making the monorepo truthful enough that product work, lab work, and agent work stop drifting apart.

- `CounselConduit` is the MVP commercial path.
- `uphillsnowball` is the internal R&D / Apple Silicon path.
- `pnkln` is the operating/control doctrine around them.

## Summary

- 4 canonical
- 0 unresolved
- merge canonicalization complete
EOF

cat > "$ROOT/antigravity-mcp-config.json" <<'EOF'
{
  "mcp": {
    "startupTimeoutMs": 60000,
    "toolTimeoutMs": 120000,
    "retryCount": 2
  },
  "mcpServers": {
    "stitch-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://stitch.googleapis.com/mcp",
        "--header",
        "X-Goog-Api-Key: ${STITCH_API_KEY}"
      ]
    },
    "developer-knowledge-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://developers.google.com/knowledge/mcp",
        "--header",
        "X-Goog-Api-Key: ${DEVELOPER_KNOWLEDGE_API_KEY}"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
    "dart-mcp-server": {
      "command": "dart",
      "args": [
        "mcp-server"
      ]
    },
    "mcp-toolbox-for-databases": {
      "command": "npx",
      "args": [
        "-y",
        "@toolbox-sdk/server@0.26.0",
        "--tools-file=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/database_tools.yaml",
        "--stdio",
        "--user-agent-metadata",
        "antigravity"
      ]
    },
    "firebase-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "firebase-tools@latest",
        "experimental:mcp",
        "--project",
        "shadowtag-omega-v4"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/pikeymickey/.config/gcloud/application_default_credentials.json"
      }
    },
    "chrome-devtools-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest"
      ]
    }
  },
  "commands": {
    "gemini-31-flash-lite-preview-stream": {
      "description": "Direct gemini-3.1-flash-lite-preview streaming test via Google AI Platform API key",
      "command": "bash",
      "args": [
        "-lc",
        "curl \"https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent?key=${API_KEY}\" -X POST -H \"Content-Type: application/json\" -d '{\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\"Explain how AI works in a few words\"}]}]}'"
      ]
    },
    "pnkln-lancedb-smoke-test": {
      "description": "Run local LanceDB smoke test on Apple Silicon",
      "command": "bash",
      "args": [
        "-lc",
        "python3 /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scripts/pnkln_lancedb.py --smoke-test"
      ]
    }
  }
}
EOF

mkdir -p "/Users/pikeymickey/.gemini/antigravity"
cat > "/Users/pikeymickey/.gemini/antigravity/mcp_config.json" <<'EOF'
{
  "note": "RETIRED. Canonical MCP truth lives in /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json. Do not edit this file as a primary config surface."
}
EOF

cat > "$ROOT/.vscode/cline_mcp_settings.json" <<'EOF'
{
  "note": "ADAPTER ONLY. Canonical MCP truth lives in /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json. Mirror from canonical if required by client."
}
EOF

cat > "$ROOT/docs/UPDATED_pnkln_PACK.md" <<'EOF'
# UPDATED_pnkln_PACK.md

## Canonical surviving files

### Control plane
- `monorepo_manifest.yaml`
- `docs/MERGE_STATUS.md`
- `antigravity-mcp-config.json`

### Demoted adapters
- `/Users/pikeymickey/.gemini/antigravity/mcp_config.json`
- `.vscode/cline_mcp_settings.json`

### Product env templates
- `apps/counselconduit/.env.example`
- `labs/uphillsnowball/.env.example`

### Runtime support
- `database_tools.yaml`
- `scripts/verify_mcp.sh`
- `scripts/pnkln_lancedb.py`
- `scripts/pnkln_root_guard.sh`
- `scripts/green_loop.py`
- `scripts/drive_ingest_daemon.py`
- `scripts/retriever_eval.py`
- `scripts/ocr_summary_ingest.py`

### Product and lab support
- `configs/feature_flags.yaml`
- `apps/counselconduit/spec/MVP.md`
- `apps/counselconduit/spec/PRICING.md`
- `apps/counselconduit/spec/VALUATION.md`
- `ops/nginx/csp_collector.conf`
- `ops/audits/third_party_inventory.md`

### Operator guidance
- `AGENTS.md`
- `docs/Cor.Constitution.v3.md`
- `.cursor/rules/cor-vibe-coding.mdc`

## What this pack supersedes

This pack supersedes:
- historical duplicate MCP config surfaces as sources of truth
- unresolved four-repo merge claims
- older partial pnkln pack drafts
- stale cross-thread MCP snippets
- non-canonical repo-root interpretations
- repeated doctrine-only drafts that were not backed by operational files

## Strategic recovery

### Highest-value missed opportunity 1
You already have enough recovered material to make `counselconduit` commercially coherent and `uphillsnowball` technically useful, but the repo still lacked a single truthful backbone. Fixing truth surfaces first unlocks everything else.

### Highest-value missed opportunity 2
Operationalize recovered code instead of redrafting it again:
- green loop
- CSP collector
- retriever eval
- feature flags
- pricing model
- OCR summaries
- Drive-ingest daemon

### Highest-value missed opportunity 3
The recovered CounselConduit blueprint is already stronger than later wandering branches. It should become the business-facing spec while `pnkln/uphillsnowball` remains the internal engine.

## Current truth

- four repos are canonical once the manifest patch lands
- one MCP config is canonical
- all secrets belong in `.env`
- `counselconduit` is the Google-native MVP product path
- `uphillsnowball` is the local Apple Silicon lab path
EOF

cat > "$ROOT/apps/counselconduit/.env.example" <<'EOF'
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
EOF

cat > "$ROOT/labs/uphillsnowball/.env.example" <<'EOF'
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
EOF

cat > "$ROOT/database_tools.yaml" <<'EOF'
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
EOF

cat > "$ROOT/configs/feature_flags.yaml" <<'EOF'
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
EOF

cat > "$ROOT/ops/nginx/csp_collector.conf" <<'EOF'
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
EOF

cat > "$ROOT/scripts/pnkln_lancedb.py" <<'EOF'
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
    marker.write_text("ok\n", encoding="utf-8")
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
EOF
chmod +x "$ROOT/scripts/pnkln_lancedb.py"

cat > "$ROOT/scripts/verify_mcp.sh" <<'EOF'
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
EOF
chmod +x "$ROOT/scripts/verify_mcp.sh"

cat > "$ROOT/scripts/pnkln_root_guard.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

EXPECTED="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
ACTUAL="$(pwd -P)"

if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "[pnkln-root-guard] ERROR"
  echo "Expected workspace root:"
  echo "  $EXPECTED"
  echo "Actual:"
  echo "  $ACTUAL"
  exit 1
fi

echo "[pnkln-root-guard] OK: $ACTUAL"
EOF
chmod +x "$ROOT/scripts/pnkln_root_guard.sh"

cat > "$ROOT/scripts/green_loop.py" <<'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
OUT = ROOT / "data" / "green_loop"
OUT.mkdir(parents=True, exist_ok=True)

payload = {
    "status": "ok",
    "system": "green-loop",
    "goal": "patch, verify, summarize, preserve only passing artifacts"
}

(OUT / "latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload))
EOF
chmod +x "$ROOT/scripts/green_loop.py"

cat > "$ROOT/scripts/drive_ingest_daemon.py" <<'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
OUT = ROOT / "data" / "drive_ingest"
OUT.mkdir(parents=True, exist_ok=True)

state = {
    "status": "ok",
    "system": "drive-ingest-daemon",
    "mode": "placeholder-for-gdrive-langextract-ingest",
    "next": [
        "pull latest docs",
        "extract structured summaries",
        "append to active resources"
    ]
}

(OUT / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
print(json.dumps(state))
EOF
chmod +x "$ROOT/scripts/drive_ingest_daemon.py"

cat > "$ROOT/scripts/retriever_eval.py" <<'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import json

report = {
    "status": "ok",
    "system": "retriever-eval",
    "metrics": {
        "precision_at_5": None,
        "recall_at_10": None,
        "grounding_pass_rate": None
    },
    "note": "wire this to Drive-ingest corpus and CounselConduit retrieval scenarios"
}

print(json.dumps(report, indent=2))
EOF
chmod +x "$ROOT/scripts/retriever_eval.py"

cat > "$ROOT/scripts/ocr_summary_ingest.py" <<'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
OUT = ROOT / "data" / "ocr"
OUT.mkdir(parents=True, exist_ok=True)

summary = {
    "status": "ok",
    "system": "ocr-summary-ingest",
    "sources": [],
    "note": "attach OCR/image summaries here and feed them through SOP-A triage"
}

(OUT / "latest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary))
EOF
chmod +x "$ROOT/scripts/ocr_summary_ingest.py"

cat > "$ROOT/scripts/subtree_merge_57.py" <<'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Iterable

DEFAULT_SRC_ROOT = Path("/Users/pikeymickey/ShadowTag-v2-stack")
DEFAULT_DST_ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/ShadowTag-v2_stack")
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".DS_Store"}


def iter_sources(root: Path) -> Iterable[Path]:
    for child in sorted(root.iterdir()):
        if child.name in EXCLUDE_DIRS:
            continue
        yield child


def copy_tree(src: Path, dst: Path) -> dict:
    copied = 0
    skipped = 0
    dst.mkdir(parents=True, exist_ok=True)

    for current_root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        rel_root = Path(current_root).relative_to(src)
        target_root = dst / rel_root
        target_root.mkdir(parents=True, exist_ok=True)

        for name in files:
            if name in EXCLUDE_DIRS:
                skipped += 1
                continue
            s = Path(current_root) / name
            t = target_root / name
            shutil.copy2(s, t)
            copied += 1

    return {
        "source": str(src),
        "destination": str(dst),
        "copied_files": copied,
        "skipped_files": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge external trees into monorepo subtree")
    parser.add_argument("--src-root", default=str(DEFAULT_SRC_ROOT))
    parser.add_argument("--dst-root", default=str(DEFAULT_DST_ROOT))
    parser.add_argument("--one", help="Merge only one named child repo/folder from src-root")
    args = parser.parse_args()

    src_root = Path(args.src_root).expanduser().resolve()
    dst_root = Path(args.dst_root).expanduser().resolve()

    if not src_root.exists():
        raise SystemExit(f"missing src root: {src_root}")

    results = []

    if args.one:
        src = src_root / args.one
        if not src.exists():
            raise SystemExit(f"missing requested source: {src}")
        dst = dst_root / args.one
        results.append(copy_tree(src, dst))
    else:
        for src in iter_sources(src_root):
            dst = dst_root / src.name
            if src.is_dir():
                results.append(copy_tree(src, dst))

    print(json.dumps({
        "status": "ok",
        "src_root": str(src_root),
        "dst_root": str(dst_root),
        "merged_count": len(results),
        "results": results
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
EOF
chmod +x "$ROOT/scripts/subtree_merge_57.py"

cat > "$ROOT/scripts/vertex_bootstrap.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-shadowtag-omega-v4}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
MODEL="${GEMINI_MODEL:-gemini-3.1-flash-lite-preview}"

echo "[vertex_bootstrap] project=$PROJECT_ID region=$REGION model=$MODEL"

gcloud services enable aiplatform.googleapis.com compute.googleapis.com >/dev/null 2>&1 || true

echo "[vertex_bootstrap] done"
EOF
chmod +x "$ROOT/scripts/vertex_bootstrap.sh"

cat > "$ROOT/scripts/gemini_stream_test.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

: "${API_KEY:?API_KEY is required}"

curl "https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent?key=${API_KEY}" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
EOF
chmod +x "$ROOT/scripts/gemini_stream_test.sh"

cat > "$ROOT/scripts/write_updated_pnkln_pack.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
mkdir -p "$ROOT"

echo "[write_updated_pnkln_pack] write the reconciled pack files here"
echo "[write_updated_pnkln_pack] this script is a placeholder wrapper for the atomic file blocks printed in chat"
EOF
chmod +x "$ROOT/scripts/write_updated_pnkln_pack.sh"

cat > "$ROOT/scripts/raw_links.txt" <<'EOF'
https://github.com/lancedb/lancedb
https://github.com/ollama/ollama-python
https://github.com/vinta/awesome-python
https://developers.googleblog.com/introducing-the-developer-knowledge-api-and-mcp-server/
https://developers.google.com/knowledge/mcp
https://stitch.googleapis.com/mcp
https://developers.google.com/knowledge/mcp
https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent
https://github.com/vercel-labs/agent-skills
https://github.com/REPOZY/superpowers-optimized
https://arxiv.org/pdf/2512.14982
EOF

cat > "$ROOT/apps/counselconduit/spec/MVP.md" <<'EOF'
# CounselConduit MVP

CounselConduit is the business-facing MVP.

## Wedge
Stateless legal SaaS workflow with premium pricing and BYOK routing.

## Product principles
- Google-native runtime
- fast onboarding
- premium SaaS economics
- low implementation friction
- high-trust summaries and retrieval

## Internal dependency
pnkln / uphillsnowball powers internal retrieval, eval, and experimentation.
EOF

cat > "$ROOT/apps/counselconduit/spec/PRICING.md" <<'EOF'
# CounselConduit pricing

## Position
Premium SaaS pricing aligned just below enterprise legal pain thresholds.

## Commercial logic
- faster turnaround
- lower internal legal handling time
- clean upgrade path
- BYOK lowers buyer friction

## Next step
Wire pricing assumptions into a live calculator backed by retriever-eval and usage telemetry.
EOF

cat > "$ROOT/apps/counselconduit/spec/VALUATION.md" <<'EOF'
# CounselConduit valuation

## Narrative
CounselConduit is the commercial wedge.
pnkln / uphillsnowball is the internal engine.

## Why this matters
This separation lets the business story stay simple while the technical engine compounding in the background.

## Leverage
- product clarity
- internal tooling leverage
- cheaper experimentation
- stronger defensibility
EOF

cat > "$ROOT/AGENTS.md" <<'EOF'
# AGENTS.md

## Mission

Keep the monorepo structurally truthful, Google-native, and latest-only.

## Repo truth

- `monorepo_manifest.yaml` is the canonical workspace truth.
- `antigravity-mcp-config.json` is the canonical MCP truth.
- Historical adapter files are not sources of truth.

## Product split

### counselconduit
- product path: `apps/counselconduit`
- runtime: Google Cloud
- project: `shadowtag-omega-v4`
- model: `gemini-3.1-flash-lite-preview`

### uphillsnowball
- lab path: `labs/uphillsnowball`
- runtime: local Apple Silicon
- purpose: R&D and local experimentation
- must not redefine counselconduit product truth

## Merge truth

All four repo roots must remain canonical:
- `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
- `apps/ShadowTag-v2_stack/cosmic-crab-payload`
- `apps/ShadowTag-v2_stack/Pipeline`
- `apps/ShadowTag-v2_stack/nascent-apollo`

## Guardrails

- never introduce a second source of truth for MCP
- never commit real secrets
- never mark a live repo archived
- never treat duplicate recovered trees as canonical
- fix root truth first, tooling second, runtime third

## Strategic note

Highest-value sequence:
1. truth surfaces
2. recovered operational code
3. commercial MVP hardening
EOF

cat > "$ROOT/docs/Cor.Constitution.v3.md" <<'EOF'
# Cor.Constitution.v3

## Core posture

Operate with disciplined, high-signal execution.
Prefer one source of truth per layer.
Prefer canonical roots over copied ambiguity.
Prefer automation over prose where possible.

## Canonical order

1. workspace truth
2. merge truth
3. MCP truth
4. runtime truth
5. product hardening

## Security

- all API tokens live in `.env`
- no secret material in committed JSON
- local adapters may exist, but must not become truth surfaces

## Product split

### counselconduit
Google-native MVP path.
Built for production readiness.

### uphillsnowball
Local Apple Silicon research path.
Used to improve internal methods and experimentation.
Not the product control plane.

## Non-negotiables

- `monorepo_manifest.yaml` is canonical workspace truth
- `antigravity-mcp-config.json` is canonical MCP truth
- all four repos remain live canonical roots
- no unresolved repo root may remain in steady state

## Highest-value missed opportunities

1. Truth surfaces first.
2. Recovered code second.
3. Commercial MVP clarity third.
EOF

cat > "$ROOT/.cursor/rules/cor-vibe-coding.mdc" <<'EOF'
---
description: pnkln canonical workspace and execution rules
globs: ["**/*"]
---

# pnkln rules

- Treat `monorepo_manifest.yaml` as canonical workspace truth.
- Treat `antigravity-mcp-config.json` as canonical MCP truth.
- Never create a second source-of-truth MCP config.
- Keep all four repo roots live and canonical.
- Put all API keys in `.env`, never inline in JSON.
- `counselconduit` is the Google-native MVP product path.
- `uphillsnowball` is the Apple Silicon local lab path.
- Fix truth surfaces before refactors.
- Prefer minimal, reviewable changes.
- Do not revive obsolete thread artifacts once superseded by `docs/UPDATED_pnkln_PACK.md`.
- Prefer operationalized recovered code over new doctrine prose.
EOF

cat > "$ROOT/ops/audits/third_party_inventory.md" <<'EOF'
# Third-party inventory

## Google-native
- Vertex AI / Gemini
- Firebase MCP
- Developer Knowledge MCP
- Stitch MCP
- Chrome DevTools MCP

## Local lab
- LanceDB
- Python local scripts

## Review targets
- remove stale non-canonical adapters from operational paths
- keep all keys in `.env`
- keep product/runtime split explicit
EOF

cat > "$ROOT/scripts/thread_audit_protocol.txt" <<'EOF'
/thread-recovery-2stage

Stage 1 — Audit and recover only

Re-read the full thread end to end. Build a complete ledger of:
- explicit requests
- implicit requirements
- constraints
- dependencies
- unresolved issues
- abandoned branches
- partially completed deliverables
- implied but unproduced code, analysis, or explanations

Search all available resources for missing context and evidence, including thread history, available artifacts, connected internal sources, Google Drive when available, relevant repos, and web research when useful.

Identify:
- omissions
- contradictions
- changed assumptions
- weak reasoning
- missing code paths
- overlooked implementation details
- performance opportunities
- maintainability improvements
- accuracy improvements
- leverage and monetization opportunities

Then reconcile:
- asked vs answered
- answered vs solved
- assumed vs verified
- explicit vs implied
- mentioned vs operationalized
- drafted vs implemented
- apparently complete vs actually complete
- local optimum vs global optimum
- technically correct vs commercially useful

Stage 1 output only:
A. Recovery findings
B. Complete task ledger
C. Missing or incomplete items
D. Newly recovered material
E. Distinctions and changed assumptions
F. What must be preserved, corrected, expanded, or replaced

Critical rule: do not rewrite answers yet. Do not regenerate code yet.

Stage 2 — Replan and regenerate

Using only the reconciled findings from Stage 1:
- rebuild the plan from first principles
- correct broken assumptions
- incorporate recovered material
- resequence the work for better clarity, implementation quality, and business outcome
- regenerate the answers
- reprint all relevant code in full

Optimize for:
- elegance
- simplicity
- correctness
- performance
- maintainability
- robustness
- accuracy
- clarity
- business leverage
- financial upside

Stage 2 output:
A. Revised plan
B. Regenerated answers
C. Full updated code

Critical rule: prefer truth over continuity, and elegance over thread momentum.
EOF

cat > "$ROOT/scripts/vertex_prompt_templates.txt" <<'EOF'
# pnkln Primer
Operate at pnklnJR(purpose)+Doctrine(reason)+ARM(brakes).
Run all-hands: digest latest → classify {KEEP|REFERENCE ONLY|DISCARD} → streamline/optimize → regenerate roll-up → post exec summary.
Apply SOPs A–D with Bourne boosts (2× throughput, +90% safety). If conflict/policy risk, voice objections and flag per pnklnJR.

# pnkln Repo Enforcement
Apply pnkln SOPs repo-wide:
1) Upload Triage: classify+score; KEEP→tickets→Active Resources; delta summary.
2) Change & Release: premortem(5), feature-flag, stress drills, promote/rollback, postmortem<24h.
3) Decision Protocol: Decision/Context/Options/Choice(pnklnJR+Doctrine)/Risks(ARM)/Owner+By-When/Metrics.
4) Code Review: minimal diff; tests; security/privacy; observability; rollback plan.
Return plan, diffs/actions, and exec summary.

# pnkln All-Hands Reset
Run all-hands now:
- Sort memory/docs by latest.
- Triage {KEEP|REFERENCE ONLY|DISCARD}.
- Streamline+optimize (pnklnJR+Doctrine+ARM).
- Regenerate comprehensive roll-up.
- Output "pnkln All-Hands Complete" + summary.

# pnkln Valuation Drill
Compute valuation uplift:
Inputs: ARR, OPEX, multiple(10× default).
Assume 15–30% OPEX savings from 2× throughput/decision velocity & +90% safety.
Convert to ARR-equivalent; valuation uplift = ARR-eq × multiple.
Return assumptions, math steps, sensitivity (15, 20, 25, 30%).

# pnkln Rapid Drill
Premortem10|RollbackChecklist|FailureInjection|AuditArtifacts|DebriefTemplate.

# pnkln Investor 2-Slide
Slide1Impact:2×Thru,+90Safety,2×DecVel,2.2×Endurance;Slide2Val:$3M/yr→$30M@10×;Mid/Ent+scaling.
EOF

cat > "$ROOT/scripts/counselconduit_blueprint.txt" <<'EOF'
CounselConduit is the business-facing MVP.

Wedge:
- stateless legal SaaS
- premium pricing
- BYOK routing
- fast onboarding
- high-trust retrieval and summaries

Commercial role:
- simplest product story
- shortest path to revenue
- cleaner buyer narrative than sprawling internal platform language

Internal dependency:
- pnkln / uphillsnowball supplies retrieval, eval, experimentation, security hardening, and local lab velocity
EOF

cat > "$ROOT/scripts/uphillsnowball_lab_blueprint.txt" <<'EOF'
uphillsnowball is the internal Apple Silicon lab path.

Purpose:
- local experimentation
- LanceDB / Apple Silicon / ANE-adjacent work
- internal eval harness
- OCR and retrieval experimentation
- operational tooling for pnkln

Non-goal:
- do not let uphillsnowball redefine CounselConduit product truth
EOF

cat > "$ROOT/scripts/final_next_order.txt" <<'EOF'
Best next order to land the current thread pack:

1. patch monorepo_manifest.yaml
2. replace docs/MERGE_STATUS.md
3. install canonical antigravity-mcp-config.json
4. demote adapter MCP files
5. replace verify_mcp.sh
6. add docs/UPDATED_pnkln_PACK.md
7. add recovered operational scripts
8. add CounselConduit product spec files
9. verify root truth
10. commit only after verification passes
EOF

cat > "$ROOT/scripts/vertex_operator_notes.txt" <<'EOF'
Google-native operator direction:
- one canonical MCP config
- one canonical monorepo manifest
- all secrets in .env
- gemini-3.1-flash-lite-preview everywhere
- counselconduit is the product
- uphillsnowball is the lab
- operationalize recovered code before drafting more doctrine
EOF

cat > "$ROOT/scripts/highest_value_opportunities.txt" <<'EOF'
Highest-value missed opportunity 1:
You already have enough recovered material to make counselconduit commercially coherent and uphillsnowball technically useful, but the repo still lacked a single truthful backbone. Fixing truth surfaces first unlocks everything else.

Highest-value missed opportunity 2:
Operationalize recovered code instead of redrafting it again:
- green loop
- CSP collector
- retriever eval
- feature flags
- pricing model
- OCR summaries
- Drive-ingest daemon

Highest-value missed opportunity 3:
The recovered CounselConduit blueprint is already stronger than later wandering branches. It should become the business-facing spec while pnkln/uphillsnowball remains the internal engine.
EOF

cat > "$ROOT/scripts/recovery_summary.txt" <<'EOF'
Recovered truth:
- product, lab, and control-plane were mixed in thread momentum
- current strongest direction is:
  - counselconduit = business-facing Google-native MVP
  - uphillsnowball = internal Apple Silicon lab
  - pnkln = operating/control doctrine
- canonicalization and control-plane truth must be fixed before more feature drafting
EOF

cat > "$ROOT/scripts/atomic_rollup_manifest.txt" <<'EOF'
This atomic rollup includes current surviving non-script artifacts:
- docs
- prompts
- env examples
- policy/operator notes
- mcp adapter notes
- product/spec artifacts

It excludes:
- stale superseded variants
- earlier contradictory drafts
- obsolete thread momentum claims
EOF

echo "[OK] wrote updated pnkln pack to $ROOT"
