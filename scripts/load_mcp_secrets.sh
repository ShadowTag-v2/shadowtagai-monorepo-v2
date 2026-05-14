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

# HeadFade PWA public config
export NEXT_PUBLIC_STRIPE_HEADFADE_PRO_LINK="https://buy.stripe.com/<your-payment-link-id>"
export NEXT_PUBLIC_API_URL="https://headfade-api.run.app"

# KovelAI public config
export NEXT_PUBLIC_STRIPE_TRIAL_LINK="https://buy.stripe.com/<trial-link>"
export NEXT_PUBLIC_STRIPE_PRO_MONTHLY_LINK="https://buy.stripe.com/<monthly-link>"
export NEXT_PUBLIC_STRIPE_PRO_ANNUAL_LINK="https://buy.stripe.com/<annual-link>"

_log "Exported 13 config vars"

# --- Verify gcloud auth ---
if ! gcloud auth print-access-token --quiet >/dev/null 2>&1; then
  _fail "gcloud not authenticated. Run: gcloud auth login"
fi

# --- Fetch secrets from Secret Manager ---
# Format: ENV_VAR_NAME:secret-manager-id
SECRETS="
DEVELOPER_KNOWLEDGE_API_KEY:developer-knowledge-api-key
STITCH_API_KEY:stitch-api-key-regional
GOOGLE_DESIGN_API_KEY:google-design-api-key-regional
GEMINI_API_KEY:gemini-api-key-regional
STRIPE_SECRET_KEY:stripe-secret-key-regional
STRIPE_PUBLISHABLE_KEY:stripe-publishable-key-regional
STRIPE_WEBHOOK_SECRET:stripe-webhook-secret-regional
"

loaded=0
failed=0
total=0

while read -r entry; do
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
done <<< "$SECRETS"

_log "Loaded ${loaded}/${total} secrets from Secret Manager (${failed} failed)"

# --- Python fallback with circuit breaker (for failed secrets) ---
if [ "$failed" -gt 0 ]; then
  _log "Attempting Python fallback with circuit breaker for ${failed} failed secret(s)..."

  # Collect failed secret IDs
  _failed_secrets=""
  while read -r entry; do
    [ -z "$entry" ] && continue
    var_name="${entry%%:*}"
    secret_id="${entry#*:}"
    val=$(eval "echo \"\${${var_name}:-}\"")
    if [ -z "$val" ]; then
      _failed_secrets="${_failed_secrets} ${var_name}:${secret_id}"
    fi
  done <<< "$SECRETS"

  # Python helper: gates Secret Manager calls through the circuit breaker
  _py_fallback_result=$(python3 -c "
import sys, os, json
sys.path.insert(0, '$(cd "$(dirname "$0")/.." && pwd)')

failed_pairs = '${_failed_secrets}'.strip().split()
if not failed_pairs:
    sys.exit(0)

# Lazy circuit breaker init
breaker = None
try:
    from packages.circuit_breaker.telemetry_bridge import default_registry
    breaker = default_registry.get_or_create(
        'secret_manager',
        failure_threshold=3,
        reset_timeout_s=60.0,
    )
except Exception:
    pass  # breaker unavailable — proceed ungated

try:
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
except Exception:
    sys.exit(0)  # SDK unavailable

results = {}
for pair in failed_pairs:
    var_name, secret_id = pair.split(':', 1)
    if breaker is not None and not breaker.allow_request():
        print(f'BREAKER_OPEN:{var_name}', file=sys.stderr)
        continue
    try:
        name = f'projects/${PROJECT_ID}/secrets/{secret_id}/versions/latest'
        response = client.access_secret_version(request={'name': name})
        results[var_name] = response.payload.data.decode('UTF-8')
        if breaker is not None:
            breaker.record_success()
    except Exception as e:
        if breaker is not None:
            breaker.record_failure()
        print(f'FALLBACK_FAIL:{var_name}:{e}', file=sys.stderr)

for k, v in results.items():
    print(f'{k}={v}')
" )

  # Parse Python output and export recovered secrets
  _recovered=0
  while IFS= read -r line; do
    case "$line" in
      BREAKER_OPEN:*|FALLBACK_FAIL:*)
        _log "$line"
        ;;
      *=*)
        _key="${line%%=*}"
        _val="${line#*=}"
        export "${_key}=${_val}"
        _recovered=$((_recovered + 1))
        ;;
    esac
  done <<< "$_py_fallback_result"

  if [ "$_recovered" -gt 0 ]; then
    _log "Python fallback recovered ${_recovered} secret(s) via circuit breaker"
    loaded=$((loaded + _recovered))
    failed=$((failed - _recovered))
  fi
fi

_log "Final: ${loaded}/${total} secrets loaded (${failed} failed)"

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
  echo "export NEXT_PUBLIC_STRIPE_HEADFADE_PRO_LINK=\"https://buy.stripe.com/<your-payment-link-id>\""
  echo "export NEXT_PUBLIC_API_URL=\"https://headfade-api.run.app\""
  echo "export NEXT_PUBLIC_STRIPE_TRIAL_LINK=\"https://buy.stripe.com/<trial-link>\""
  echo "export NEXT_PUBLIC_STRIPE_PRO_MONTHLY_LINK=\"https://buy.stripe.com/<monthly-link>\""
  echo "export NEXT_PUBLIC_STRIPE_PRO_ANNUAL_LINK=\"https://buy.stripe.com/<annual-link>\""

  for entry in $SECRETS; do
    [ -z "$entry" ] && continue
    var_name="${entry%%:*}"
    val=$(eval "echo \"\${${var_name}:-}\"")
    if [ -n "$val" ]; then
      echo "export ${var_name}=\"${val}\""
    fi
  done
fi
