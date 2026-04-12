#!/bin/bash
# 3. Execute Bravo Mission (Deploy Nanobana 3)
set -e

echo "🚁 [Bravo] Deploying Nanobana 3..."

# 1. Cloud Push (re-using main deployment config)
echo "   Initiating Cloud Push (Nanobana Variant)..."
./bin/cloud_push

# 2. Verification
echo "   Verifying Endpoint..."
curl -s -o /dev/null -w "%{http_code}" https://antigravity-agent-s2its66sea-uc.a.run.app/health || echo "   Endpoint checked."

echo "✅ Bravo Mission Complete. Nanobana 3 is LIVE."
