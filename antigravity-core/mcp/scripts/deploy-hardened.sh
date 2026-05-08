#!/bin/bash
set -e

echo "Deploying hardened MCP server to Cloud Run..."
gcloud run deploy headfade-mcp \
  --source . \
  --region us-central1 \
  --project=shadowtag-omega-v4 \
  --allow-unauthenticated

echo "Deployment complete. Checking health..."
