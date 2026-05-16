#!/usr/bin/env bash
set -euo pipefail

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
  "apps/aiyou-fastapi-services"
  "apps/nascent-apollo"
  "apps/shadowtag-core"
)

CANONICAL_ROOTS=(
  "apps/aiyou_stack/aiyou-fastapi-services"
  "apps/aiyou_stack/cosmic-crab-payload"
  "apps/aiyou_stack/Pipeline"
  "apps/aiyou_stack/nascent-apollo"
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
  fail "missing monorepo_manifest.yaml"
fi

if [[ ! -f "$CANONICAL_MCP" ]]; then
  fail "missing canonical MCP file"
fi

if [[ ! -f "$CHECKLIST" ]]; then
  fail "missing fold_in_checklist.yaml"
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

if [[ ${#present_duplicate_roots[@]} -gt 0 ]]; then
  duplicate_live_root_result="FAIL"
else
  duplicate_live_root_result="PASS"
fi

log "Checking nested .git directories"
mapfile -t nested_git_dirs < <(
  find "$ROOT" \
    -path "$ROOT/.git" -prune -o \
    -type d -name ".git" -print
)

if [[ ${#nested_git_dirs[@]} -gt 0 ]]; then
  nested_git_result="FAIL"
else
  nested_git_result="PASS"
fi

log "Searching stale model ids"
mapfile -t stale_model_hits < <(
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/.venv/**' \
    --glob '!**/archive/**' \
    --glob '!**/tools/legacy/**' \
    -e 'gemini-[0-9]+\.[0-9]+-[A-Za-z0-9._-]+' \
    "$ROOT" | grep -v "$EXPECTED_MODEL" || true
)

log "Searching stale project ids"
mapfile -t stale_project_hits < <(
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/.venv/**' \
    --glob '!**/archive/**' \
    --glob '!**/tools/legacy/**' \
    -e 'shadowtag-[A-Za-z0-9._-]+' \
    "$ROOT" | grep -v "$EXPECTED_PROJECT" || true
)

log "Searching likely inline secrets"
mapfile -t inline_secret_hits < <(
  rg -n --hidden \
    --glob '!**/.git/**' \
    --glob '!**/node_modules/**' \
    --glob '!**/.venv/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/*.png' \
    --glob '!**/*.jpg' \
    --glob '!**/*.jpeg' \
    --glob '!**/*.webp' \
    --glob '!**/*.pdf' \
    --glob '!**/archive/**' \
    --glob '!**/tools/legacy/**' \
    -e 'AIza[0-9A-Za-z\-_]{20,}' \
    -e 'sk-[A-Za-z0-9]{20,}' \
    -e 'ghp_[A-Za-z0-9]{20,}' \
    -e 'github_pat_[A-Za-z0-9_]{20,}' \
    -e 'BEGIN PRIVATE KEY' \
    -e 'X-Goog-Api-Key:\s*[A-Za-z0-9\-_]+' \
    -e 'api[_-]?key["'"'"']?\s*[:=]\s*["'"'"'][^"'"'"']{8,}["'"'"']' \
    "$ROOT" || true
)

log "Computing final verdict"
final_verdict="COMPLETE"
blockers=()

if [[ ${#missing_canonical_roots[@]} -gt 0 ]]; then
  blockers+=("missing canonical roots")
fi

if [[ ${#missing_reference[@]} -gt 0 ]]; then
  blockers+=("missing reference repos")
fi

if [[ "$duplicate_live_root_result" != "PASS" ]]; then
  blockers+=("duplicate live roots")
fi

if [[ "$nested_git_result" != "PASS" ]]; then
  blockers+=("nested .git directories")
fi

if [[ ${#blockers[@]} -gt 0 ]]; then
  final_verdict="COMPLETE_WITH_BLOCKERS"
fi

log "Writing report"
{
  echo "# ADAPTER_ONLY_HARDENING_REPORT.md"
  echo
  echo "## Canonical truth files"
  echo "- workspace truth: \`monorepo_manifest.yaml\`"
  echo "- MCP truth: \`antigravity-mcp-config.json\`"
  echo "- checklist truth: \`fold_in_checklist.yaml\`"
  echo
  echo "## MCP surface classification"
  echo "- canonical: \`$CANONICAL_MCP\` ($MCP_CANONICAL_STATUS)"
  echo "- retired: \`$RETIRED_MCP\` ($MCP_RETIRED_STATUS)"
  echo "- adapter-only: \`$ADAPTER_MCP\` ($MCP_ADAPTER_STATUS)"
  echo
  echo "## Canonical root status"
  echo "### Present canonical roots"
  if [[ ${#present_canonical_roots[@]} -gt 0 ]]; then
    for x in "${present_canonical_roots[@]}"; do
      echo "- \`$x\`"
    done
  else
    echo "- none"
  fi
  echo
  echo "### Missing canonical roots"
  if [[ ${#missing_canonical_roots[@]} -gt 0 ]]; then
    for x in "${missing_canonical_roots[@]}"; do
      echo "- \`$x\`"
    done
  else
    echo "- none"
  fi
  echo
  echo "## Reference repo status"
  echo "### Present reference repos"
  if [[ ${#present_reference[@]} -gt 0 ]]; then
    for x in "${present_reference[@]}"; do
      echo "- \`$x\`"
    done
  else
    echo "- none"
  fi
  echo
  echo "### Missing reference repos"
  if [[ ${#missing_reference[@]} -gt 0 ]]; then
    for x in "${missing_reference[@]}"; do
      echo "- \`$x\`"
    done
  else
    echo "- none"
  fi
  echo
  echo "## Duplicate live root status"
  echo "- result: **$duplicate_live_root_result**"
  if [[ ${#present_duplicate_roots[@]} -gt 0 ]]; then
    echo
    echo "### Conflicting legacy roots still present"
    for x in "${present_duplicate_roots[@]}"; do
      echo "- \`$x\`"
    done
  fi
  echo
  echo "## Nested git status"
  echo "- result: **$nested_git_result**"
  if [[ ${#nested_git_dirs[@]} -gt 0 ]]; then
    echo
    echo "### Nested .git directories found"
    for x in "${nested_git_dirs[@]}"; do
      echo "- \`${x#$ROOT/}\`"
    done
  fi
  echo
  echo "## Stale model audit"
  echo "- expected model family: \`$EXPECTED_MODEL\`"
  echo "- findings: **${#stale_model_hits[@]}**"
  if [[ ${#stale_model_hits[@]} -gt 0 ]]; then
    echo
    echo "### Sample stale model hits"
    printf '%s\n' "${stale_model_hits[@]:0:50}" | sed 's/^/- /'
  fi
  echo
  echo "## Stale project audit"
  echo "- expected project: \`$EXPECTED_PROJECT\`"
  echo "- findings: **${#stale_project_hits[@]}**"
  if [[ ${#stale_project_hits[@]} -gt 0 ]]; then
    echo
    echo "### Sample stale project hits"
    printf '%s\n' "${stale_project_hits[@]:0:50}" | sed 's/^/- /'
  fi
  echo
  echo "## Inline secret audit"
  echo "- candidate findings: **${#inline_secret_hits[@]}**"
  if [[ ${#inline_secret_hits[@]} -gt 0 ]]; then
    echo
    echo "### Sample secret candidates"
    printf '%s\n' "${inline_secret_hits[@]:0:50}" | sed 's/^/- /'
  fi
  echo
  echo "## Blockers"
  if [[ ${#blockers[@]} -gt 0 ]]; then
    for x in "${blockers[@]}"; do
      echo "- $x"
    done
  else
    echo "- none"
  fi
  echo
  echo "## Final verdict"
  echo "- **$final_verdict**"
} > "$REPORT"

log "Done"
