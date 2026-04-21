# CounselConduit — Canary Deployment Strategy

## Item #12: Canary Deployment for Future Revisions

### Strategy

Cloud Run native traffic splitting enables zero-downtime canary deployment.

### Deployment Flow

```
1. Deploy new revision (no traffic):
   gcloud run deploy counselconduit --no-traffic --tag=canary [...]

2. Route 5% traffic to canary:
   gcloud run services update-traffic counselconduit \
     --to-tags=canary=5 --region=us-central1

3. Monitor for 15 minutes:
   - Check error rates in Cloud Monitoring dashboard
   - Check latency p95 in dashboard
   - Check circuit breaker status

4. Scale to 25%, then 50%, then 100%:
   gcloud run services update-traffic counselconduit \
     --to-tags=canary=25 --region=us-central1
   # Wait 15 min, verify, then:
   gcloud run services update-traffic counselconduit \
     --to-tags=canary=100 --region=us-central1

5. Rollback if needed (instant):
   gcloud run services update-traffic counselconduit \
     --to-tags=canary=0 --region=us-central1
```

### Automated Canary Script

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT="shadowtag-omega-v4"
SERVICE="counselconduit"
REGION="us-central1"
TAG="canary"

echo "🚀 Deploying canary revision..."
gcloud run deploy $SERVICE --no-traffic --tag=$TAG \
  --source=apps/counselconduit \
  --region=$REGION --project=$PROJECT --quiet

echo "🐤 Routing 5% to canary..."
gcloud run services update-traffic $SERVICE \
  --to-tags=$TAG=5 --region=$REGION --project=$PROJECT --quiet

echo "⏱  Monitoring for 15 minutes..."
sleep 900

# Check health of canary
CANARY_URL="https://${TAG}---${SERVICE}-767252945109.${REGION}.run.app/health"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $CANARY_URL)

if [ "$STATUS" != "200" ]; then
  echo "❌ Canary failed! Rolling back..."
  gcloud run services update-traffic $SERVICE \
    --to-tags=$TAG=0 --region=$REGION --project=$PROJECT --quiet
  exit 1
fi

echo "✅ Canary healthy. Promoting to 100%..."
gcloud run services update-traffic $SERVICE \
  --to-tags=$TAG=100 --region=$REGION --project=$PROJECT --quiet

echo "🎉 Canary promoted successfully."
```

### Rollback SLA

| Metric | Target |
|--------|--------|
| Detection | < 5 minutes (via alert policies) |
| Rollback execution | < 30 seconds (traffic split) |
| Full recovery | < 2 minutes |

### Canary Criteria

- Error rate must stay < 1% (vs baseline)
- p95 latency must stay < 3 seconds
- No circuit breaker trips
- All smoke tests pass against canary URL
