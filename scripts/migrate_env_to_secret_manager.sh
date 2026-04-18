#!/usr/bin/env bash
# scripts/migrate_env_to_secret_manager.sh
# Reads secrets from local .env and creates them in Secret Manager.
# Usage: bash scripts/migrate_env_to_secret_manager.sh

set -euo pipefail

PROJECT="shadowtag-omega-v4"
GCLOUD="/opt/homebrew/share/google-cloud-sdk/bin/gcloud"
ENV_FILE=".env"

# Pairs: ENV_VAR_NAME SECRET_MANAGER_NAME
PAIRS=(
  "STRIPE_SECRET_KEY stripe-secret-key"
  "STRIPE_WEBHOOK_SECRET stripe-webhook-secret"
  "STRIPE_PUBLISHABLE_KEY stripe-publishable-key"
  "DISCORD_WEBHOOK_URL discord-webhook-url"
  "RESEND_API_KEY resend-api-key"
  "STITCH_API_KEY stitch-api-key"
)

# Unlock .env temporarily
echo "🔓 Unlocking .env..."
chflags nouchg "$ENV_FILE" 2>/dev/null || true

echo "📦 Reading .env and creating secrets in Secret Manager..."
echo ""

for PAIR in "${PAIRS[@]}"; do
  ENV_VAR=$(echo "$PAIR" | awk '{print $1}')
  SECRET_NAME=$(echo "$PAIR" | awk '{print $2}')

  # Extract value from .env
  VALUE=$(grep "^${ENV_VAR}=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d'=' -f2- | sed "s/^[\"']//;s/[\"']$//")

  if [[ -z "$VALUE" || "$VALUE" == "sk_test_..." || "$VALUE" == "whsec_..." || "$VALUE" == "re_..." ]]; then
    echo "⏭️  $ENV_VAR — empty or placeholder, skipping"
    continue
  fi

  # Check if secret already exists
  if $GCLOUD secrets describe "$SECRET_NAME" --project="$PROJECT" &>/dev/null; then
    echo "🔄 $SECRET_NAME — exists, adding new version"
    echo -n "$VALUE" | $GCLOUD secrets versions add "$SECRET_NAME" \
      --project="$PROJECT" --data-file=-
  else
    echo "✨ Creating $SECRET_NAME"
    echo -n "$VALUE" | $GCLOUD secrets create "$SECRET_NAME" \
      --project="$PROJECT" \
      --replication-policy="automatic" \
      --data-file=-
  fi
done

# Re-lock .env
echo ""
echo "🔒 Re-locking .env..."
chflags uchg "$ENV_FILE" 2>/dev/null || true

echo ""
echo "✅ Done. Verify with:"
echo "  $GCLOUD secrets list --project=$PROJECT"
echo ""
echo "Next: mount in Cloud Run with --set-secrets"
