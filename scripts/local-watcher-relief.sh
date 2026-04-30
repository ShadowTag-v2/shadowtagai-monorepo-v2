#!/usr/bin/env bash
set -euo pipefail

# scripts/local-watcher-relief.sh
#
# Removes local-only heavy reference clones and generated directories that can
# overwhelm macOS FSEvents / IDE file watchers.
#
# This does not remove manifest truth files.
# This does not remove canonical source.
#
# Usage:
#   scripts/local-watcher-relief.sh --dry-run
#   scripts/local-watcher-relief.sh --apply

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

MODE="${1:---dry-run}"

case "${MODE}" in
  --dry-run|--apply) ;;
  *)
    echo "Usage: $0 --dry-run|--apply" >&2
    exit 2
    ;;
esac

TARGETS=(
  "external_repos/upstream"
  "external_repos/ai-website-cloner"
  "external_repos/ai-website-cloner-template"
  "external_repos/omni_ingest"
  "external_repos/numpy-100"
  ".gitnexus"
  ".index"
  ".lancedb"
  ".lancedb_data"
  "browser_artifacts"
  ".reports/external_repos/clone-worktrees"
)

echo "== Local watcher relief =="
echo "Mode: ${MODE}"
echo

echo "Tracked external_repos files:"
git ls-files external_repos || true
echo

for target in "${TARGETS[@]}"; do
  if [ -e "${target}" ]; then
    size="$(du -sh "${target}" 2>/dev/null | awk '{print $1}' || echo unknown)"
    if [ "${MODE}" = "--dry-run" ]; then
      echo "[DRY] remove ${target} (${size})"
    else
      echo "Removing ${target} (${size})"
      rm -rf "${target}"
    fi
  fi
done

if [ "${MODE}" = "--apply" ]; then
  mkdir -p external_repos
fi

echo
echo "Tracked external_repos files after:"
git ls-files external_repos || true
echo
echo "Done."
