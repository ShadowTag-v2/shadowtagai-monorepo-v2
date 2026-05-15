#!/bin/bash
# Setup GCP Secret Manager for ShadowTag v2
# Usage: ./scripts/setup_gcp_secrets.sh <project-id> <secret-name> <private-key>

set -euo pipefail

PROJECT_ID="${1:-}"
SECRET_NAME="${2:-blockchain-private-key}"
PRIVATE_KEY="${3:-}"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID required"
    echo "Usage: $0 <project-id> [secret-name] [private-key]"
    exit 1
fi

echo "=== GCP Secret Manager Setup for ShadowTag v2 ==="
echo "Project: $PROJECT_ID"
echo "Secret: $SECRET_NAME"
echo ""

# Enable Secret Manager API
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID"

# Create secret if it doesn't exist
if ! gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" &>/dev/null; then
    echo "Creating secret: $SECRET_NAME"
    gcloud secrets create "$SECRET_NAME" \
        --replication-policy="automatic" \
        --project="$PROJECT_ID"
else
    echo "Secret $SECRET_NAME already exists"
fi

# Add secret version if private key provided
if [ -n "$PRIVATE_KEY" ]; then
    echo "Adding secret version..."
    echo -n "$PRIVATE_KEY" | gcloud secrets versions add "$SECRET_NAME" \
        --data-file=- \
        --project="$PROJECT_ID"
    echo "✅ Secret version added"
else
    echo "⚠️  No private key provided. Add manually with:"
    echo "   echo -n 'YOUR_PRIVATE_KEY' | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID"
fi

# Grant access to service account (example)
echo ""
echo "To grant access to a service account:"
echo "  gcloud secrets add-iam-policy-binding $SECRET_NAME \\"
echo "    --member='serviceAccount:YOUR_SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com' \\"
echo "    --role='roles/secretmanager.secretAccessor' \\"
echo "    --project='$PROJECT_ID'"

echo ""
echo "✅ GCP Secret Manager setup complete!"
