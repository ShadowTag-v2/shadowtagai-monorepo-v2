#!/usr/bin/env bash
# Manifest Drift Guard — validates monorepo_manifest.yaml structural integrity
# Called from pre-commit hook to prevent CI workflow drift
set -euo pipefail

MONOREPO_ROOT="${MONOREPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
MANIFEST="$MONOREPO_ROOT/monorepo_manifest.yaml"
WORKFLOWS_DIR="$MONOREPO_ROOT/.github/workflows"
ERRORS=0

if [ ! -f "$MANIFEST" ]; then
  echo "❌ DRIFT: monorepo_manifest.yaml not found at $MANIFEST"
  exit 1
fi

# Check 1: Verify all CI workflow files referenced in manifest exist on disk
echo "[1/3] Checking CI workflow paths..."
# Extract workflow file paths from manifest (lines matching "path:" under ci_workflows)
# Simple grep approach — works for the flat YAML structure we use
WORKFLOW_PATHS=$(awk '/^ci_workflows:/,/^[a-z]/' "$MANIFEST" | grep -E '^\s+path:' | sed 's/.*path:\s*//; s/["\x27]//g; s/\s*$//' 2>/dev/null || true)

for wf_path in $WORKFLOW_PATHS; do
  full_path="$MONOREPO_ROOT/$wf_path"
  if [ ! -f "$full_path" ]; then
    echo "❌ DRIFT: Manifest references '$wf_path' but file does not exist"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check 2: Verify all actual workflow files are referenced in manifest
echo "[2/3] Checking for untracked workflows..."
if [ -d "$WORKFLOWS_DIR" ]; then
  for wf_file in "$WORKFLOWS_DIR"/*.yml "$WORKFLOWS_DIR"/*.yaml; do
    if [ -f "$wf_file" ]; then
      basename_file=$(basename "$wf_file")
      if ! grep -q "$basename_file" "$MANIFEST" 2>/dev/null; then
        echo "⚠️  WARNING: Workflow '$basename_file' exists but is not in manifest"
        # Don't count as error — warnings are informational
      fi
    fi
  done
fi

# Check 3: Verify critical truth files exist
echo "[3/3] Checking canonical truth files..."
TRUTH_FILES=(
  "AGENTS.md"
  "monorepo_manifest.yaml"
  "BUSINESS_CONTEXT_LOCKED.md"
  "RISK_REGISTER.md"
  "firestore.rules"
  "storage.rules"
  ".firebaserc"
  "firebase.json"
)

for tf in "${TRUTH_FILES[@]}"; do
  if [ ! -f "$MONOREPO_ROOT/$tf" ]; then
    echo "❌ DRIFT: Canonical truth file '$tf' is missing"
    ERRORS=$((ERRORS + 1))
  fi
done

if [ "$ERRORS" -eq 0 ]; then
  echo "✅ Manifest drift guard PASSED ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
else
  echo "❌ Manifest drift guard FAILED — $ERRORS errors ($(date -u +%Y-%m-%dT%H:%M:%SZ))"
  exit 1
fi
