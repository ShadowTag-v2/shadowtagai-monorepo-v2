#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# ANTIGRAVITY OS: GITHUB_TOKEN SCOPE AUDIT (P0 Security Contract)
# Scans all CI workflows for overly permissive GITHUB_TOKEN usage.
# Validates that no workflow requests `permissions: write-all` or
# uses `${{ secrets.GITHUB_TOKEN }}` in contexts that leak scope.
#
# Contract: tool_contracts/github_app.workflow_token.yaml
# Risk: Token leakage, supply chain compromise
# ------------------------------------------------------------------------------
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKFLOW_DIR="$REPO_ROOT/.github/workflows"
VIOLATIONS=0
WARNINGS=0

echo "═══ GITHUB_TOKEN Scope Audit ═══"

if [ ! -d "$WORKFLOW_DIR" ]; then
  echo "  ⚠️  No .github/workflows/ directory found"
  exit 0
fi

# Audit 1: Check for write-all permissions (dangerous)
echo "  [1/5] Scanning for 'permissions: write-all'..."
WRITE_ALL=$(grep -rn 'write-all' "$WORKFLOW_DIR" 2>/dev/null | grep -v '#' || true)
if [ -n "$WRITE_ALL" ]; then
  echo "  ✗ CRITICAL: write-all permissions detected:"
  echo "$WRITE_ALL" | while IFS= read -r line; do
    echo "      $line"
  done
  VIOLATIONS=$((VIOLATIONS + 1))
else
  echo "  ✓ No write-all permissions"
fi

# Audit 2: Check each workflow has explicit permissions block
echo "  [2/5] Verifying explicit permissions declarations..."
WORKFLOW_COUNT=0
MISSING_PERMS=0
for wf in "$WORKFLOW_DIR"/*.yml; do
  [ -f "$wf" ] || continue
  WORKFLOW_COUNT=$((WORKFLOW_COUNT + 1))
  WF_NAME=$(basename "$wf")
  if ! grep -q '^permissions:' "$wf" 2>/dev/null; then
    echo "  ⚠️  $WF_NAME — missing top-level permissions block"
    MISSING_PERMS=$((MISSING_PERMS + 1))
    WARNINGS=$((WARNINGS + 1))
  fi
done
echo "  ✓ $WORKFLOW_COUNT workflows scanned, $MISSING_PERMS missing permissions"

# Audit 3: Check for secrets.GITHUB_TOKEN in curl/wget calls (potential exfiltration)
echo "  [3/5] Scanning for token usage in HTTP requests..."
TOKEN_IN_CURL=$(grep -rn 'secrets.GITHUB_TOKEN' "$WORKFLOW_DIR" 2>/dev/null \
  | grep -iE 'curl|wget|fetch|http' \
  | grep -v '#' \
  || true)
if [ -n "$TOKEN_IN_CURL" ]; then
  echo "  ⚠️  GITHUB_TOKEN used in HTTP calls:"
  echo "$TOKEN_IN_CURL" | while IFS= read -r line; do
    echo "      $line"
  done
  WARNINGS=$((WARNINGS + 1))
else
  echo "  ✓ No token leakage in HTTP calls"
fi

# Audit 4: Check for excessive write permissions
echo "  [4/5] Auditing write permission scope..."
WRITE_PERMS=$(grep -rn 'write' "$WORKFLOW_DIR" 2>/dev/null \
  | grep -v 'write-all' \
  | grep -v '#' \
  | grep 'permissions' -A 10 \
  || true)
WRITE_COUNT=$(echo "$WRITE_PERMS" | grep -c 'write' 2>/dev/null || echo "0")
echo "  ✓ Found $WRITE_COUNT write permission declarations across workflows"

# Audit 5: Verify our workflows use 'contents: read' (principle of least privilege)
echo "  [5/5] Verifying least-privilege defaults..."
LEAST_PRIV=$(grep -l 'contents: read' "$WORKFLOW_DIR"/*.yml 2>/dev/null | wc -l | tr -d ' ')
echo "  ✓ $LEAST_PRIV/$WORKFLOW_COUNT workflows use 'contents: read'"

echo ""
if [ "$VIOLATIONS" -gt 0 ]; then
  echo "✗ GITHUB_TOKEN Scope Audit FAILED — $VIOLATIONS violation(s), $WARNINGS warning(s)"
  exit 1
else
  echo "✅ GITHUB_TOKEN Scope Audit PASSED — $VIOLATIONS violations, $WARNINGS warning(s)"
  exit 0
fi
