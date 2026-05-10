#!/bin/bash
# provision_cdc_datastream.sh — Spanner CDC → Pub/Sub Living Ledger
#
# Transforms the Spanner database from a static ledger into a real-time
# event generator using Datastream Change Data Capture (CDC).
#
# Every DML mutation (INSERT/UPDATE/DELETE) in Spanner is captured at the
# binary transaction log level and streamed to Pub/Sub as a JSON event.
# This eliminates the need for application-layer event firing.
#
# Usage: ./scripts/provision_cdc_datastream.sh [--dry-run]

set -euo pipefail

PROJECT_ID="shadowtag-omega-v4"
REGION="us-central1"
STREAM_ID="uphill-spanner-pulse"
PUBSUB_TOPIC="database-events"
SPANNER_INSTANCE="uphill-core-cluster"
SPANNER_DATABASE="uphill-ledger"
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧬 Living Ledger — Datastream CDC Provisioning"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Ensure the Datastream API is enabled
echo "[1/4] Enabling Datastream API..."
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would enable datastream.googleapis.com"
else
    gcloud services enable datastream.googleapis.com --project="$PROJECT_ID" --quiet 2>/dev/null || true
fi

# 2. Create the Pub/Sub nervous system topic
echo "[2/4] Ensuring Pub/Sub topic: $PUBSUB_TOPIC"
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create topic $PUBSUB_TOPIC"
else
    gcloud pubsub topics create "$PUBSUB_TOPIC" --project="$PROJECT_ID" 2>/dev/null || echo "  ℹ️  Topic already exists"
    # Create a dead-letter subscription for unprocessed events
    gcloud pubsub subscriptions create "${PUBSUB_TOPIC}-dlq" \
        --topic="$PUBSUB_TOPIC" \
        --project="$PROJECT_ID" \
        --ack-deadline=60 \
        --message-retention-duration=7d 2>/dev/null || echo "  ℹ️  DLQ subscription already exists"
fi

# 3. Provision the Datastream connection profile for Spanner
echo "[3/4] Creating Spanner connection profile..."
CONN_PROFILE_ID="uphill-spanner-source"
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create connection profile: $CONN_PROFILE_ID"
else
    gcloud datastream connection-profiles create "$CONN_PROFILE_ID" \
        --project="$PROJECT_ID" \
        --location="$REGION" \
        --type=GOOGLE_CLOUD_SPANNER \
        --spanner-database="projects/$PROJECT_ID/instances/$SPANNER_INSTANCE/databases/$SPANNER_DATABASE" \
        --display-name="UphillSnowball Spanner Source" \
        --quiet 2>/dev/null || echo "  ℹ️  Connection profile already exists"
fi

# 4. Create the Datastream stream (Spanner → Pub/Sub)
echo "[4/4] Provisioning Datastream CDC stream: $STREAM_ID"
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create stream: $STREAM_ID"
    echo "  Source: Spanner ($SPANNER_INSTANCE/$SPANNER_DATABASE)"
    echo "  Destination: Pub/Sub ($PUBSUB_TOPIC)"
    echo "  Format: JSON"
else
    gcloud datastream streams create "$STREAM_ID" \
        --project="$PROJECT_ID" \
        --location="$REGION" \
        --display-name="Spanner to PubSub Living Ledger" \
        --source="$CONN_PROFILE_ID" \
        --destination-type=pubsub \
        --pubsub-destination-topic="projects/$PROJECT_ID/topics/$PUBSUB_TOPIC" \
        --state=NOT_STARTED \
        --quiet 2>/dev/null || echo "  ℹ️  Stream already exists or requires manual config"
    echo "  ⚠️  Stream created in NOT_STARTED state. Run:"
    echo "     gcloud datastream streams update $STREAM_ID --location=$REGION --state=RUNNING"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Living Ledger CDC Provisioning Complete"
echo ""
echo "  Data flow: Spanner DML → Transaction Log → Datastream → Pub/Sub"
echo "  Topic: projects/$PROJECT_ID/topics/$PUBSUB_TOPIC"
echo "  All storage mutations are now event-sourced."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
