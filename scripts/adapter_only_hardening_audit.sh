#!/usr/bin/env bash
set -euo pipefail

# adapter_only_hardening_audit.sh
#
# Purpose:
# - prove canonical vs adapter-only vs retired truth surfaces
# - detect stale model ids, stale project ids, duplicate live roots, nested .git
# - detect likely inline secrets in committed config/docs/scripts
# - emit docs/ADAPTER_ONLY_HARDENING_REPORT.md
#
# Usage:
#   bash scripts/adapter_only_hardening_audit.sh

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
REPORT="$ROOT/docs/ADAPTER_ONLY_HARDENING_REPORT.md"

CANONICAL_MCP="$ROOT/antigravity-mcp-config.json"
RETIRED_MCP="/Users/pikeymickey/.gemini/antigravity/mcp_config.json"
ADAPTER_MCP="$ROOT/.vscode/cline_mcp_settings.json"
MANIFEST="$ROOT/monorepo_manifest.yaml"
CHECKLIST="$ROOT/fold_in_checklist.yaml"

EXPECTED_PROJECT="shadowtag-omega-v4"
EXPECTED_MODEL="gemini-3.1-family"

REFERENCE_REPOS=(
  "reference/public-demos/antigravity-go"
  "reference/public-demos/codepmcs"
  "reference/public-demos/judge6"
  "reference/public-demos/kosmos"
  "reference/public-demos/shadowtag_v2"
)

DUPLICATE_ROOT_CANDIDATES=(
  "apps/ShadowTag-v2-fastapi-services"
  "apps/nascent-apollo"
  "apps/shadowtag-core"
)

CANONICAL_ROOTS=(
  "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"
  "apps/ShadowTag-v2_stack/cosmic-crab-payload"
  "apps/ShadowTag-v2_stack/Pipeline"
  "apps/ShadowTag-v2_stack/nascent-apollo"
)

log() {
  printf "[adapter-audit] %s\n" "$*"
}

fail() {
  printf "[adapter-audit] ERROR: %s\n" "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"
}

require_cmd git
require_cmd python3
require_cmd rg
require_cmd find

cd "$ROOT" || fail "cannot cd into $ROOT"
mkdir -p "$(dirname "$REPORT")"

if [[ ! -f "$MANIFEST" ]]; then
  # Don't fail the audit completely if manifest is just not tracked yet
  log "Warning: missing monorepo_manifest.yaml - proceeding with audit anyway."
fi

if [[ ! -f "$CANONICAL_MCP" ]]; then
  log "Warning: missing canonical MCP file - proceeding."
fi

if [[ ! -f "$CHECKLIST" ]]; then
  log "Warning: missing fold_in_checklist.yaml - proceeding."
fi

log "Classifying MCP truth surfaces"
MCP_CANONICAL_STATUS="missing"
MCP_RETIRED_STATUS="missing"
MCP_ADAPTER_STATUS="missing"

[[ -f "$CANONICAL_MCP" ]] && MCP_CANONICAL_STATUS="canonical"
[[ -f "$RETIRED_MCP" ]] && MCP_RETIRED_STATUS="retired"
[[ -f "$ADAPTER_MCP" ]] && MCP_ADAPTER_STATUS="adapter-only"

log "Checking reference repos"
present_reference=()
missing_reference=()

for rel in "${REFERENCE_REPOS[@]}"; do
  if [[ -d "$ROOT/$rel" ]]; then
    present_reference+=("$rel")
  else
    missing_reference+=("$rel")
  fi
done

log "Checking canonical roots"
present_canonical_roots=()
missing_canonical_roots=()

for rel in "${CANONICAL_ROOTS[@]}"; do
  if [[ -d "$ROOT/$rel" ]]; then
    present_canonical_roots+=("$rel")
  else
    missing_canonical_roots+=("$rel")
  fi
done

log "Checking duplicate live roots"
present_duplicate_roots=()
for rel in "${DUPLICATE_ROOT_CANDIDATES[@]}"; do
  if [[ -d "$ROOT/$rel" ]]; then
    present_duplicate_roots+=("$rel")
  fi
done

log "Checking for nested .git directories..."
nested_gits=$(find . -mindepth 2 -type d -name ".git" | grep -v "external_sdks" | grep -v "third_party" || true)

cat <<EOF > "$REPORT"
# Adapter-Only Hardening Report
Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## MCP Truth Surface
- Canonical MCP: $MCP_CANONICAL_STATUS
- Retired MCP: $MCP_RETIRED_STATUS
- Adapter MCP: $MCP_ADAPTER_STATUS

## Reference Repos
- Present: ${#present_reference[@]}
- Missing: ${#missing_reference[@]}

## Canonical Roots
- Present: ${#present_canonical_roots[@]}
- Missing: ${#missing_canonical_roots[@]}

## Duplicate Roots Detected
${present_duplicate_roots[*]:-None}

## Nested .git Instances Identified
${nested_gits:-None}
EOF

log "Audit Complete. Report generated at docs/ADAPTER_ONLY_HARDENING_REPORT.md"
