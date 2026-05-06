#!/usr/bin/env bash
# scripts/validate_env.sh
# Validates that .env contains all required keys for local development.
# Usage: bash scripts/validate_env.sh

set -euo pipefail

ENV_FILE=".env"
ERRORS=0

echo "🔍 Validating .env..."
echo "====================="

# Required keys
REQUIRED=(
  "GCP_PROJECT_ID"
  "DEVELOPER_KNOWLEDGE_API_KEY"
  "GEMINI_API_KEY"
  "STITCH_API_KEY"
  "DISABLE_TELEMETRY"
)

# Optional (warn if missing)
OPTIONAL=(
  "STRIPE_SECRET_KEY"
  "STRIPE_WEBHOOK_SECRET"
  "STRIPE_PUBLISHABLE_KEY"
  "TEMPORAL_HOST"
  "KVCACHED_PORT"
  "NANO_BANANA_2_MODEL"
)

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ .env file not found at $ENV_FILE"
  exit 1
fi

# Check uchg lock
if ls -lO "$ENV_FILE" 2>/dev/null | grep -q "uchg"; then
  echo "🔒 Kernel lock: ACTIVE (uchg)"
else
  echo "⚠️  Kernel lock: NOT ACTIVE — run 'chflags uchg .env'"
fi

# Validate required
for key in "${REQUIRED[@]}"; do
  value=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- || true)
  if [ -z "$value" ]; then
    echo "❌ MISSING: $key (REQUIRED)"
    ERRORS=$((ERRORS + 1))
  elif echo "$value" | grep -qi "PASTE\|YOUR_\|REPLACE\|TODO"; then
    echo "❌ PLACEHOLDER: $key (still has placeholder value)"
    ERRORS=$((ERRORS + 1))
  else
    echo "✅ $key"
  fi
done

echo ""

# Validate optional
for key in "${OPTIONAL[@]}"; do
  value=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- || true)
  if [ -z "$value" ]; then
    echo "⚠️  MISSING: $key (optional)"
  elif echo "$value" | grep -qi "PASTE\|YOUR_\|REPLACE\|TODO"; then
    echo "⚠️  PLACEHOLDER: $key"
  else
    echo "✅ $key"
  fi
done

echo ""
echo "====================="
if [ "$ERRORS" -gt 0 ]; then
  echo "❌ $ERRORS required key(s) missing or invalid"
  exit 1
else
  echo "✅ All required keys present and valid"
fi
