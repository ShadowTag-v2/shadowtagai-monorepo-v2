#!/bin/bash
# cloud_nuke.sh - The Cloud Run Kill Switch
# IMMEDIATE SCALING TO ZERO for all Agent Services

PROJECT_ID="acquired-jet-478701-b3"
REGION="us-central1"

echo "🚨 ACTIVATING CLOUD KILL CHAIN for Project: $PROJECT_ID..."

# 1. Scale Cloud Run Services to Zero
echo "📉 Scaling Down Cloud Run Services..."
gcloud run services list --project="$PROJECT_ID" --format="value(SERVICE)" | while read SERVICE; do
    if [[ "$SERVICE" == *"n-autoresearch/Kosmos/BioAgents"* ]] || [[ "$SERVICE" == *"genkit"* ]] || [[ "$SERVICE" == *"shadowtag"* ]]; then
        echo "   ❄️ Freezing $SERVICE..."
        gcloud run services update "$SERVICE" \
            --project="$PROJECT_ID" \
            --region="$REGION" \
            --min-instances=0 \
            --max-instances=0 \
            --async
    fi
done

# 2. Purge Pub/Sub Queues (Stop the flow of tasks)
echo "🧹 Purging Task Queues..."
gcloud pubsub subscriptions list --project="$PROJECT_ID" --format="value(SUBSCRIPTION)" | while read SUB; do
    if [[ "$SUB" == *"agent-tasks"* ]]; then
        echo "   Emptying $SUB..."
        gcloud pubsub subscriptions seek "$SUB" --time=$(date +%Y-%m-%dT%H:%M:%S) --project="$PROJECT_ID"
    fi
done

echo "✅ CLOUD KILL CHAIN INITIATED. Services scaling to zero."
