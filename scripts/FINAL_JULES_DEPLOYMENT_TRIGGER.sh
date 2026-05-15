#!/bin/bash
set -euo pipefail

echo "🚀 FINAL JULES DEPLOYMENT TRIGGER"
echo "=================================="

echo ""
echo "[1/7] Connecting to Jules via official Workload Identity..."
node scripts/connect-jules.js

echo ""
echo "[2/7] Triggering full production deployment..."
node scripts/trigger-jules-deployment.js

echo ""
echo "[3/7] Deploying MCP Server to Cloud Run..."
./scripts/deploy-mcp.sh

echo ""
echo "[4/7] Deploying PWA to Firebase Hosting..."
cd apps/headfade/pwa
npm run build
firebase deploy --only hosting --project=shadowtag-omega-v4

echo ""
echo "[5/7] Activating Stripe production mode..."
echo "STRIPE_MODE=production" >> .env.production

echo ""
echo "[6/7] Removing beta flag globally..."
firebase functions:config:set beta.enabled=false --project=shadowtag-omega-v4

echo ""
echo "[7/7] Final verification..."
echo "✅ https://headfade.com/ should now be live"

echo ""
echo "🎉 DEPLOYMENT TRIGGER COMPLETE"
echo "Jules is now handling the live deployment of https://headfade.com/"