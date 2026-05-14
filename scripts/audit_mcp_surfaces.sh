#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
OUT_DIR="$ROOT/docs/canonicalization"
REPORT="$OUT_DIR/mcp_surfaces_report.md"

CANONICAL_MCP="$ROOT/antigravity-mcp-config.json"
RETIRED_MCP="/Users/pikeymickey/.gemini/antigravity/mcp_config.json"
ADAPTER_MCP="$ROOT/.vscode/cline_mcp_settings.json"

EXPECTED_PROJECT="shadowtag-omega-v4"

mkdir -p "$OUT_DIR"
cd "$ROOT"

mapfile -t MCP_FILES < <(
  find "$ROOT" -type d \( -name ".git" -o -name ".venv" -o -name "node_modules" \) -prune -o -type f \( \
    -name "antigravity-mcp-config.json" -o \
    -name "mcp_config.json" -o \
    -name ".mcp.json" -o \
    -name "cline_mcp_settings.json" \
  \) -print | sort
)

mapfile -t SETTINGS_INLINE_MCP < <(
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/.venv/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/.lancedb/**' \
    --glob '!**/data/**' \
    --max-columns=500 \
    '"mcpServers"\s*:|mcp-remote|experimental:mcp|MCP-Protocol-Version|stitch\.googleapis\.com/mcp|developers\.google\.com/.*/mcp' \
    "$ROOT" || true
)

mapfile -t INLINE_SECRET_CANDIDATES < <(
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/.venv/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/.lancedb/**' \
    --glob '!**/data/**' \
    --max-columns=500 \
    -e 'AIza[0-9A-Za-z\-_]{20,}' \
    -e 'ghp_[A-Za-z0-9]{20,}' \
    -e 'github_pat_[A-Za-z0-9_]{20,}' \
    -e 'BEGIN PRIVATE KEY' \
    -e 'X-Goog-Api-Key:\s*[A-Za-z0-9\-_]+' \
    "$ROOT" || true
)

classify_file() {
  local path="$1"
  if [[ "$path" == "$CANONICAL_MCP" ]]; then
    echo "canonical"
  elif [[ "$path" == "$RETIRED_MCP" ]]; then
    echo "retired"
  elif [[ "$path" == "$ADAPTER_MCP" ]]; then
    echo "adapter-only"
  else
    echo "forbidden-to-revive"
  fi
}

{
  echo "# MCP Surfaces Canonicalization Report"
  echo
  echo "## Canonical Truth"
  echo "- canonical MCP: \`$CANONICAL_MCP\`"
  echo "- expected project anchor: \`$EXPECTED_PROJECT\`"
  echo
  echo "## Discovered MCP Files"
  if [[ ${#MCP_FILES[@]} -eq 0 ]]; then
    echo "- none"
  else
    for f in "${MCP_FILES[@]}"; do
      rel="${f#$ROOT/}"
      [[ "$f" == "$ROOT" ]] && rel="$f"
      echo "- \`${rel}\` → **$(classify_file "$f")**"
    done
  fi
  echo
  echo "## Inline MCP Definitions Outside Canonical File"
  if [[ ${#SETTINGS_INLINE_MCP[@]} -eq 0 ]]; then
    echo "- none"
  else
    printf '%s\n' "${SETTINGS_INLINE_MCP[@]}" | sed 's/^/- /'
  fi
  echo
  echo "## Inline Secret Candidates"
  if [[ ${#INLINE_SECRET_CANDIDATES[@]} -eq 0 ]]; then
    echo "- none"
  else
    printf '%s\n' "${INLINE_SECRET_CANDIDATES[@]}" | sed 's/^/- /'
  fi
  echo
  echo "## Required Outcome"
  echo "- only \`antigravity-mcp-config.json\` may remain a live MCP truth surface"
  echo "- adapter and retired files must be note-only stubs"
  echo "- no live secrets in committed MCP/config files"
} > "$REPORT"

echo "Wrote $REPORT"
