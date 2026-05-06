#!/bin/bash
set -euo pipefail

echo "🚀 Deploying HeadFade Truth Oracle MCP Server..."

# 1. Build
cd antigravity-core/mcp
npm run build

# 2. Deploy to Cloud Run (example)
gcloud run deploy headfade-mcp \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="NODE_ENV=production" \
  --max-instances=200 \
  --service-account=headfade-mcp-sa@PROJECT_ID.iam.gserviceaccount.com

echo "✅ MCP Server deployed successfully"
echo "Endpoint: https://headfade-mcp-[hash]-uc.a.run.app"