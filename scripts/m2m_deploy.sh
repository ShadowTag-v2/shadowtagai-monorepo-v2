#!/bin/bash
# M2M Firebase Deploy Script
export CI=true
export DEBIAN_FRONTEND=noninteractive
export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.config/gcloud/application_default_credentials.json"

echo "Initializing Firebase MCP M2M Deployment..."
# Layer 2 Auth Bypass for Headless
npm i -g firebase-tools

echo "Deploying KovelAI & ShadowTagAI..."
firebase deploy --only hosting:kovelai --project shadowtag-omega-v4 --non-interactive
firebase deploy --only hosting:shadowtagai --project shadowtag-omega-v4 --non-interactive

echo "Deployment complete."
