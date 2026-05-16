#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[info] monorepo root: $ROOT"
cd "$ROOT"

mkdir -p control/antigravity/v11
mkdir -p data/memory
mkdir -p .agent/memory

# Stage v11 bundle contents into control plane cache
for f in \
  "$SELF_DIR/antigravity_final_ingest_bundle.tar.gz" \
  "$SELF_DIR/ane_cortex_stack_v10_bundle.tar.gz" \
  "$SELF_DIR/fold_in_checklist.yaml" \
  "$SELF_DIR/operator_invariants.json" \
  "$SELF_DIR/operator_invariants_atoms.json" \
  "$SELF_DIR/INSTALL_ANTIGRAVITY_V10_LOCAL.md" \
  "$SELF_DIR/setup_antigravity_v10_local.sh"
do
  if [ -f "$f" ]; then
    cp "$f" control/antigravity/v11/
  fi
done

# Install v10 using prior installer if available
if [ -f "control/antigravity/v11/setup_antigravity_v10_local.sh" ]; then
  echo "[run] invoking v10 local installer"
  bash "control/antigravity/v11/setup_antigravity_v10_local.sh" \
    "$ROOT" \
    "control/antigravity/v11/antigravity_final_ingest_bundle.tar.gz" \
    "control/antigravity/v11/ane_cortex_stack_v10_bundle.tar.gz"
fi

# Promote operator invariants
if [ -f "control/antigravity/v11/operator_invariants.json" ]; then
  cp "control/antigravity/v11/operator_invariants.json" "data/memory/operator_invariants.json"
  echo "[ok] operator_invariants.json installed"
fi
if [ -f "control/antigravity/v11/operator_invariants_atoms.json" ]; then
  cp "control/antigravity/v11/operator_invariants_atoms.json" "data/memory/operator_invariants_atoms.json"
  echo "[ok] operator_invariants_atoms.json installed"
fi

# Promote fold-in checklist to repo root for visibility
if [ -f "control/antigravity/v11/fold_in_checklist.yaml" ]; then
  cp "control/antigravity/v11/fold_in_checklist.yaml" "./fold_in_checklist.yaml"
  echo "[ok] fold_in_checklist.yaml installed at repo root"
fi

# If repo-native pnkln pack script exists, keep it as backbone truth.
if [ -f "./scripts/apply_latest_pack_2.sh" ]; then
  echo "[run] refreshing repo-native pnkln control plane"
  bash ./scripts/apply_latest_pack_2.sh || echo "[warn] apply_latest_pack_2.sh failed; continuing"
fi

# Generate derived memory-bank views again after refresh
GEN="control/antigravity/ane_cortex_stack_v10/scripts/generate_memory_bank_views.py"
if [ -f "$GEN" ]; then
  echo "[run] regenerate .agent/memory views"
  python3 "$GEN" || echo "[warn] memory-bank generation failed; continuing"
fi

# Export launch packet again after refresh
EXPORT="control/antigravity/ane_cortex_stack_v10/scripts/export_launch_packet.py"
if [ -f "$EXPORT" ]; then
  echo "[run] export launch packet"
  python3 "$EXPORT" || echo "[warn] export_launch_packet failed; continuing"
fi

cat <<'EOF'

[done] Antigravity v11 merged control-plane install staged.

Canonical local truth now:
- data/memory/authority-current.json
- data/memory/operator_invariants.json
- data/memory/operator_invariants_atoms.json
- manifests/monorepo_manifest.yaml
- docs/MERGE_STATUS.md
- docs/ANTIGRAVITY_CONTROL_PLANE.md
- fold_in_checklist.yaml

Next:
1. Start API from:
   control/antigravity/ane_cortex_stack_v10
2. Example:
   cd control/antigravity/ane_cortex_stack_v10
   uvicorn service.app.main:app --reload --port 8090
3. Make Antigravity call:
   GET /api/hydrate-pack
4. Use GitHub app for freshness/control and local clones only for indexing/execution.
EOF
