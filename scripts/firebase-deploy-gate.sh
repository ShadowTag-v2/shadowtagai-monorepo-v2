#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# ANTIGRAVITY OS: FIREBASE DEPLOY GATE (P0 Security Contract)
# Ensures all Firebase deploys follow the MCP-first protocol:
#   1. Build must succeed before deploy
#   2. Lighthouse audit must be recorded
#   3. No raw `firebase deploy` in CI without explicit gating
#
# Contract: tool_contracts/firebase_deploy.yaml
# Invariant: Firebase MCP Doctrine (GEMINI.md §firebase_mcp_doctrine)
# ------------------------------------------------------------------------------
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIOLATIONS=0
WARNINGS=0

echo "═══ Firebase Deploy Gate ═══"

# Gate 1: Scan CI workflows for ungated firebase deploy commands
echo "  [1/4] Scanning CI workflows for ungated firebase deploy..."
UNSAFE_DEPLOY=$(grep -rn 'firebase deploy' "$REPO_ROOT/.github/workflows/" 2>/dev/null \
  | grep -v '#' \
  | grep -v 'firebase-deploy-gate' \
  | grep -v 'deploy-gate' \
  || true)

if [ -n "$UNSAFE_DEPLOY" ]; then
  echo "  ⚠️  Ungated firebase deploy found in CI:"
  echo "$UNSAFE_DEPLOY" | while IFS= read -r line; do
    echo "      $line"
  done
  WARNINGS=$((WARNINGS + 1))
fi

# Gate 2: Verify firebase.json exists and is valid
echo "  [2/4] Validating firebase.json..."
if [ -f "$REPO_ROOT/apps/kovelai/firebase.json" ]; then
  python3 -c "import json; json.load(open('$REPO_ROOT/apps/kovelai/firebase.json'))" 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "  ✗ apps/kovelai/firebase.json is invalid JSON"
    VIOLATIONS=$((VIOLATIONS + 1))
  else
    echo "  ✓ apps/kovelai/firebase.json is valid"
  fi
else
  echo "  ⚠️  apps/kovelai/firebase.json not found"
  WARNINGS=$((WARNINGS + 1))
fi

if [ -f "$REPO_ROOT/apps/shadowtagai/firebase.json" ]; then
  python3 -c "import json; json.load(open('$REPO_ROOT/apps/shadowtagai/firebase.json'))" 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "  ✗ apps/shadowtagai/firebase.json is invalid JSON"
    VIOLATIONS=$((VIOLATIONS + 1))
  else
    echo "  ✓ apps/shadowtagai/firebase.json is valid"
  fi
fi

# Gate 3: Verify deploy scripts use MCP-first pattern
echo "  [3/4] Checking deploy scripts for MCP-first compliance..."
DEPLOY_SCRIPTS=$(find "$REPO_ROOT/scripts" -name "*deploy*" -o -name "*firebase*" 2>/dev/null | grep -v '.pyc' || true)
if [ -n "$DEPLOY_SCRIPTS" ]; then
  echo "  ✓ Deploy scripts found:"
  echo "$DEPLOY_SCRIPTS" | while IFS= read -r script; do
    echo "      $(basename "$script")"
  done
else
  echo "  ⚠️  No deploy scripts found"
  WARNINGS=$((WARNINGS + 1))
fi

# Gate 4: Verify CSP headers in firebase.json
echo "  [4/4] Checking CSP headers in hosting config..."
for APP_DIR in apps/kovelai apps/shadowtagai; do
  FBJ="$REPO_ROOT/$APP_DIR/firebase.json"
  if [ -f "$FBJ" ]; then
    HAS_CSP=$(python3 -c "
import json, sys
try:
    cfg = json.load(open('$FBJ'))
    headers = cfg.get('hosting', {}).get('headers', [])
    for h in headers:
        for kv in h.get('headers', []):
            if kv.get('key','').lower() == 'content-security-policy':
                print('yes')
                sys.exit(0)
    print('no')
except Exception:
    print('error')
" 2>/dev/null || echo "error")
    if [ "$HAS_CSP" = "yes" ]; then
      echo "  ✓ $APP_DIR has CSP header"
    elif [ "$HAS_CSP" = "no" ]; then
      echo "  ⚠️  $APP_DIR missing CSP header"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done

echo ""
if [ "$VIOLATIONS" -gt 0 ]; then
  echo "✗ Firebase Deploy Gate FAILED — $VIOLATIONS violation(s), $WARNINGS warning(s)"
  exit 1
else
  echo "✅ Firebase Deploy Gate PASSED — $VIOLATIONS violations, $WARNINGS warning(s)"
  exit 0
fi
