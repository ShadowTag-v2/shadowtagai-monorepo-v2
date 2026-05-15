#!/bin/bash

# Configuration
ROLE="roles/cloudaicompanion.user"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

# Fallback if project ID is missing
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Could not determine current Google Cloud Project ID."
    echo "Please run: gcloud config set project <PROJECT_ID>"
    exit 1
fi

echo "🚀 Starting Gemini Enterprise Seat Provisioning"
echo "Target Project: $PROJECT_ID"
echo "Target Role:    $ROLE"
echo "------------------------------------------------"

# List of users to provision (Seats 3 through 10)
USERS=(
    "ehanc6903@gmail.com"
    "ehanc6904@gmail.com"
    "ehanc6905@gmail.com"
    "ehanc6906@gmail.com"
    "ehanc6907@gmail.com"
    "ehanc6908@gmail.com"
    "ehanc6909@gmail.com"
    "ehanc6910@gmail.com"
)

# Loop and Provision
for user in "${USERS[@]}"; do
    echo "👉 Granting license to: $user"

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="user:$user" \
        --role="$ROLE" \
        --condition=None \
        --quiet

    if [ $? -eq 0 ]; then
        echo "   ✅ Success"
    else
        echo "   ❌ Failed to add $user"
    fi
done

echo "------------------------------------------------"
echo "🎉 Provisioning Complete."
echo "Verify quotas at: https://console.cloud.google.com/iam-admin/iam"
