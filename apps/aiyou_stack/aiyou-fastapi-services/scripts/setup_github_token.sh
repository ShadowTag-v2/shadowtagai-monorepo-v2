#!/bin/bash
set -e

SECRET_ID="dataform-github-token"
PROJECT_ID="shadowtag-omega-v2"

echo ">>> 🔐 SETTING UP GITHUB AUTH FOR KAFKA/DATAFORM..."

# 1. Try to get token from gh CLI
if command -v gh &> /dev/null; then
    echo "Check gh auth status..."
    if gh auth status &> /dev/null; then
        echo "✓ GitHub CLI is authenticated."
        TOKEN=$(gh auth token)
    else
        echo "⚠️  GitHub CLI not authenticated. Please run 'gh auth login' first."
        exit 1
    fi
else
    echo "❌ 'gh' CLI not found. Please install it or manually update the secret."
    exit 1
fi

if [ -z "$TOKEN" ]; then
    echo "❌ Could not fetch token."
    exit 1
fi

# 2. Upload to Secret Manager
echo "Upload token to Secret Manager ($SECRET_ID)..."
printf "%s" "$TOKEN" | gcloud secrets versions add $SECRET_ID --data-file=- --project $PROJECT_ID

echo ">>> ✅ SUCCESS. The Sovereign Brain can now pull your code."
