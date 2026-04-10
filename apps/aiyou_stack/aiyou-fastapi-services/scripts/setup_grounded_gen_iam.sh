#!/bin/bash
set -e

# Configuration
PROJECT_ID="acquired-jet-478701-b3"
SERVICE_ACCOUNT_NAME="grounded-gen-sa"
DISPLAY_NAME="Grounded Generation Service Account"
KEY_FILE="grounded-gen-sa-key.json"

echo "--- Setting up IAM for Grounded Generation ---"
echo "Project ID: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_NAME"

# 1. Enable APIs
echo "Enabling necessary APIs..."
gcloud services enable discoveryengine.googleapis.com --project "$PROJECT_ID"
gcloud services enable aiplatform.googleapis.com --project "$PROJECT_ID"
gcloud services enable iamcredentials.googleapis.com --project "$PROJECT_ID"

# 2. Create Service Account
if gcloud iam service-accounts describe "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --project "$PROJECT_ID" > /dev/null 2>&1; then
    echo "Service account ${SERVICE_ACCOUNT_NAME} already exists."
else
    echo "Creating service account..."
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name "$DISPLAY_NAME" \
        --project "$PROJECT_ID"
fi

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Service Account Email: $SA_EMAIL"

# 3. Assign Roles
echo "Assigning roles..."
# Discovery Engine User (for search/grounding)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/discoveryengine.editor"

# Vertex AI User (for model access)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"

# 4. Generate Key (Optional, as requested by user)
echo "Generating JSON key file..."
if [ -f "$KEY_FILE" ]; then
    echo "Key file $KEY_FILE already exists. Skipping generation."
else
    gcloud iam service-accounts keys create "$KEY_FILE" \
        --iam-account="$SA_EMAIL" \
        --project="$PROJECT_ID"
    echo "Key saved to $KEY_FILE"
fi

echo "--- Setup Complete ---"
echo "To use the key, set the environment variable:"
echo "export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/$KEY_FILE"
