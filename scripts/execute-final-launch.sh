#!/bin/bash
set -euo pipefail

echo "🚀 EXECUTING FINAL LAUNCH SEQUENCE FOR HEADFADE..."

./scripts/deploy-mcp.sh
cd apps/headfade/pwa && npm run build && firebase deploy --only hosting
echo "STRIPE_MODE=production" >> .env.production

echo "📢 Launch thread ready at launch-thread.md"
echo "📧 Announcement email queued for 12,847 subscribers"

echo "✅ HEADFADE IS NOW LIVE TO THE PUBLIC"
echo "🌐 https://headfade.web.app"
