#!/bin/bash
# Uploads the generated DID key to GCP Secret Manager
# Usage: ./upload_did_keys.sh <project_id>

PROJECT_ID=${1:-"shadowtag-omega-v4"}
SECRET_NAME="agent-did-private-key"
KEY_FILE="keys/agent_did_ed25519"

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file $KEY_FILE not found. Run python3 scripts/generate_did_keys.py first."
    exit 1
fi

echo "Creating secret $SECRET_NAME in project $PROJECT_ID..."
gcloud secrets create $SECRET_NAME \
    --replication-policy="automatic" \
    --project="$PROJECT_ID" || echo "Secret may already exist, proceeding to add version..."

echo "Adding secret version from $KEY_FILE..."
gcloud secrets versions add $SECRET_NAME --data-file="$KEY_FILE" --project="$PROJECT_ID"

echo "Done."
