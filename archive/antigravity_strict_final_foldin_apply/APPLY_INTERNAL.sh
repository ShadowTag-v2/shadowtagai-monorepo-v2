#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[info] monorepo root: $ROOT"
cd "$ROOT"

mkdir -p control/antigravity/strict_final_foldin
mkdir -p control/antigravity/v11
mkdir -p control/antigravity/final_ingest
mkdir -p data/memory
mkdir -p .agent/memory

# Stage strict-final assets for traceability
for f in \
  "$SELF_DIR/README_STRICT_FINAL_FOLDIN.md" \
  "$SELF_DIR/INSTALL_INTERNAL_APPLY.md" \
  "$SELF_DIR/KEEP_OR_DEMOTE.md" \
  "$SELF_DIR/PUBLIC_REPOS_TO_CLONE.md" \
  "$SELF_DIR/clone_public_support_repos.sh" \
  "$SELF_DIR/antigravity_v11_merged_control_plane_final_bundle.tar.gz" \
  "$SELF_DIR/antigravity_final_ingest_bundle.tar.gz" \
  "$SELF_DIR/ane_cortex_stack_v10_bundle.tar.gz" \
  "$SELF_DIR/operator_invariants.json" \
  "$SELF_DIR/operator_invariants_atoms.json" \
  "$SELF_DIR/fold_in_checklist.yaml" \
  "$SELF_DIR/setup_antigravity_v10_local.sh" \
  "$SELF_DIR/setup_antigravity_v11_merged.sh" \
  "$SELF_DIR/INSTALL_ANTIGRAVITY_V10_LOCAL.md" \
  "$SELF_DIR/INSTALL_ANTIGRAVITY_V11_MERGED.md" \
  "$SELF_DIR/antigravity_handoff.txt"
do
  [ -f "$f" ] && cp "$f" control/antigravity/strict_final_foldin/
done

# Ensure the v11 installer has every file it expects, including the final-ingest bundle.
for f in \
  "$SELF_DIR/antigravity_final_ingest_bundle.tar.gz" \
  "$SELF_DIR/ane_cortex_stack_v10_bundle.tar.gz" \
  "$SELF_DIR/fold_in_checklist.yaml" \
  "$SELF_DIR/operator_invariants.json" \
  "$SELF_DIR/operator_invariants_atoms.json" \
  "$SELF_DIR/INSTALL_ANTIGRAVITY_V10_LOCAL.md" \
  "$SELF_DIR/setup_antigravity_v10_local.sh" \
  "$SELF_DIR/setup_antigravity_v11_merged.sh" \
  "$SELF_DIR/INSTALL_ANTIGRAVITY_V11_MERGED.md"
do
  [ -f "$f" ] && cp "$f" control/antigravity/v11/
done

# Explicitly unpack final ingest in case the caller wants visible staging before v11 runs.
if [ -f control/antigravity/v11/antigravity_final_ingest_bundle.tar.gz ]; then
  echo "[extract] final ingest bundle -> control/antigravity/final_ingest"
  tar -xzf control/antigravity/v11/antigravity_final_ingest_bundle.tar.gz -C control/antigravity/final_ingest --strip-components=1 || true
fi

# Apply merged installer
if [ -f control/antigravity/v11/setup_antigravity_v11_merged.sh ]; then
  echo "[run] invoking v11 merged installer"
  bash control/antigravity/v11/setup_antigravity_v11_merged.sh "$ROOT"
else
  echo "[error] missing setup_antigravity_v11_merged.sh"
  exit 1
fi

cat <<'MSG'

[done] strict final fold-in apply complete.

Next:
1. cd control/antigravity/ane_cortex_stack_v10
2. uvicorn service.app.main:app --reload --port 8090
3. Make Antigravity call GET /api/hydrate-pack before substantial repo reasoning.
4. Clone public support repos only into external_support/public if needed.
MSG
