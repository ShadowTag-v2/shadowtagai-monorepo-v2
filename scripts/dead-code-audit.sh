#!/usr/bin/env bash
set -uo pipefail

root() { git rev-parse --show-toplevel 2>/dev/null || pwd; }
staged() { git diff --cached --name-only --diff-filter=ACMR; }

fail() { printf '%s\n' "[precommit][BLOCK] $*"; return 1; }
note() { printf '%s\n' "[precommit] $*"; }

check_gitignore() {
  cd "$(root)" || return 1
  [ -f .gitignore ] || fail "missing .gitignore" || return 1
}

check_no_env_files() {
  staged | grep -Eq '(^|/)\.env(\..*)?$' && fail ".env file staged" || return 0
}

check_no_prod_sourcemaps() {
  cd "$(root)" || return 1
  local bad=0
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in
      next.config.*|vite.config.*|webpack.config.*|rollup.config.*|package.json|netlify.toml|vercel.json)
        git show ":$f" 2>/dev/null | grep -nE 'productionBrowserSourceMaps\s*:\s*true|sourcemap\s*:\s*true|sourceMap\s*:\s*true' >/dev/null 2>&1 && {
          printf '%s\n' "[precommit][BLOCK] production source maps enabled in: $f"
          bad=1
        }
        ;;
    esac
  done <<< "$(staged)"
  [ "$bad" -eq 0 ] || return 1
}

check_alignment() {
  cd "$(root)" || return 1
  local bad=0
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in
      AGENTS.md|CLAUDE.md|GEMINI.md|operator_invariants.json|pricing_doctrine.md|release_checklist.md|BUSINESS_CONTEXT_LOCKED.md|antigravity-mcp-config.json|monorepo_manifest.yaml)
        local blob
        blob="$(git show ":$f" 2>/dev/null)"
        printf '%s' "$blob" | grep -q 'shadowtag-omega-v4' || {
          case "$f" in
            pricing_doctrine.md|release_checklist.md|BUSINESS_CONTEXT_LOCKED.md|AGENTS.md|CLAUDE.md|GEMINI.md|operator_invariants.json)
              printf '%s\n' "[precommit][BLOCK] project lock missing in: $f"
              bad=1
              ;;
          esac
        }
        printf '%s' "$blob" | grep -q 'gemini-3\.1-flash-lite-preview-thinking' || {
          case "$f" in
            AGENTS.md|CLAUDE.md|GEMINI.md|operator_invariants.json)
              printf '%s\n' "[precommit][BLOCK] authorized external model missing in: $f"
              bad=1
              ;;
          esac
        }
        ;;
    esac
  done <<< "$(staged)"
  [ "$bad" -eq 0 ] || return 1
}

check_business_context_file() {
  cd "$(root)" || return 1
  [ -f BUSINESS_CONTEXT_LOCKED.md ] || fail "missing BUSINESS_CONTEXT_LOCKED.md" || return 1
}

check_lockfile_when_manifest_changes() {
  if staged | grep -Eq '(^|/)package\.json$'; then
    staged | grep -Eq '(^|/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|npm-shrinkwrap\.json)$' || fail "package manifest changed without lockfile update" || return 1
  fi
  return 0
}

check_debug_and_storage() {
  cd "$(root)" || return 1
  local bad=0
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in
      *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.html)
        git show ":$f" 2>/dev/null | grep -nE 'console\.log\(|console\.debug\(|debugger;|localStorage|sessionStorage' >/dev/null 2>&1 && {
          printf '%s\n' "[precommit][BLOCK] debug or banned browser storage pattern in: $f"
          bad=1
        }
        ;;
    esac
  done <<< "$(staged)"
  [ "$bad" -eq 0 ] || return 1
}

check_30_point_tech_debt() {
  cd "$(root)" || return 1
  local bad=0
  
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in
      *.ts|*.tsx|*.js|*.jsx|*.py|*.java|*.cs)
        # Debt 1 & 10: DB Queries / Feature Flags in Route Handlers
        if echo "$f" | grep -qE 'route|controller|api/'; then
            git show ":$f" 2>/dev/null | grep -nE 'SELECT \* FROM|UPDATE |DELETE FROM|db\.query' >/dev/null 2>&1 && {
              note "Raw DB query in route handler (Tech Debt 1): $f"
              bad=1
            }
            git show ":$f" 2>/dev/null | grep -nE 'process\.env\.FEATURE_' >/dev/null 2>&1 && {
              note "Inline feature flag detected (Tech Debt 10): $f"
              bad=1
            }
        fi

        # Debt 3 & 14: Hardcoded Secrets
        git show ":$f" 2>/dev/null | grep -nE "api_key['\"]?\s*:\s*['\"]sk-[a-zA-Z0-9]{10,}" >/dev/null 2>&1 && {
          note "Hardcoded secret detected (Tech Debt 3/14): $f"
          bad=1
        }

        # Debt 4: Monolith Ban (>2000 LOC to encourage Rich Hickey splitting)
        local lines
        lines=$(git show ":$f" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$lines" -gt 2000 ]; then
          note "File exceeds 2000 lines. Apply Rich Hickey protocol: split by concern (Tech Debt 4): $f"
          bad=1
        fi
        ;;
    esac
  done <<< "$(staged)"

  # Debt 2: Missing tests for AI generated code
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in
      apps/*.ts|apps/*.tsx|apps/*.py|apps/*.java|apps/*.cs)
        local basename
        basename=$(basename "$f" | cut -d. -f1)
        if ! find tests/ apps/ src/test -name "*${basename}*test*" -o -name "*${basename}*spec*" 2>/dev/null | grep -q .; then
             note "Modified file $f has no tests. AI-generated code without tests is untouchable (Tech Debt 2)."
        fi
        ;;
    esac
  done <<< "$(staged)"

  [ "$bad" -eq 0 ] || return 1
}

run_typecheck_if_present() {
  cd "$(root)" || return 1
  [ -f package.json ] || return 0
  python3 - "$PWD/package.json" <<'PY'
import json, sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    pkg = json.load(f)
sys.exit(0 if "typecheck" in pkg.get("scripts", {}) else 1)
PY
  if [ $? -eq 0 ]; then
    npm run typecheck || fail "typecheck failed" || return 1
  fi
}

main() {
  note "running v8.3 guard & 30-Point Tech Debt Guillotine"
  check_gitignore || exit 1
  check_no_env_files || exit 1
  check_no_prod_sourcemaps || exit 1
  check_alignment || exit 1
  check_business_context_file || exit 1
  check_lockfile_when_manifest_changes || exit 1
  check_debug_and_storage || exit 1
  
  check_30_point_tech_debt || exit 1
  
  run_typecheck_if_present || exit 1
  note "all checks passed"
}

main "$@"
