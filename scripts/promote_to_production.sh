#!/usr/bin/env bash
# promote_to_production.sh — Staging → Production Promotion
# Usage: ./scripts/promote_to_production.sh [--skip-tests] [--canary-pct 10]
set -euo pipefail

PROJECT="shadowtag-omega-v4"
REGION="us-central1"
STAGING_URL="https://counselconduit-staging-767252945109.us-central1.run.app"
PROD_URL="https://counselconduit-767252945109.us-central1.run.app"
CANARY_PCT="${2:-10}"

echo "╔══════════════════════════════════════════╗"
echo "║  CounselConduit Promotion Pipeline       ║"
echo "╚══════════════════════════════════════════╝"

# Step 1: Run regression on staging
if [[ "${1:-}" != "--skip-tests" ]]; then
  echo "[1/6] Running regression tests on staging..."
  CC_STAGING_URL="$STAGING_URL" python3 -m pytest apps/counselconduit/tests/test_regression.py -q --tb=short
  echo "  ✅ Staging regression passed"

  echo "[2/6] Running chaos tests..."
  python3 -m pytest apps/counselconduit/tests/test_chaos.py -q --tb=short
  echo "  ✅ Chaos tests passed"
else
  echo "[1-2/6] Skipping tests (--skip-tests)"
fi

# Step 3: Deploy canary
echo "[3/6] Deploying canary (0% traffic)..."
gcloud run deploy counselconduit \
  --project="$PROJECT" --region="$REGION" \
  --source=apps/counselconduit \
  --service-account=counselconduit-sa@${PROJECT}.iam.gserviceaccount.com \
  --set-env-vars="APP_ENV=production" \
  --no-traffic --tag=canary --quiet

# Step 4: Health check canary
CANARY_URL=$(gcloud run services describe counselconduit \
  --project="$PROJECT" --region="$REGION" \
  --format='value(status.traffic[tag=canary].url)')
echo "[4/6] Health checking canary at $CANARY_URL..."
HEALTH=$(curl -s "$CANARY_URL/health" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','unknown'))")
if [[ "$HEALTH" != "healthy" ]]; then
  echo "  ❌ Canary health check failed: $HEALTH"
  exit 1
fi
echo "  ✅ Canary healthy"

# Step 5: Split traffic
echo "[5/6] Splitting ${CANARY_PCT}% traffic to canary..."
gcloud run services update-traffic counselconduit \
  --project="$PROJECT" --region="$REGION" \
  --to-tags=canary="$CANARY_PCT" --quiet
echo "  ✅ Traffic split: $((100-CANARY_PCT))% stable / ${CANARY_PCT}% canary"
echo "  ⏳ Monitor for 5 minutes..."
sleep 300

# Step 6: Promote to 100%
echo "[6/6] Promoting canary to 100%..."
gcloud run services update-traffic counselconduit \
  --project="$PROJECT" --region="$REGION" \
  --to-latest=100 --quiet

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ Production Promotion Complete        ║"
echo "╚══════════════════════════════════════════╝"

# Run production regression
echo "Running production regression..."
CC_STAGING_URL="$PROD_URL" python3 -m pytest apps/counselconduit/tests/test_regression.py -q --tb=short
echo "  ✅ Production regression passed"
