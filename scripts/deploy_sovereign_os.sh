#!/bin/bash
# deploy_sovereign_os.sh — Deploy all Sovereign OS services to Cloud Run
#
# Deploys:
#   1. database-events-handler (CDC event subscriber)
#   2. finops-governor (Economic circuit breaker)
#   3. sovereign-orchestrator (Autonomous pipeline brain)
#
# Also provisions:
#   - Pub/Sub topics and push subscriptions
#   - Cloud Scheduler cron for FinOps (hourly)
#
# Usage: ./scripts/deploy_sovereign_os.sh [--dry-run]
# Prerequisites: Run provision_cdc_datastream.sh first

set -euo pipefail

PROJECT_ID="shadowtag-omega-v4"
REGION="us-central1"
SA="counselconduit-sa@${PROJECT_ID}.iam.gserviceaccount.com"
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
    esac
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🏭 Dark Factory — Sovereign OS Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ─── 1. Pub/Sub Topics ──────────────────────────────────────────────────────

echo ""
echo "[1/7] Ensuring Pub/Sub topics..."
TOPICS=(
    "database-events"
    "schema-healing-requests"
    "finops-checks"
    "finops-alerts"
    "payment-reconciliation"
    "epistemic-events"
)

for topic in "${TOPICS[@]}"; do
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would create topic: $topic"
    else
        gcloud pubsub topics create "$topic" --project="$PROJECT_ID" 2>/dev/null \
            || echo "  ℹ️  Topic $topic already exists"
    fi
done

# ─── 2. Deploy database-events-handler ──────────────────────────────────────

echo ""
echo "[2/7] Deploying database-events-handler..."
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would deploy database-events-handler"
else
    gcloud run deploy database-events-handler \
        --source=services/database-events-handler \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --service-account="$SA" \
        --set-env-vars="GCP_PROJECT=${PROJECT_ID},BIGQUERY_DATASET=uphill_events,HEALING_TOPIC=schema-healing-requests,FINOPS_TOPIC=finops-checks" \
        --no-allow-unauthenticated \
        --memory=512Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=10 \
        --quiet
fi

# ─── 3. Deploy finops-governor ──────────────────────────────────────────────

echo ""
echo "[3/7] Deploying finops-governor..."
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would deploy finops-governor"
else
    gcloud run deploy finops-governor \
        --source=services/finops-governor \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --service-account="$SA" \
        --set-env-vars="GCP_PROJECT=${PROJECT_ID},BUDGET_MONTHLY_USD=500,WARN_PCT=80,HALT_PCT=100" \
        --no-allow-unauthenticated \
        --memory=256Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=3 \
        --quiet
fi

# ─── 4. Deploy sovereign-orchestrator ──────────────────────────────────────

echo ""
echo "[4/7] Deploying sovereign-orchestrator..."
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would deploy sovereign-orchestrator"
else
    gcloud run deploy sovereign-orchestrator \
        --source=services/sovereign-orchestrator \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --service-account="$SA" \
        --set-env-vars="GCP_PROJECT=${PROJECT_ID},SPANNER_INSTANCE=uphill-core-cluster,SPANNER_DATABASE=uphill-ledger,MEMORY_TOPIC=epistemic-events" \
        --no-allow-unauthenticated \
        --memory=512Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=5 \
        --timeout=120 \
        --quiet
fi

# ─── 5. Pub/Sub Push Subscriptions ─────────────────────────────────────────

echo ""
echo "[5/7] Wiring Pub/Sub push subscriptions..."

# Get service URLs
if [ "$DRY_RUN" = false ]; then
    CDC_URL=$(gcloud run services describe database-events-handler --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)' 2>/dev/null || echo "UNKNOWN")
    FINOPS_URL=$(gcloud run services describe finops-governor --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)' 2>/dev/null || echo "UNKNOWN")
    ORCH_URL=$(gcloud run services describe sovereign-orchestrator --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)' 2>/dev/null || echo "UNKNOWN")
else
    CDC_URL="https://database-events-handler-HASH.run.app"
    FINOPS_URL="https://finops-governor-HASH.run.app"
    ORCH_URL="https://sovereign-orchestrator-HASH.run.app"
fi

# database-events → database-events-handler
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create push subscription: database-events → $CDC_URL"
else
    gcloud pubsub subscriptions create database-events-push \
        --topic=database-events \
        --push-endpoint="$CDC_URL" \
        --push-auth-service-account="$SA" \
        --ack-deadline=30 \
        --project="$PROJECT_ID" 2>/dev/null \
        || echo "  ℹ️  Subscription database-events-push already exists"
fi

# schema-healing-requests → sovereign-orchestrator
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create push subscription: schema-healing-requests → $ORCH_URL"
else
    gcloud pubsub subscriptions create healing-push \
        --topic=schema-healing-requests \
        --push-endpoint="$ORCH_URL" \
        --push-auth-service-account="$SA" \
        --ack-deadline=60 \
        --project="$PROJECT_ID" 2>/dev/null \
        || echo "  ℹ️  Subscription healing-push already exists"
fi

# finops-checks → finops-governor
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create push subscription: finops-checks → $FINOPS_URL"
else
    gcloud pubsub subscriptions create finops-push \
        --topic=finops-checks \
        --push-endpoint="$FINOPS_URL" \
        --push-auth-service-account="$SA" \
        --ack-deadline=30 \
        --project="$PROJECT_ID" 2>/dev/null \
        || echo "  ℹ️  Subscription finops-push already exists"
fi

# ─── 6. Cloud Scheduler Cron (FinOps Hourly) ──────────────────────────────

echo ""
echo "[6/7] Setting up Cloud Scheduler cron for FinOps Governor..."
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would create hourly scheduler job"
else
    gcloud scheduler jobs create http finops-hourly-check \
        --location="$REGION" \
        --schedule="0 * * * *" \
        --uri="$FINOPS_URL" \
        --http-method=POST \
        --oidc-service-account-email="$SA" \
        --project="$PROJECT_ID" 2>/dev/null \
        || echo "  ℹ️  Scheduler job already exists"
fi

# ─── 7. Verification ──────────────────────────────────────────────────────

echo ""
echo "[7/7] Verifying deployment..."
if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would verify all 3 services are running"
else
    echo "  Services:"
    gcloud run services list --region="$REGION" --project="$PROJECT_ID" \
        --filter="metadata.name:(database-events-handler OR finops-governor OR sovereign-orchestrator)" \
        --format="table(metadata.name, status.url, status.conditions.status)" 2>/dev/null \
        || echo "  ⚠️  Could not list services"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Dark Factory Deployment Complete"
echo ""
echo "  Data flow:"
echo "    Spanner DML → Datastream CDC → Pub/Sub"
echo "    → database-events-handler → {BigQuery, Healing, Payment, FinOps}"
echo "    → sovereign-orchestrator → {Diagnose, Budget Check, Heal, Document}"
echo "    → finops-governor → {Scale Down | Alert | OK}"
echo ""
echo "  Cron: FinOps Governor runs hourly via Cloud Scheduler"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
