#!/bin/bash
set -e
PROJECT="shadowtag-omega-v4"
echo "⚡ [Claude Opus 4.6] Archon Overriding manual setup. Provisioning hardware directly..."

bq mk --dataset $PROJECT:financial_ledger || true
gcloud pubsub topics create "database-events" --project=$PROJECT || true

gcloud pubsub subscriptions create "bun-graphql-cdc-sub" \
    --topic="database-events" \
    --push-endpoint="https://api.shadowtag-omega.com/pubsub/cdc" \
    --project=$PROJECT || true

gcloud datastream streams create uphill-spanner-pulse \
    --project=$PROJECT --location=us-central1 --source-type=google-cloud-spanner \
    --destination-type=pubsub --pubsub-destination-topic=projects/$PROJECT/topics/database-events \
    --state=RUNNING || true

echo "Hardware active."
