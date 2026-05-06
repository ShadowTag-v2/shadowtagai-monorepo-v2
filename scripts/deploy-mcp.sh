#!/bin/bash
set -euo pipefail

echo "🚀 Deploying HeadFade Truth Oracle MCP Server..."

cd antigravity-core/mcp
npm run build

gcloud run deploy headfade-mcp \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="NODE_ENV=production" \
  --service-account=headfade-mcp-sa@shadowtag-omega-v4.iam.gserviceaccount.com

echo "✅ MCP Server deployed successfully"
