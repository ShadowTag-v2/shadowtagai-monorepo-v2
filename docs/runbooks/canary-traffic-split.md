# Canary Traffic Split for CounselConduit

## Quick Canary Deploy (10% → 100%)

### Step 1: Deploy WITHOUT routing traffic
```bash
gcloud run deploy counselconduit \
  --project=shadowtag-omega-v4 \
  --region=us-central1 \
  --source=apps/counselconduit \
  --service-account=counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com \
  --set-env-vars="APP_ENV=production" \
  --no-traffic \
  --quiet
```

### Step 2: Split traffic (10% canary)
```bash
gcloud run services update-traffic counselconduit \
  --project=shadowtag-omega-v4 \
  --region=us-central1 \
  --to-latest=10
```

### Step 3: Monitor for 15 minutes
- Check Cloud Monitoring dashboard for error rate
- Check staging uptime for latency spikes
- Verify `/health` returns on new revision

### Step 4: Promote to 100%
```bash
gcloud run services update-traffic counselconduit \
  --project=shadowtag-omega-v4 \
  --region=us-central1 \
  --to-latest=100
```

### Rollback
```bash
gcloud run services update-traffic counselconduit \
  --project=shadowtag-omega-v4 \
  --region=us-central1 \
  --to-revisions=PREVIOUS_REVISION=100
```

## Automation
Cloud Scheduler job `session-pin-cleanup` runs every 30 minutes.
Staging uptime check every 5 minutes.
