#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
OUT_DIR="$ROOT/docs/canonicalization"
REPORT="$OUT_DIR/gitignore_surfaces_report.md"

mkdir -p "$OUT_DIR"
cd "$ROOT"

ROOT_GITIGNORE="$ROOT/.gitignore"

mapfile -t GITIGNORE_FILES < <(
  find "$ROOT" -type d \( -name ".git" -o -name ".venv" -o -name "node_modules" \) -prune -o -type f -name ".gitignore" -print | sort
)

mapfile -t EXCLUDE_FILES < <(
  find "$ROOT/.git" -type f \( -path "*/info/exclude" \) 2>/dev/null | sort || true
)

COMMON_PATTERNS=(
  ".env"
  ".venv"
  "node_modules"
  "__pycache__"
  ".pytest_cache"
  ".mypy_cache"
  ".ruff_cache"
  "dist"
  "build"
  "coverage"
)

has_pattern() {
  local file="$1"
  local pattern="$2"
  rg -n --fixed-strings "$pattern" "$file" >/dev/null 2>&1
}

{
  echo "# .gitignore Canonicalization Report"
  echo
  echo "## Canonical Recommendation"
  echo "- canonical shared ignore file: \`.gitignore\` at repo root"
  echo "- local-only ignore belongs in \`.git/info/exclude\`"
  echo
  echo "## Root .gitignore Presence"
  if [[ -f "$ROOT_GITIGNORE" ]]; then
    echo "- present: \`$ROOT_GITIGNORE\`"
  else
    echo "- missing: \`$ROOT_GITIGNORE\`"
  fi
  echo
  echo "## Discovered .gitignore Files"
  if [[ ${#GITIGNORE_FILES[@]} -eq 0 ]]; then
    echo "- none"
  else
    for f in "${GITIGNORE_FILES[@]}"; do
      rel="${f#$ROOT/}"
      if [[ "$f" == "$ROOT_GITIGNORE" ]]; then
        echo "- \`${rel}\` → **canonical candidate**"
      else
        echo "- \`${rel}\` → **needs classification: necessary local override vs redundant vs stale**"
      fi
    done
  fi
  echo
  echo "## Local Exclude Files"
  if [[ ${#EXCLUDE_FILES[@]} -eq 0 ]]; then
    echo "- none"
  else
    for f in "${EXCLUDE_FILES[@]}"; do
      rel="${f#$ROOT/}"
      echo "- \`${rel}\` → local-only ignore surface"
    done
  fi
  echo
  echo "## Root Coverage Check"
  if [[ -f "$ROOT_GITIGNORE" ]]; then
    for p in "${COMMON_PATTERNS[@]}"; do
      if has_pattern "$ROOT_GITIGNORE" "$p"; then
        echo "- pattern present: \`$p\`"
      else
        echo "- pattern missing: \`$p\`"
      fi
    done
  else
    echo "- skipped; root .gitignore missing"
  fi
  echo
  echo "## Required Outcome"
  echo "- keep one canonical root .gitignore"
  echo "- keep only narrow, justified nested .gitignore overrides"
  echo "- move personal/local ignores to .git/info/exclude where appropriate"
  echo "- do not hide canonical source roots"
} > "$REPORT"

echo "Wrote $REPORT"
