#!/bin/bash
# finish_deployment.sh

PROJECT_ID="acquired-jet-478701-b3"
REGION="us-central1"
SERVICE="ShadowTag-v2-fastapi-service"
DOMAIN="api.shadowtagai.com"

echo "🚀 Monitoring Deployment for $SERVICE..."

# 1. Wait for Cloud Run Service to be ready
while true; do
  URL=$(gcloud run services describe $SERVICE --region $REGION --project $PROJECT_ID --format='value(status.url)' 2>/dev/null)
  if [ ! -z "$URL" ]; then
    echo "✅ Service Deployed at: $URL"
    break
  fi
  echo "⏳ Build still in progress... waiting 30s"
  sleep 30
done

# 2. Map Custom Domain
echo "🔗 Mapping domain: $DOMAIN"
gcloud beta run domain-mappings create \
  --service $SERVICE \
  --domain $DOMAIN \
  --region $REGION \
  --project $PROJECT_ID \
  --quiet

# 3. Output DNS Instructions
echo "---------------------------------------------------"
echo "✅ Mapped! Now update your DNS records at your registrar:"
echo "   Type:  CNAME"
echo "   Name:  api"
echo "   Value: ghs.googlehosted.com."
echo "---------------------------------------------------"
