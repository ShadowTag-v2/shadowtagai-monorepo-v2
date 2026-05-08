#!/bin/bash
set -euo pipefail

# ============================================
# HEADFADE MCP - PRODUCTION DEPLOYMENT SCRIPT
# ============================================

PROJECT_ID="shadowtag-omega-v4"
SERVICE_NAME="headfade-mcp"
REGION="us-central1"
SERVICE_ACCOUNT="headfade-mcp-sa@shadowtag-omega-v4.iam.gserviceaccount.com"

echo "🚀 Deploying hardened HeadFade MCP to production..."

# ============================================
# 1. SET REQUIRED SECRETS
# ============================================

echo "📦 Ensuring secrets exist in Secret Manager..."

# Create secrets if they don't exist
gcloud secrets describe STRIPE_SECRET_KEY --project=$PROJECT_ID >/dev/null 2>&1 || \
  gcloud secrets create STRIPE_SECRET_KEY --project=$PROJECT_ID

gcloud secrets describe STRIPE_WEBHOOK_SECRET --project=$PROJECT_ID >/dev/null 2>&1 || \
  gcloud secrets create STRIPE_WEBHOOK_SECRET --project=$PROJECT_ID

gcloud secrets describe SENTRY_DSN --project=$PROJECT_ID >/dev/null 2>&1 || \
  gcloud secrets create SENTRY_DSN --project=$PROJECT_ID

# ============================================
# 2. DEPLOY TO CLOUD RUN
# ============================================

echo "☁️  Deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --project $PROJECT_ID \
  --service-account $SERVICE_ACCOUNT \
  --allow-unauthenticated \
  --set-env-vars="NODE_ENV=production,PORT=8080" \
  --set-secrets="STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,STRIPE_WEBHOOK_SECRET=STRIPE_WEBHOOK_SECRET:latest,SENTRY_DSN=SENTRY_DSN:latest" \
  --min-instances=25 \
  --max-instances=500 \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300s \
  --concurrency=80

echo "✅ Deployment complete!"

# ============================================
# 3. VERIFY DEPLOYMENT
# ============================================

echo "🔍 Verifying deployment..."

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format="value(status.url)")

echo "🌐 Service URL: $SERVICE_URL"

# Health check
echo "🏥 Running health check..."
curl -s "$SERVICE_URL/health" | jq .

# Metrics check
echo "📊 Checking metrics endpoint..."
curl -s "$SERVICE_URL/metrics" | head -20

echo ""
echo "🎉 HeadFade MCP is now live at: $SERVICE_URL"
echo "   Health: $SERVICE_URL/health"
echo "   Metrics: $SERVICE_URL/metrics"
```