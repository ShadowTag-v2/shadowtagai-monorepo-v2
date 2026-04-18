# CounselConduit Deployment Runbook

> **Service**: `counselconduit` on Cloud Run (Gen2)
> **Region**: `us-central1`
> **Project**: `shadowtag-omega-v4`
> **URL**: `https://counselconduit-767252945109.us-central1.run.app`
> **Last Updated**: 2026-04-18

## Pre-Deployment Checklist

- [ ] All tests pass locally: `PIP_USER=0 .venv/bin/pytest tests/ --ignore=tests/e2e -x`
- [ ] `ruff check apps/counselconduit/ --select F401,F841` reports 0 errors
- [ ] `bandit -r apps/counselconduit/api/ --severity-level medium` reports 0 medium/high
- [ ] Secrets are in Google Secret Manager (not `.env`)
- [ ] `.gcloudignore` is present (prevents 2GB tarball uploads)
- [ ] Git HEAD is tagged `latest-stable`

## Deployment Steps

### 1. Source Deploy (Recommended)

```bash
GCLOUD="/opt/homebrew/share/google-cloud-sdk/bin/gcloud"

# Deploy from source (Cloud Build builds container)
$GCLOUD run deploy counselconduit \
  --source=apps/counselconduit/ \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --service-account=counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --min-instances=1 \
  --max-instances=10 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --set-env-vars="GCP_PROJECT_ID=shadowtag-omega-v4"
```

### 2. Label-Only Update (No rebuild)

```bash
$GCLOUD run services update counselconduit \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --update-labels="managed_by=opentofu,environment=production"
```

### 3. Traffic Splitting (Canary)

```bash
# Route 25% to new revision
$GCLOUD run services update-traffic counselconduit \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --to-revisions=counselconduit-00008-wpf=75,LATEST=25

# Promote to 100%
$GCLOUD run services update-traffic counselconduit \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --to-latest
```

## Post-Deployment Verification

```bash
# Health check
curl -s https://counselconduit-767252945109.us-central1.run.app/health | jq .

# Security headers check
curl -sI https://counselconduit-767252945109.us-central1.run.app/health | grep -E "^(x-|content-security|strict-transport)"

# Webhook signature test (Stripe)
curl -X POST https://counselconduit-767252945109.us-central1.run.app/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"type": "test"}' -w "%{http_code}"
# Expected: 400 (invalid signature — correct behavior)
```

## Rollback

```bash
# List revisions
$GCLOUD run revisions list --service=counselconduit --region=us-central1

# Roll back to previous revision
$GCLOUD run services update-traffic counselconduit \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --to-revisions=counselconduit-00007-c66=100
```

## Environment Variables (Cloud Run)

| Variable | Source | Description |
|----------|--------|-------------|
| `GCP_PROJECT_ID` | Cloud Run env | `shadowtag-omega-v4` |
| `STRIPE_SECRET_KEY` | Secret Manager | Stripe backend key |
| `STRIPE_WEBHOOK_SECRET` | Secret Manager | Webhook HMAC key |
| `GOOGLE_CHAT_SPACE` | Secret Manager | Chat space for ops alerts |
| `GMAIL_SENDER` | Secret Manager | Gmail sender address |

## Service Account

- **Production**: `counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com`
- **Staging**: `counselconduit-staging-sa@shadowtag-omega-v4.iam.gserviceaccount.com`
- **Required Roles**: `roles/secretmanager.secretAccessor`, `roles/datastore.user`, `roles/cloudtasks.enqueuer`

## Monitoring

- **Cloud Run Metrics**: [Console](https://console.cloud.google.com/run/detail/us-central1/counselconduit/metrics?project=shadowtag-omega-v4)
- **Logs**: `gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=counselconduit" --limit 50`
- **Alerts**: Google Chat space (via `workspace_alerts.py`)

## Revisions History

| Revision | Date | Notes |
|----------|------|-------|
| `00008-wpf` | 2026-04-18 | Added IaC labels, Google Workspace alerts |
| `00007-c66` | 2026-04-18 | Health probes + Secret Manager integration |
| `00006-jpl` | 2026-04-18 | Initial production deployment |
