#!/usr/bin/env bash
# ==============================================================================
# PRE-PUSH EGRESS SCAN — Secret Leakage Prevention (Invariant #115)
#
# Scans staged diff for potential secret leakage patterns before push.
# Uses pattern matching as a lightweight complement to betterleaks full scan.
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

echo "  Scanning HEAD commit diff for potential secrets..."

# Patterns that indicate secret leakage in diff content
PATTERNS=(
  'PRIVATE KEY'
  'BEGIN RSA'
  'BEGIN EC PRIVATE'
  'BEGIN DSA'
  'sk-[a-zA-Z0-9]{20,}'
  'ghp_[a-zA-Z0-9]{36}'
  'ghs_[a-zA-Z0-9]{36}'
  'AIza[a-zA-Z0-9_-]{35}'
  'ya29\.[a-zA-Z0-9_-]{50,}'
  'AKIA[A-Z0-9]{16}'
  'password\s*[:=]\s*["\x27][^"\x27]{8,}'
)

VIOLATIONS=0

# Check the most recent commit diff
DIFF_CONTENT=$(git diff HEAD~1..HEAD -- . ':(exclude)*.lock' ':(exclude)*.sum' ':(exclude)vendor/' ':(exclude)node_modules/' 2>/dev/null || echo "")

if [ -z "$DIFF_CONTENT" ]; then
  echo "  ✓ No diff to scan (initial commit or no changes)"
  exit 0
fi

for pattern in "${PATTERNS[@]}"; do
  MATCHES=$(echo "$DIFF_CONTENT" | grep -cE "$pattern" 2>/dev/null || true)
  # Strip non-digits (newlines, spaces) to get a clean integer
  MATCHES=$(echo "$MATCHES" | tr -cd '0-9')
  MATCHES="${MATCHES:-0}"
  if [ "$MATCHES" -gt 0 ]; then
    echo "  ⚠️  Pattern match: $pattern ($MATCHES occurrences)"
    VIOLATIONS=$((VIOLATIONS + MATCHES))
  fi
done

if [ "$VIOLATIONS" -gt 0 ]; then
  echo ""
  echo "  ❌ EGRESS SCAN FAILED: $VIOLATIONS potential secret patterns detected"
  echo "  Review with: git diff HEAD~1..HEAD | grep -P '<pattern>'"
  echo ""
  echo "  If these are false positives, add fingerprints to .gitleaksignore"
  exit 1
fi

echo "  ✓ Egress scan clean — 0 secret patterns detected"
