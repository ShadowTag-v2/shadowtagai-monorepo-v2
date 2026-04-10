#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
FINAL_BUNDLE="${2:-./antigravity_final_ingest_bundle.tar.gz}"
V10_BUNDLE="${3:-./ane_cortex_stack_v10_bundle.tar.gz}"

echo "[info] monorepo root: $ROOT"
cd "$ROOT"

mkdir -p control/antigravity/final_ingest
mkdir -p control/antigravity/ane_cortex_stack_v10
mkdir -p data/memory
mkdir -p .agent/memory

if [ -f "$FINAL_BUNDLE" ]; then
  echo "[extract] final ingest bundle -> control/antigravity/final_ingest"
  tar -xzf "$FINAL_BUNDLE" -C control/antigravity/final_ingest --strip-components=1
else
  echo "[warn] final ingest bundle not found: $FINAL_BUNDLE"
fi

if [ ! -f "$V10_BUNDLE" ] && [ -f "control/antigravity/final_ingest/ane_cortex_stack_v10_bundle.tar.gz" ]; then
  V10_BUNDLE="control/antigravity/final_ingest/ane_cortex_stack_v10_bundle.tar.gz"
fi

if [ -f "$V10_BUNDLE" ]; then
  echo "[extract] v10 bundle -> control/antigravity/ane_cortex_stack_v10"
  rm -rf control/antigravity/ane_cortex_stack_v10/*
  tar -xzf "$V10_BUNDLE" -C control/antigravity/ane_cortex_stack_v10 --strip-components=1
else
  echo "[warn] v10 bundle not found: $V10_BUNDLE"
fi

if [ -f "control/antigravity/ane_cortex_stack_v10/data_templates/authority-current.json" ]; then
  cp "control/antigravity/ane_cortex_stack_v10/data_templates/authority-current.json" "data/memory/authority-current.json"
  echo "[ok] authority-current.json promoted to data/memory/"
elif [ ! -f "data/memory/authority-current.json" ]; then
  cat > "data/memory/authority-current.json" <<'JSON'
{
  "version": 1,
  "repo_id": "ane",
  "startup_contract": {
    "hydrate_before_reasoning": true,
    "ignore_codebase_as_authority": true,
    "upgrade_codebase_from_memory": true
  },
  "standards": {
    "formatter": "prettier-vscode",
    "memory_mode": "authority_first",
    "context_rule": "never start from old codebase state"
  },
  "settings": {
    "default_inference_backend": "ane",
    "fallback_backend": "metal"
  },
  "procedures": [
    "Load authority memory first",
    "Load latest task state second",
    "Load codebase only after memory hydration",
    "If mismatch exists, create upgrade task instead of mutating memory backward"
  ]
}
JSON
  echo "[ok] authority-current.json seeded"
fi

touch data/memory/memories.jsonl
if [ ! -f data/memory/launch-packet.json ]; then
  echo '{}' > data/memory/launch-packet.json
fi

for f in   control/antigravity/final_ingest/fold_in_checklist.yaml   control/antigravity/final_ingest/antigravity_github_app_policy.md   control/antigravity/final_ingest/antigravity_github_app_sync_plan.sh   control/antigravity/final_ingest/clone_upstreams_v10.sh
do
  if [ -f "$f" ]; then
    cp "$f" .
  fi
done

GEN="control/antigravity/ane_cortex_stack_v10/scripts/generate_memory_bank_views.py"
if [ -f "$GEN" ]; then
  echo "[run] generate derived .agent/memory views"
  python3 "$GEN" || echo "[warn] generator failed; continuing"
fi

BOOTSTRAP="control/antigravity/ane_cortex_stack_v10/scripts/bootstrap.sh"
if [ -f "$BOOTSTRAP" ]; then
  echo "[run] bootstrap local SQLite/data dirs"
  bash "$BOOTSTRAP" || echo "[warn] bootstrap failed; continuing"
fi

if [ -f "control/antigravity/ane_cortex_stack_v10/docker-compose.yml" ]; then
  echo "[run] starting docker services"
  (cd control/antigravity/ane_cortex_stack_v10 && docker compose up -d) || echo "[warn] docker compose failed; continuing"
fi

SEED="control/antigravity/ane_cortex_stack_v10/scripts/bootstrap_memory_first.py"
if [ -f "$SEED" ]; then
  echo "[run] seed memory-first bootstrap"
  python3 "$SEED" || echo "[warn] bootstrap_memory_first failed; continuing"
fi

EXPORT="control/antigravity/ane_cortex_stack_v10/scripts/export_launch_packet.py"
if [ -f "$EXPORT" ]; then
  echo "[run] export launch packet"
  python3 "$EXPORT" || echo "[warn] export_launch_packet failed; continuing"
fi

cat <<'EOF'

[done] Antigravity v10 local install staged.

Next:
1. Start API from:
   control/antigravity/ane_cortex_stack_v10
2. Example:
   cd control/antigravity/ane_cortex_stack_v10
   uvicorn service.app.main:app --reload --port 8090
3. Make Antigravity call:
   GET /api/hydrate-pack

Canonical local truth:
- data/memory/authority-current.json
- fold_in_checklist.yaml
- manifests/monorepo_manifest.yaml
- docs/MERGE_STATUS.md
- docs/ANTIGRAVITY_CONTROL_PLANE.md
EOF
