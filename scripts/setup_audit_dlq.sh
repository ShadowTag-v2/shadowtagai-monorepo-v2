#!/bin/bash
# Setup Audit DLQ Infrastructure
# Creates Pub/Sub topics, subscriptions, and DLQ routing

set -euo pipefail

echo "Setting up Audit DLQ Infrastructure..."

PROJECT_ID="${GCP_PROJECT_ID:-acquired-jet-478701-b3}"
REGION="us-central1"

# Topic names
MAIN_TOPIC="audit-trace-events"
DLQ_TOPIC="audit-trace-dlq"

# Subscription names
MAIN_SUB="audit-trace-sub"
DLQ_SUB="audit-trace-dlq-sub"

# Max delivery attempts before DLQ
MAX_DELIVERY_ATTEMPTS=5

echo "Project: $PROJECT_ID"
echo "Main Topic: $MAIN_TOPIC"
echo "DLQ Topic: $DLQ_TOPIC"
echo ""

# 1. Create the Main Topic (if not exists)
echo "Creating main topic: $MAIN_TOPIC"
gcloud pubsub topics create $MAIN_TOPIC --project=$PROJECT_ID 2>/dev/null || echo "  -> Topic already exists"

# 2. Create the Dead Letter Topic ("The Morgue")
echo "Creating DLQ topic: $DLQ_TOPIC"
gcloud pubsub topics create $DLQ_TOPIC --project=$PROJECT_ID 2>/dev/null || echo "  -> Topic already exists"

# 3. Create DLQ subscription (to inspect failures)
echo "Creating DLQ subscription: $DLQ_SUB"
gcloud pubsub subscriptions create $DLQ_SUB \
    --topic=$DLQ_TOPIC \
    --project=$PROJECT_ID \
    --ack-deadline=60 \
    --message-retention-duration=7d \
    2>/dev/null || echo "  -> Subscription already exists"

# 4. Create Main Subscription with Dead Letter Policy
echo "Creating main subscription with DLQ routing: $MAIN_SUB"

# First, check if subscription exists
if gcloud pubsub subscriptions describe $MAIN_SUB --project=$PROJECT_ID &>/dev/null; then
    echo "  -> Subscription exists, updating DLQ policy..."
    gcloud pubsub subscriptions update $MAIN_SUB \
        --project=$PROJECT_ID \
        --dead-letter-topic=$DLQ_TOPIC \
        --max-delivery-attempts=$MAX_DELIVERY_ATTEMPTS
else
    echo "  -> Creating new subscription with DLQ..."
    gcloud pubsub subscriptions create $MAIN_SUB \
        --topic=$MAIN_TOPIC \
        --project=$PROJECT_ID \
        --dead-letter-topic=$DLQ_TOPIC \
        --max-delivery-attempts=$MAX_DELIVERY_ATTEMPTS \
        --ack-deadline=60 \
        --message-retention-duration=7d
fi

# 5. Grant Pub/Sub service account permissions on DLQ
echo ""
echo "Granting DLQ permissions..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
PUBSUB_SA="service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com"

gcloud pubsub topics add-iam-policy-binding $DLQ_TOPIC \
    --project=$PROJECT_ID \
    --member="serviceAccount:$PUBSUB_SA" \
    --role="roles/pubsub.publisher" \
    --quiet 2>/dev/null || echo "  -> Permission already granted"

gcloud pubsub subscriptions add-iam-policy-binding $MAIN_SUB \
    --project=$PROJECT_ID \
    --member="serviceAccount:$PUBSUB_SA" \
    --role="roles/pubsub.subscriber" \
    --quiet 2>/dev/null || echo "  -> Permission already granted"

# 6. Create GCS bucket for audit storage (if not exists)
AUDIT_BUCKET="shadowtagai-audit-traces"
echo ""
echo "Creating audit storage bucket: $AUDIT_BUCKET"
gsutil mb -p $PROJECT_ID -l $REGION gs://$AUDIT_BUCKET 2>/dev/null || echo "  -> Bucket already exists"

# Set lifecycle policy (retain for 7 years for compliance)
echo "Setting retention policy (7 years)..."
cat > /tmp/lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 2555}
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/lifecycle.json gs://$AUDIT_BUCKET 2>/dev/null || true

# 7. Summary
echo ""
echo "=============================================="
echo "DLQ Infrastructure Setup Complete!"
echo "=============================================="
echo ""
echo "Main Topic:       $MAIN_TOPIC"
echo "DLQ Topic:        $DLQ_TOPIC"
echo "Main Subscription: $MAIN_SUB (max $MAX_DELIVERY_ATTEMPTS attempts)"
echo "DLQ Subscription:  $DLQ_SUB"
echo "Audit Bucket:      gs://$AUDIT_BUCKET"
echo ""
echo "Usage:"
echo "  # Publish audit event"
echo "  python -m app.pubsub.audit_publisher"
echo ""
echo "  # Start worker"
echo "  python -m app.pubsub.audit_worker"
echo ""
echo "  # Inspect DLQ (The Coroner)"
echo "  python -m app.pubsub.dlq_inspector"
echo ""
echo "Monitoring:"
echo "  # Create alert for DLQ > 0 messages"
echo "  gcloud alpha monitoring policies create --policy-from-file=dlq_alert.yaml"
