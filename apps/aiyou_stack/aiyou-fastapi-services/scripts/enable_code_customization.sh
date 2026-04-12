#!/bin/bash
set -e

# Antigravity: Enable Gemini Code Assist "Code Customization"
# Usage: ./scripts/enable_code_customization.sh

PROJECT_ID="acquired-jet-478701-b3"
REGION="us-central1"
REPO_NAME="ShadowTag-v2-fastapi-services"
REPO_URI="https://github.com/ShadowTag-v2/ShadowTag-v2-fastapi-services.git"

echo "///▞ ANTIGRAVITY :: Enabling Code Customization for $PROJECT_ID"

# 1. Enable Required APIs
echo "///▞ STEP 1: Enabling APIs..."
gcloud services enable \
    cloudaicompanion.googleapis.com \
    discoveryengine.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --project="$PROJECT_ID"

# 2. Grant Permissions to the Gemini Service Agent
# This allows Gemini to access the Data Store we are about to create
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_AGENT="service-$PROJECT_NUMBER@gcp-sa-cloudaicompanion.iam.gserviceaccount.com"

echo "///▞ STEP 2: Granting IAM roles to $SERVICE_AGENT..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_AGENT" \
    --role="roles/discoveryengine.admin" \
    --condition=None

# 3. Create Vertex AI Search Data Store (for Code)
# Note: This often requires the Console for the initial "Link Repo" step if not using Developer Connect.
# We will attempt to create the engine if it doesn't exist.

DATA_STORE_ID="antigravity-code-index"

echo "///▞ STEP 3: Checking Data Store..."
if gcloud discovery-engine data-stores list --project="$PROJECT_ID" --location=global | grep -q "$DATA_STORE_ID"; then
    echo "///▞ Data Store '$DATA_STORE_ID' already exists."
else
    echo "///▞ Creating Data Store '$DATA_STORE_ID'..."
    # Note: CLI creation of code-specific data stores is complex and often requires
    # linking a specific GitHub installation ID.
    # We will output instructions for the final link.

    echo "!!! ACTION REQUIRED !!!"
    echo "To finalize the Code Customization index, you must link your GitHub repo."
    echo "Run this command to open the console directly to the setup page:"
    echo "open 'https://console.cloud.google.com/gen-ai/code-repository-index?project=$PROJECT_ID'"
fi

# 4. Configure Gemini Code Assist to use this Data Store
# This is the "Group" setting in the console.

echo "///▞ STEP 4: Configuration Instructions"
echo "1. Go to: https://console.cloud.google.com/gen-ai/code-repository-index?project=$PROJECT_ID"
echo "2. Click 'Create Index'"
echo "3. Select 'GitHub' and choose '$REPO_NAME'"
echo "4. Wait for indexing to complete (usually 10-15 mins)"
echo "5. Restart VS Code to see the '@' context picker populated."

echo "///▞ ANTIGRAVITY :: Setup script complete."
