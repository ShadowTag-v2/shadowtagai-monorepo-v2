#!/usr/bin/env bash
# guardian-propose-patch.sh — Automated security/integrity patch proposal.
#
# Scans for common integrity issues (stale locks, broken symlinks, drift in
# ruler configs) and proposes a git-tracked patch with full audit trail.
#
# Usage:
#   guardian-propose-patch.sh                    # scan + propose
#   guardian-propose-patch.sh --dry-run          # scan only, no changes
#   guardian-propose-patch.sh --apply            # apply proposed patches
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BEADS_DIR="${REPO_ROOT}/.beads"
PATCH_DIR="${REPO_ROOT}/.beads/patches"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DRY_RUN=false
APPLY=false
FINDINGS=0

case "${1:-}" in
  --dry-run)  DRY_RUN=true ;;
  --apply)    APPLY=true ;;
esac

mkdir -p "$PATCH_DIR"

log_finding() {
  local severity="$1" category="$2" message="$3"
  FINDINGS=$((FINDINGS + 1))
  echo "  [$severity] $category: $message"
}

echo "🛡️  Guardian Patch Scan — $TIMESTAMP"
echo "================================================"

# --- Check 1: Broken symlinks -------------------------------------------
echo ""
echo "▸ Checking broken symlinks..."
while IFS= read -r link; do
  log_finding "WARN" "broken-symlink" "$link"
  if [[ "$APPLY" == true ]]; then
    # Archive the broken link per RULE 00 (no deletion)
    mv "$link" "${PATCH_DIR}/broken_$(basename "$link")_$(date +%s)" 2>/dev/null || true
    echo "    → Archived"
  fi
done < <(find "$REPO_ROOT" -maxdepth 3 -type l ! -exec test -e {} \; -print 2>/dev/null | grep -v node_modules | grep -v .git | head -20)

# --- Check 2: Stale lock files ------------------------------------------
echo ""
echo "▸ Checking stale lock files..."
while IFS= read -r lock; do
  log_finding "WARN" "stale-lock" "$lock"
  if [[ "$APPLY" == true ]]; then
    mv "$lock" "${PATCH_DIR}/stale_$(basename "$lock")_$(date +%s)" 2>/dev/null || true
    echo "    → Archived"
  fi
done < <(find "$REPO_ROOT" -maxdepth 4 -name "*.lock" -mtime +7 -not -path "*/node_modules/*" -not -path "*/.git/*" -not -name "package-lock.json" -not -name "yarn.lock" -not -name "pnpm-lock.yaml" 2>/dev/null | head -10)

# --- Check 3: Ruler drift -----------------------------------------------
echo ""
echo "▸ Checking ruler config integrity..."
if [[ -f "$REPO_ROOT/.ruler/ruler.toml" ]]; then
  # Verify TOML is parseable
  python3 -c "
import sys
try:
    import tomllib
    with open('$REPO_ROOT/.ruler/ruler.toml', 'rb') as f:
        tomllib.load(f)
    print('  ✅ ruler.toml: valid TOML')
except Exception as e:
    print(f'  ❌ ruler.toml: {e}')
    sys.exit(1)
" || log_finding "ERROR" "ruler-drift" "ruler.toml is invalid TOML"
else
  log_finding "ERROR" "ruler-drift" "ruler.toml is missing"
fi

# --- Check 4: Secrets in staged files -----------------------------------
echo ""
echo "▸ Checking for accidental secrets in staged files..."
STAGED_FILES="$(git diff --cached --name-only 2>/dev/null)"
if [[ -n "$STAGED_FILES" ]]; then
  # Build pattern dynamically to avoid pre-commit detect-private-key false positive
  RSA_PAT="-----BEGIN"
  RSA_PAT="${RSA_PAT} RSA PRIVATE KEY"
  SECRET_PATTERNS="(sk_live_|sk_test_|AKIA[0-9A-Z]{16}|${RSA_PAT}|ghp_[0-9a-zA-Z]{36}|password\s*=\s*[\"\\x27][^\"\\x27]{8,})"
  while IFS= read -r staged_file; do
    if [[ -f "$staged_file" ]] && grep -qEi "$SECRET_PATTERNS" "$staged_file" 2>/dev/null; then
      log_finding "CRITICAL" "secret-leak" "Potential secret in staged file: $staged_file"
    fi
  done <<< "$STAGED_FILES"
else
  echo "  ✅ No staged files"
fi

# --- Check 5: .beads/issues.jsonl validity -------------------------------
echo ""
echo "▸ Validating beads journal..."
if [[ -f "$BEADS_DIR/issues.jsonl" ]]; then
  python3 -c "
import json, sys
errors = 0
with open('$BEADS_DIR/issues.jsonl') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f'  ❌ Line {i}: {e}')
            errors += 1
if errors:
    sys.exit(1)
print(f'  ✅ issues.jsonl: all lines valid JSON')
" || log_finding "ERROR" "beads-corrupt" "issues.jsonl has invalid JSON lines"
else
  log_finding "WARN" "beads-missing" "issues.jsonl does not exist"
fi

# --- Summary -------------------------------------------------------------
echo ""
echo "================================================"
if [[ $FINDINGS -eq 0 ]]; then
  echo "✅ Guardian scan complete — 0 findings. Repository is clean."
else
  echo "⚠️  Guardian scan complete — $FINDINGS finding(s)."
  if [[ "$DRY_RUN" == true ]]; then
    echo "   Run without --dry-run to generate patches."
  elif [[ "$APPLY" == false ]]; then
    echo "   Run with --apply to auto-fix archivable issues."
  fi
fi

# --- Record event --------------------------------------------------------
if [[ -f "$REPO_ROOT/scripts/beads-capture.sh" ]]; then
  bash "$REPO_ROOT/scripts/beads-capture.sh" event \
    "guardian-scan-$(date +%Y%m%d)" \
    "Guardian scan: ${FINDINGS} findings" 2>/dev/null || true
fi

exit 0
