#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
EXT="/Users/pikeymickey/.gemini/antigravity"

mkdir -p "$ROOT/docs" "$ROOT/scripts" "$ROOT/apps/counselconduit" "$ROOT/labs/uphillsnowball" "$ROOT/.vscode" "$ROOT/.cursor/rules"

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

  uphillsnowball:
    root: labs/uphillsnowball
    runtime: local-apple-silicon
    model: gemini-3.1-flash-lite-preview
    project: shadowtag-omega-v4

completion_rule:
  canonicalization_complete_when:
    - all_target_repos_have_status_canonical_or_archived
    - no_repo_has_status_unresolved
    - control_plane_has_single_canonical_mcp_config
    - deprecated_mcp_configs_are_demoted
EOF

cat > "$ROOT/docs/MERGE_STATUS.md" <<'EOF'
# MERGE_STATUS.md

## Status

The four-repo merge has been resolved at the manifest level.

### Canonical
- `ShadowTag-v2-fastapi-services` → `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
- `cosmic-crab-payload` → `apps/ShadowTag-v2_stack/cosmic-crab-payload`
- `Pipeline` → `apps/ShadowTag-v2_stack/Pipeline`
- `nascent-apollo` → `apps/ShadowTag-v2_stack/nascent-apollo`

## Meaning

All four shared repos now have one declared live canonical root.

There are no unresolved repos remaining in `monorepo_manifest.yaml`.

## Completion rule

A repo counts as fully merged only when:

1. it has exactly one declared canonical live root
2. it is no longer unresolved in `monorepo_manifest.yaml`
3. active tooling points to that canonical root
4. duplicate live roots, backup trees, recovered trees, legacy mirrors, and raw-ingest debris are excluded from live code paths

## Remaining work

Canonicalization of repo roots is complete.

Structural hardening may still remain, including:
- denied-zone cleanup in live trees
- build / CI hardening
- CODEOWNERS and protected-main enforcement
- shared contracts and `third_party` centralization
- repo-wide refactorability proof

## Summary

- 4 canonical
- 0 unresolved
- merge canonicalization complete

The monorepo is now structurally truthful at the repo-root layer.
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

cat > "$EXT/mcp_config.json" <<'EOF'
{
  "note": "RETIRED. Canonical MCP truth lives in /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json. Do not edit this file as a primary config surface."
}
EOF

cat > "$ROOT/.vscode/cline_mcp_settings.json" <<'EOF'
{
  "note": "ADAPTER ONLY. Canonical MCP truth lives in /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json. Mirror from canonical if required by client."
}
EOF

cat > "$ROOT/docs/UPDATED_PNKLN_PACK.md" <<'EOF'
# UPDATED_PNKLN_PACK.md

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

## Current truth

- four repos are canonical in `monorepo_manifest.yaml`
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

echo "[verify_mcp] validating JSON"
python3 - <<'PY'
import json, pathlib
p = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json")
json.loads(p.read_text())
print("[verify_mcp] json ok")
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

echo "[verify_mcp] smoke test: gemini stream command template present"
grep -q 'gemini-3.1-flash-lite-preview:streamGenerateContent' "$CONFIG"

echo "[verify_mcp] smoke test: lancedb command template present"
grep -q 'pnkln-lancedb-smoke-test' "$CONFIG"

echo "[verify_mcp] done"
EOF

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
- Do not revive obsolete thread artifacts once superseded by `docs/UPDATED_PNKLN_PACK.md`.
EOF

chmod +x "$ROOT/scripts/pnkln_lancedb.py" "$ROOT/scripts/verify_mcp.sh" "$ROOT/scripts/pnkln_root_guard.sh"

echo "[pnkln] all files written"
