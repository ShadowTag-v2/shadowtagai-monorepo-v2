# CounselConduit — Staging Environment

## Item #11: Staging Environment Configuration

### Overview

Staging uses the same Cloud Run service with `APP_ENV=staging` to differentiate behavior.
Staging traffic is routed to a tagged revision that does NOT receive live traffic.

### Setup

```bash
# Deploy a staging revision (tagged, no traffic)
gcloud run deploy counselconduit \
  --source=apps/counselconduit \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --service-account=counselconduit-staging-sa@shadowtag-omega-v4.iam.gserviceaccount.com \
  --no-traffic \
  --tag=staging \
  --set-env-vars="APP_ENV=staging,GOOGLE_CLOUD_PROJECT=shadowtag-omega-v4" \
  --memory=512Mi \
  --cpu=1 \
  --quiet
```

### Access

The staging revision gets a URL like:
```
https://staging---counselconduit-767252945109.us-central1.run.app
```

### Environment Differences

| Setting | Production | Staging |
|---------|-----------|---------|
| `APP_ENV` | `production` | `staging` |
| Admin auth | OIDC required | Relaxed (auto-approve) |
| Firestore DB | `(default)` | `(default)` (same, but filtered by `env` field) |
| Rate limits | Enforced | Higher thresholds |
| Model providers | All live | Gemini Flash only |
| Service Account | `counselconduit-sa` | `counselconduit-staging-sa` |

### Smoke Test Against Staging

```bash
BASE_URL=https://staging---counselconduit-767252945109.us-central1.run.app \
  pytest apps/counselconduit/tests/test_smoke.py -v
```

### Promote Staging to Production

```bash
# Route 100% traffic to the staging revision
gcloud run services update-traffic counselconduit \
  --region=us-central1 \
  --to-tags=staging=100 \
  --project=shadowtag-omega-v4
```
