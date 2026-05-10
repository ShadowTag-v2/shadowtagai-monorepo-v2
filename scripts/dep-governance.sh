#!/usr/bin/env bash
# dep-governance.sh — Dependency Governance Gate
# Validates no BUILD file in canonical zones references forbidden zones.
#
# This script checks for structural violations — imports from archive/,
# external_repos/, apps/aiyou_stack/, venvs, or node_modules leaking
# into canonical Bazel packages.
#
# Usage: bash scripts/dep-governance.sh
# Exit 0 = clean, Exit 1 = violations found

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Forbidden zone patterns in BUILD deps
FORBIDDEN_PATTERNS=(
  "//archive"
  "//external_repos"
  "//external_sdks"
  "//apps/aiyou_stack"
  "//node_modules"
  "//.venv"
  "//.venv-314"
  "//.venv-3.14-bak"
  "//venv"
  "//.gitnexus"
  "//legacy_workspaces"
)

CANONICAL_DIRS=(
  "packages"
  "libs"
  "apps/counselconduit"
  "apps/kovelai"
  "apps/shadowtagai"
  "tools"
  "scripts"
  "infra"
)

violations=0
total_checked=0

echo "=== Dependency Governance Gate ==="
echo "Checking canonical BUILD files for forbidden-zone references..."
echo ""

for dir in "${CANONICAL_DIRS[@]}"; do
  target_dir="${REPO_ROOT}/${dir}"
  if [ ! -d "$target_dir" ]; then
    continue
  fi

  # Find all BUILD files in this canonical zone
  while IFS= read -r -d '' build_file; do
    total_checked=$((total_checked + 1))
    for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
      if grep -q "$pattern" "$build_file" 2>/dev/null; then
        echo "❌ VIOLATION: ${build_file#"$REPO_ROOT/"} references forbidden zone: $pattern"
        violations=$((violations + 1))
      fi
    done
  done < <(find "$target_dir" -name "BUILD" -o -name "BUILD.bazel" -print0 2>/dev/null)
done

echo ""
echo "Checked $total_checked BUILD files across ${#CANONICAL_DIRS[@]} canonical zones."

if [ "$violations" -gt 0 ]; then
  echo ""
  echo "❌ FAILED: $violations forbidden-zone dependency violation(s) found."
  echo "Fix: Remove references to archive/, external_repos/, aiyou_stack/ etc."
  echo "     Canonical packages must only depend on other canonical packages."
  exit 1
fi

echo "✅ PASSED: No forbidden-zone dependencies detected."

# =============================================================================
# Phase 2 check: verify BUILD files exist in required zones
# =============================================================================
echo ""
echo "=== Required Zone Coverage ==="

REQUIRED_ZONES=(
  "packages/tool_gateway"
  "packages/repo_oracle"
)

missing=0
for zone in "${REQUIRED_ZONES[@]}"; do
  zone_path="${REPO_ROOT}/${zone}"
  if [ ! -f "${zone_path}/BUILD.bazel" ] && [ ! -f "${zone_path}/BUILD" ]; then
    echo "❌ MISSING: ${zone} has no BUILD file (required by bazel_adoption.yaml)"
    missing=$((missing + 1))
  else
    echo "✅ ${zone} — BUILD file present"
  fi
done

if [ "$missing" -gt 0 ]; then
  echo ""
  echo "❌ FAILED: $missing required zone(s) missing BUILD files."
  exit 1
fi

echo ""
echo "✅ ALL GOVERNANCE CHECKS PASSED"
exit 0
