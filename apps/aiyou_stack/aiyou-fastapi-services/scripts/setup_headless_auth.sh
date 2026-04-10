#!/bin/bash
set -e

# CONFIG
PROJECT_ID="shadowtag-omega-v2"
SA_NAME="shadowtag-robot"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="secrets/robot_key.json"

echo ">>> 🤖 SETTING UP HEADLESS AUTHENTICATION..."

# 1. Create Service Account (if not exists)
if gcloud iam service-accounts describe $SA_EMAIL --project $PROJECT_ID &>/dev/null; then
    echo "✓ Service Account $SA_NAME exists."
else
    echo "Creating Service Account $SA_NAME..."
    gcloud iam service-accounts create $SA_NAME \
        --display-name="ShadowTag Robot (Headless Auth)" \
        --project $PROJECT_ID
fi

# 2. Grant Permissions (Owner for "God Mode" access in this context, or refine)
# Using 'Editor' + specific roles is safer, but user is in 'YOLO Mode'.
echo "Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/editor" \
    --condition=None --quiet > /dev/null

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.admin" \
    --condition=None --quiet > /dev/null

# 3. Generate Key
echo "Generating JSON Key..."
if [ -f "$KEY_FILE" ]; then
    echo "⚠️  Key file already exists at $KEY_FILE. Skipping generation to avoid rotation."
else
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=$SA_EMAIL \
        --project $PROJECT_ID
    echo "✓ Key saved to $KEY_FILE"
fi

echo ">>> ✅ HEADLESS AUTH READY."
echo "The system will now use this key instead of asking for browser login."
