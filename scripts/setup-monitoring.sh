#!/bin/bash
# Setup monitoring and alerting for pnkln orchestrator

set -e

PROJECT_ID="${1:-your-project-id}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setting up monitoring for pnkln orchestrator"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Enable required APIs
echo "📦 Enabling Monitoring APIs..."
gcloud services enable \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudtrace.googleapis.com \
  cloudprofiler.googleapis.com \
  --project="$PROJECT_ID"

# Create notification channel (email)
echo "📧 Creating notification channel..."
read -p "Enter email for alerts: " EMAIL

CHANNEL_ID=$(gcloud alpha monitoring channels create \
  --display-name="Pnkln Ops Team" \
  --type=email \
  --channel-labels=email_address="$EMAIL" \
  --project="$PROJECT_ID" \
  --format="value(name)")

echo "Created notification channel: $CHANNEL_ID"

# Update alert policies with channel ID
echo "🔔 Creating alert policies..."
for alert_file in monitoring/alerts/*.yaml; do
  echo "Creating alert from $alert_file..."

  # Replace placeholder with actual channel ID
  sed "s|# - \"projects/PROJECT_ID/notificationChannels/CHANNEL_ID\"|  - \"$CHANNEL_ID\"|g" "$alert_file" > /tmp/alert.yaml

  gcloud alpha monitoring policies create \
    --policy-from-file=/tmp/alert.yaml \
    --project="$PROJECT_ID" || echo "Alert may already exist"
done

# Create dashboard
echo "📊 Creating monitoring dashboard..."
gcloud monitoring dashboards create \
  --config-from-file=monitoring/dashboards/pnkln-overview.json \
  --project="$PROJECT_ID" || echo "Dashboard may already exist"

# Setup log-based metrics
echo "📝 Creating log-based metrics..."

# Metric: Total requests
gcloud logging metrics create pnkln_log_requests \
  --description="Total requests from logs" \
  --log-filter='resource.type="k8s_pod"
    resource.labels.namespace_name="pnkln-production"
    jsonPayload.message=~"HTTP request"' \
  --project="$PROJECT_ID" || echo "Metric may already exist"

# Metric: Errors
gcloud logging metrics create pnkln_log_errors \
  --description="Error count from logs" \
  --log-filter='resource.type="k8s_pod"
    resource.labels.namespace_name="pnkln-production"
    severity>=ERROR' \
  --project="$PROJECT_ID" || echo "Metric may already exist"

# Create uptime check
echo "🔍 Creating uptime check..."
gcloud monitoring uptime create \
  --display-name="Pnkln Orchestrator Health" \
  --resource-type="uptime-url" \
  --http-check-path="/health" \
  --port=443 \
  --check-interval=60s \
  --timeout=10s \
  --project="$PROJECT_ID" || echo "Uptime check may already exist"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Monitoring setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View your dashboard:"
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo ""
echo "View alerts:"
echo "https://console.cloud.google.com/monitoring/alerting?project=$PROJECT_ID"
