#!/usr/bin/env bash
# scripts/upload_secrets_to_gcp.sh
# Uploads secrets from .env to GCP Secret Manager for Cloud Run consumption.
# Usage: bash scripts/upload_secrets_to_gcp.sh
# Requires: gcloud with active auth, project set to shadowtag-omega-v4

set -euo pipefail

PROJECT="shadowtag-omega-v4"
ENV_FILE=".env"

echo "🔐 Uploading secrets to GCP Secret Manager (project: $PROJECT)"
echo "================================================================="

# Secrets that need to go to Secret Manager for Cloud Run
declare -A SECRETS=(
  ["stripe-secret-key"]="STRIPE_SECRET_KEY"
  ["stripe-webhook-secret"]="STRIPE_WEBHOOK_SECRET"
  ["stripe-publishable-key"]="STRIPE_PUBLISHABLE_KEY"
  ["gemini-api-key"]="GEMINI_API_KEY"
  ["stitch-api-key"]="STITCH_API_KEY"
  ["developer-knowledge-api-key"]="DEVELOPER_KNOWLEDGE_API_KEY"
)

for secret_name in "${!SECRETS[@]}"; do
  env_var="${SECRETS[$secret_name]}"
  value=$(grep "^${env_var}=" "$ENV_FILE" | cut -d'=' -f2-)
  
  if [ -z "$value" ]; then
    echo "⏭️  Skipping $secret_name ($env_var not found in .env)"
    continue
  fi
  
  # Create or update secret
  if gcloud secrets describe "$secret_name" --project="$PROJECT" &>/dev/null; then
    echo "$value" | gcloud secrets versions add "$secret_name" \
      --project="$PROJECT" --data-file=- 2>/dev/null
    echo "✅ Updated: $secret_name"
  else
    echo "$value" | gcloud secrets create "$secret_name" \
      --project="$PROJECT" --data-file=- \
      --replication-policy="automatic" 2>/dev/null
    echo "✅ Created: $secret_name"
  fi
done

echo ""
echo "================================================================="
echo "Now grant the Cloud Run SA access:"
echo "  gcloud projects add-iam-policy-binding $PROJECT \\"
echo "    --member='serviceAccount:counselconduit-sa@$PROJECT.iam.gserviceaccount.com' \\"
echo "    --role='roles/secretmanager.secretAccessor'"
echo ""
echo "Done. Secrets are ready for Cloud Run env var references."
