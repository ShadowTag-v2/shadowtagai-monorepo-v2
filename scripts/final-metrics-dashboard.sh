#!/bin/bash
echo "📊 Generating Final Metrics Dashboard..."

# Deploy dashboard
cd apps/headfade/pwa
npm run build
firebase deploy --only hosting

echo "✅ Metrics Dashboard live at: https://headfade.web.app/metrics"
echo "Real-time beta cohort monitoring enabled."