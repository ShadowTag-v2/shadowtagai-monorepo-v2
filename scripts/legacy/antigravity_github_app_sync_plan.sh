#!/usr/bin/env bash
set -euo pipefail

echo "[plan] Antigravity GitHub app sync plan"
echo
echo "1. Read authority memory first"
echo "2. Fetch monorepo control-plane truth from GitHub app:"
echo "   - manifests/monorepo_manifest.yaml"
echo "   - docs/MERGE_STATUS.md"
echo "   - docs/ANTIGRAVITY_CONTROL_PLANE.md"
echo
echo "3. Enumerate all ehanc69 repos through GitHub app"
echo "4. Classify each repo into:"
echo "   - canonical_in_monorepo"
echo "   - queued_for_fold_in"
echo "   - legacy_reference"
echo "   - public_demo"
echo "   - deprecated"
echo
echo "5. Refresh local clones only for:"
echo "   - canonical_in_monorepo"
echo "   - queued_for_fold_in"
echo "   - runtime deps used by the stack"
echo
echo "6. Re-index changed files only"
echo "7. Rebuild launch packet"
echo "8. Open fold-in tasks for repos not yet canonicalized"
echo
echo "[note] This script is an execution policy stub."
echo "[note] The authoritative freshness/read path should come from the GitHub app inside Antigravity."
