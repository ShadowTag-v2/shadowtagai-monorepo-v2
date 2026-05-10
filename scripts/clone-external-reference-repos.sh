#!/usr/bin/env bash
# scripts/clone-external-reference-repos.sh — Monorepo OS Clone Yard
# Reads external_repos/upstream_manifest.yaml and shallow-clones repos
# into external_repos/upstream/<group>/<org>/<repo>.
#
# Usage: ./scripts/clone-external-reference-repos.sh [--group GROUP] [--dry-run]
#
# Requires: git, python3 (for YAML parsing)
# All cloned repos are gitignored (external_repos/ is blanket-ignored).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="${REPO_ROOT}/external_repos/upstream_manifest.yaml"
TARGET_BASE="${REPO_ROOT}/external_repos/upstream"

# --- Flags ---
DRY_RUN=false
FILTER_GROUP=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=true; shift ;;
    --group)    FILTER_GROUP="$2"; shift 2 ;;
    -h|--help)  echo "Usage: $0 [--group GROUP] [--dry-run]"; exit 0 ;;
    *)          echo "Unknown flag: $1"; exit 1 ;;
  esac
done

if [[ ! -f "$MANIFEST" ]]; then
  echo "✗ Manifest not found: ${MANIFEST}"
  exit 1
fi

# --- Parse manifest with inline Python (avoids yq dependency) ---
parse_repos() {
  /opt/homebrew/bin/python3.14 - "$MANIFEST" "$FILTER_GROUP" <<'PYEOF'
import sys, yaml, pathlib

manifest_path = sys.argv[1]
filter_group = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else ""

with open(manifest_path) as f:
    manifest = yaml.safe_load(f)

groups = manifest.get("groups", {})
policy = manifest.get("policy", {})
depth = policy.get("clone_depth", 1)

for group_name, repos in groups.items():
    if filter_group and group_name != filter_group:
        continue
    for repo_slug in repos:
        # repo_slug is "org/repo"
        print(f"{group_name}\t{repo_slug}\t{depth}")
PYEOF
}

# --- Clone loop ---
cloned=0
skipped=0
failed=0

echo "═══════════════════════════════════════════════════════"
echo " Clone Yard — external_repos/upstream_manifest.yaml"
echo " Target: ${TARGET_BASE}"
if [[ -n "$FILTER_GROUP" ]]; then
  echo " Filter: group=${FILTER_GROUP}"
fi
echo "═══════════════════════════════════════════════════════"

while IFS=$'\t' read -r group slug depth; do
  org="${slug%%/*}"
  repo="${slug##*/}"
  target_dir="${TARGET_BASE}/${group}/${org}/${repo}"

  if [[ -d "$target_dir/.git" ]] || [[ -d "$target_dir" && -n "$(ls -A "$target_dir" 2>/dev/null)" ]]; then
    echo "  ⊘ skip (exists): ${group}/${slug}"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "  ▸ would clone: https://github.com/${slug}.git → ${target_dir} (depth=${depth})"
    cloned=$((cloned + 1))
    continue
  fi

  echo "  ▸ cloning: ${slug} → ${group}/${org}/${repo}"
  mkdir -p "$target_dir"

  if git clone --depth "${depth}" --single-branch \
       "https://github.com/${slug}.git" "$target_dir" 2>/dev/null; then
    cloned=$((cloned + 1))
  else
    echo "  ✗ FAILED: ${slug}"
    failed=$((failed + 1))
    # Clean up empty dir on failure
    rmdir "$target_dir" 2>/dev/null || true
  fi
done < <(parse_repos)

echo "───────────────────────────────────────────────────────"
echo " Done: cloned=${cloned} skipped=${skipped} failed=${failed}"
echo "───────────────────────────────────────────────────────"

if [[ "$failed" -gt 0 ]]; then
  exit 1
fi
