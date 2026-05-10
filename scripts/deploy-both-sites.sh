#!/bin/bash
set -e

echo "🚀 Deploying KovelAI to kovelai.com..."
CI=true firebase deploy --only hosting:kovelai --project=shadowtag-omega-v4

echo ""
echo "🚀 Deploying ShadowTag AI to shadowtagai.com..."
CI=true firebase deploy --only hosting:shadowtagai --project=shadowtag-omega-v4

echo ""
echo "🔍 Verifying deployments..."

echo ""
echo "=== KovelAI (kovelai.com) ==="
curl -I https://kovelai.com

echo ""
echo "=== ShadowTag AI (shadowtagai.com) ==="
curl -I https://shadowtagai.com

echo ""
echo "✅ Both sites deployed and verified successfully."
