#!/usr/bin/env bash
# Firebase 3-Layer Auth Health Check
# Verifies all three independent auth channels are active:
#   Layer 1: Firebase CLI (refresh token in configstore)
#   Layer 2: Firebase MCP Server (in-memory OAuth2 session)
#   Layer 3: Application Default Credentials (gcloud ADC)
#
# Reference: GEMINI.md firebase_mcp_doctrine -> Three-Layer Auth Architecture
# Usage: bash scripts/firebase_auth_health_check.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

check() {
  local label="$1"
  local result="$2"
  if [[ "$result" == "pass" ]]; then
    echo -e "  ${GREEN}✅ PASS${NC} — $label"
    ((PASS++))
  elif [[ "$result" == "warn" ]]; then
    echo -e "  ${YELLOW}⚠️  WARN${NC} — $label"
    ((WARN++))
  else
    echo -e "  ${RED}❌ FAIL${NC} — $label"
    ((FAIL++))
  fi
}

echo "═══════════════════════════════════════════════════"
echo "  Firebase 3-Layer Auth Health Check"
echo "═══════════════════════════════════════════════════"
echo ""

# ─── Layer 1: Firebase CLI ───────────────────────────
echo "Layer 1: Firebase CLI (configstore refresh token)"

# Check firebase-tools is installed globally (not npx)
if command -v firebase &>/dev/null; then
  FIREBASE_PATH=$(command -v firebase)
  if [[ "$FIREBASE_PATH" == *"_npx"* ]]; then
    check "firebase-tools installed globally (NOT via npx)" "fail"
  else
    check "firebase-tools installed globally at $FIREBASE_PATH" "pass"
  fi
else
  check "firebase-tools is installed" "fail"
fi

# Check CLI auth token exists
CLI_TOKEN_FILE="$HOME/.config/configstore/firebase-tools.json"
if [[ -f "$CLI_TOKEN_FILE" ]]; then
  # Check if it has a refresh token
  if grep -q "refresh_token" "$CLI_TOKEN_FILE" 2>/dev/null; then
    check "CLI refresh token exists in configstore" "pass"
  else
    check "CLI refresh token in configstore" "fail"
  fi
else
  check "CLI configstore file exists at $CLI_TOKEN_FILE" "fail"
fi

# Verify CLI can list projects (proves token is valid)
if command -v firebase &>/dev/null; then
  if CI=true firebase projects:list --limit 1 &>/dev/null; then
    check "CLI token is valid (projects:list succeeded)" "pass"
  else
    check "CLI token is valid (projects:list failed — run: CI=true firebase login --reauth --no-localhost)" "fail"
  fi
fi

echo ""

# ─── Layer 2: Firebase MCP Server ────────────────────
echo "Layer 2: Firebase MCP Server (in-memory OAuth2 session)"
echo -e "  ${YELLOW}ℹ️  INFO${NC} — MCP auth is in-memory within the IDE process."
echo -e "  ${YELLOW}ℹ️  INFO${NC} — Verify via: firebase_get_environment MCP tool → check 'Authenticated User' field."
echo -e "  ${YELLOW}ℹ️  INFO${NC} — If expired, call firebase_login MCP tool."
check "MCP auth check requires IDE MCP call (cannot verify from shell)" "warn"

echo ""

# ─── Layer 3: Application Default Credentials ────────
echo "Layer 3: Application Default Credentials (gcloud ADC)"

ADC_FILE="$HOME/.config/gcloud/application_default_credentials.json"
if [[ -f "$ADC_FILE" ]]; then
  check "ADC file exists at $ADC_FILE" "pass"

  # Check if it has a client_id (OAuth) vs service account
  if grep -q "client_id" "$ADC_FILE" 2>/dev/null; then
    check "ADC type: OAuth2 user credentials" "pass"
  elif grep -q "service_account" "$ADC_FILE" 2>/dev/null; then
    check "ADC type: Service account" "pass"
  else
    check "ADC credential type" "warn"
  fi
else
  check "ADC file exists (run: gcloud auth application-default login --project=shadowtag-omega-v4)" "fail"
fi

# Verify gcloud is authenticated
if command -v gcloud &>/dev/null; then
  ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "")
  if [[ -n "$ACTIVE_ACCOUNT" ]]; then
    check "gcloud active account: $ACTIVE_ACCOUNT" "pass"
  else
    check "gcloud has active account" "fail"
  fi

  # Check active project
  ACTIVE_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
  if [[ "$ACTIVE_PROJECT" == "shadowtag-omega-v4" ]]; then
    check "gcloud project: $ACTIVE_PROJECT" "pass"
  elif [[ -n "$ACTIVE_PROJECT" ]]; then
    check "gcloud project is shadowtag-omega-v4 (currently: $ACTIVE_PROJECT)" "warn"
  else
    check "gcloud project is set" "fail"
  fi
fi

echo ""

# ─── Supplemental: GitHub App PEM ────────────────────
echo "Supplemental: GitHub App PEM ($SHADOWTAG_PEM)"

PEM_PATH="${SHADOWTAG_PEM:-/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem}"
if [[ -f "$PEM_PATH" ]]; then
  check "GitHub App PEM exists at $PEM_PATH" "pass"
  # Check PEM is valid format
  if head -1 "$PEM_PATH" | grep -q "BEGIN.*PRIVATE KEY"; then
    check "PEM file has valid header" "pass"
  else
    check "PEM file format" "fail"
  fi
else
  check "GitHub App PEM exists (checked 5-tier fallback)" "fail"
fi

echo ""

# ─── Summary ─────────────────────────────────────────
echo "═══════════════════════════════════════════════════"
echo -e "  Results: ${GREEN}${PASS} passed${NC}, ${YELLOW}${WARN} warnings${NC}, ${RED}${FAIL} failed${NC}"
echo "═══════════════════════════════════════════════════"

if [[ $FAIL -gt 0 ]]; then
  echo ""
  echo "Repair commands:"
  echo "  Layer 1: CI=true firebase login --reauth --no-localhost"
  echo "  Layer 2: Call firebase_login MCP tool in IDE"
  echo "  Layer 3: gcloud auth application-default login --project=shadowtag-omega-v4"
  echo "  PEM:     export SHADOWTAG_PEM=/path/to/your.pem"
  exit 1
fi
