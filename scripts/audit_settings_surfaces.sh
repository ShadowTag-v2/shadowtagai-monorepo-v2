#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
OUT_DIR="$ROOT/docs/canonicalization"
REPORT="$OUT_DIR/settings_surfaces_report.md"

ROOT_SETTINGS="$ROOT/.vscode/settings.json"
WORKSPACE_FILE="$ROOT/pnkln.code-workspace"

mkdir -p "$OUT_DIR"
cd "$ROOT"

mapfile -t SETTINGS_FILES < <(
  find "$ROOT" -type d \( -name ".git" -o -name ".venv" -o -name "node_modules" \) -prune -o -type f -path "*/.vscode/settings.json" -print | sort
)

mapfile -t WORKSPACE_FILES < <(
  find "$ROOT" -type d \( -name ".git" -o -name ".venv" -o -name "node_modules" \) -prune -o -type f -name "*.code-workspace" -print | sort
)

mapfile -t SUSPICIOUS_SETTINGS < <(
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/.venv/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/.lancedb/**' \
    --glob '!**/data/**' \
    --max-columns=500 \
    '"mcpServers"\s*:|X-Goog-Api-Key|AIza[0-9A-Za-z\-_]{20,}|shadowtag-(omega|v[0-9])|gemini-[0-9]+\.[0-9]+-[A-Za-z0-9._-]+' \
    "$ROOT/.vscode" "$ROOT"/*.code-workspace 2>/dev/null || true
)

{
  echo "# settings.json Canonicalization Report"
  echo
  echo "## Canonical Recommendation"
  echo "- canonical root workspace settings: \`.vscode/settings.json\`"
  echo "- canonical operator workspace file: \`pnkln.code-workspace\`"
  echo
  echo "## Root Settings"
  if [[ -f "$ROOT_SETTINGS" ]]; then
    echo "- present: \`$ROOT_SETTINGS\`"
  else
    echo "- missing: \`$ROOT_SETTINGS\`"
  fi
  echo
  echo "## Workspace Files"
  if [[ ${#WORKSPACE_FILES[@]} -eq 0 ]]; then
    echo "- none"
  else
    for f in "${WORKSPACE_FILES[@]}"; do
      rel="${f#$ROOT/}"
      if [[ "$f" == "$WORKSPACE_FILE" ]]; then
        echo "- \`${rel}\` → **canonical operator entrypoint**"
      else
        echo "- \`${rel}\` → **needs classification**"
      fi
    done
  fi
  echo
  echo "## Discovered .vscode/settings.json Files"
  if [[ ${#SETTINGS_FILES[@]} -eq 0 ]]; then
    echo "- none"
  else
    for f in "${SETTINGS_FILES[@]}"; do
      rel="${f#$ROOT/}"
      if [[ "$f" == "$ROOT_SETTINGS" ]]; then
        echo "- \`${rel}\` → **canonical root settings**"
      else
        echo "- \`${rel}\` → **needs classification: necessary local override vs stale/superseded**"
      fi
    done
  fi
  echo
  echo "## Suspicious Settings Hits"
  if [[ ${#SUSPICIOUS_SETTINGS[@]} -eq 0 ]]; then
    echo "- none"
  else
    printf '%s\n' "${SUSPICIOUS_SETTINGS[@]}" | sed 's/^/- /'
  fi
  echo
  echo "## Required Outcome"
  echo "- keep one canonical root .vscode/settings.json"
  echo "- keep one canonical .code-workspace operator entrypoint"
  echo "- avoid inline secrets"
  echo "- avoid alternate MCP definitions in settings"
  echo "- allow subproject settings only when clearly justified"
} > "$REPORT"

echo "Wrote $REPORT"
