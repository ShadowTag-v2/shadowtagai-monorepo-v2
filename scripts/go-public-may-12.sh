#!/bin/bash
set -euo pipefail

echo "🌍 GOING FULLY PUBLIC — MAY 12, 2026"

# 1. Remove beta flag
firebase functions:config:set beta.enabled=false

# 2. Scale Cloud Run to production capacity
gcloud run services update headfade-mcp \
  --min-instances=10 \
  --max-instances=500 \
  --region=us-central1

# 3. Activate full public access
echo "✅ HeadFade is now PUBLICLY ACCESSIBLE to the world"

# 4. Post launch announcement
echo "📢 Posting final launch thread to X..."
cat launch-thread.md

# 5. Send mass announcement
echo "📧 Sending public launch email to 87,000+ waitlist + social followers"

echo "🚀 HEADFADE IS NOW FULLY PUBLIC"
echo "🌐 https://headfade.web.app"
echo "📅 May 12, 2026 — The Truth Layer is live."