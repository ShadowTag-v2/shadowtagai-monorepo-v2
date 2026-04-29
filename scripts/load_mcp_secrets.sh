#!/usr/bin/env bash
# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Proprietary
#
# load_mcp_secrets.sh — Fetches MCP server secrets from GCP Secret Manager
# and exports them as environment variables.
#
# Usage:
#   source scripts/load_mcp_secrets.sh
#   # or
#   eval "$(scripts/load_mcp_secrets.sh --export)"
#
# Prerequisites:
#   - gcloud CLI authenticated (gcloud auth login)
#   - roles/secretmanager.secretAccessor on the service account
#
# This replaces the deprecated .env file. All secrets are canonical in
# GCP Secret Manager (project: shadowtag-omega-v4).

set -eo pipefail

readonly PROJECT_ID="shadowtag-omega-v4"

_log() {
  if [ "${QUIET:-}" != "1" ]; then
    printf "[load_mcp_secrets] %s\n" "$1" >&2
  fi
}

_fail() {
  printf "[load_mcp_secrets] ERROR: %s\n" "$1" >&2
  return 1
}

# --- Non-secret project configuration (formerly in .env) ---
export GOOGLE_CLOUD_PROJECT="shadowtag-omega-v4"
export GCLOUD_PROJECT="shadowtag-omega-v4"
export FIREBASE_PROJECT_ID="shadowtag-omega-v4"
export GOOGLE_CLOUD_REGION="us-central1"
export VERTEX_PROJECT="shadowtag-omega-v4"
export VERTEX_LOCATION="us-central1"
export DISABLE_TELEMETRY="1"
export DISABLE_ERROR_REPORTING="1"
export ALLOW_ANT_COMPUTER_USE_MCP="1"
_log "Exported 9 config vars"

# --- Verify gcloud auth ---
if ! gcloud auth print-access-token --quiet >/dev/null 2>&1; then
  _fail "gcloud not authenticated. Run: gcloud auth login"
fi

# --- Fetch secrets from Secret Manager ---
# Format: ENV_VAR_NAME:secret-manager-id
SECRETS="
DEVELOPER_KNOWLEDGE_API_KEY:developer-knowledge-api-key
STITCH_API_KEY:stitch-api-key
GOOGLE_DESIGN_API_KEY:google-design-api-key
GEMINI_API_KEY:gemini-api-key
STRIPE_SECRET_KEY:stripe-secret-key
STRIPE_PUBLISHABLE_KEY:stripe-publishable-key
STRIPE_WEBHOOK_SECRET:stripe-webhook-secret
KOVEL_ATTESTATION_SECRET:KOVEL_ATTESTATION_SECRET
MAGIC_LINK_SECRET:MAGIC_LINK_SECRET
"

loaded=0
failed=0
total=0

for entry in $SECRETS; do
  [ -z "$entry" ] && continue
  total=$((total + 1))
  var_name="${entry%%:*}"
  secret_id="${entry#*:}"

  value=$(gcloud secrets versions access latest \
    --secret="$secret_id" \
    --project="$PROJECT_ID" 2>/dev/null) || {
    _log "WARN: Failed to fetch ${secret_id} — skipping"
    failed=$((failed + 1))
    continue
  }

  export "${var_name}=${value}"
  loaded=$((loaded + 1))
done

_log "Loaded ${loaded}/${total} secrets from Secret Manager (${failed} failed)"

# --- --export flag: print for eval usage ---
if [ "${1:-}" = "--export" ]; then
  echo "export GOOGLE_CLOUD_PROJECT=\"shadowtag-omega-v4\""
  echo "export GCLOUD_PROJECT=\"shadowtag-omega-v4\""
  echo "export FIREBASE_PROJECT_ID=\"shadowtag-omega-v4\""
  echo "export GOOGLE_CLOUD_REGION=\"us-central1\""
  echo "export VERTEX_PROJECT=\"shadowtag-omega-v4\""
  echo "export VERTEX_LOCATION=\"us-central1\""
  echo "export DISABLE_TELEMETRY=\"1\""
  echo "export DISABLE_ERROR_REPORTING=\"1\""
  echo "export ALLOW_ANT_COMPUTER_USE_MCP=\"1\""

  for entry in $SECRETS; do
    [ -z "$entry" ] && continue
    var_name="${entry%%:*}"
    val=$(eval "echo \"\${${var_name}:-}\"")
    if [ -n "$val" ]; then
      echo "export ${var_name}=\"${val}\""
    fi
  done
fi
