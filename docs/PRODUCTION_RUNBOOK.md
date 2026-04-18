# CounselConduit Production Runbook v1.0

## Service Overview
- **Service**: CounselConduit API
- **URL**: https://counselconduit-767252945109.us-central1.run.app
- **Staging**: https://counselconduit-staging-767252945109.us-central1.run.app
- **Region**: us-central1
- **SA**: counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com
- **Current Rev**: 00010-s74 (100% traffic)

## Health Endpoints
| Endpoint | Expected | Purpose |
|----------|----------|---------|
| `/enclave/v1/health` | 200 | Liveness + Firestore connectivity |
| `/enclave/v1/docs` | 200 | OpenAPI documentation |
| `/enclave/v1/openapi.json` | 200 | Machine-readable spec |

## Incident Response

### Severity Levels
| Level | Examples | Response Time |
|-------|----------|--------------|
| SEV1 | Service down, data breach, auth bypass | < 15 min |
| SEV2 | Degraded performance, partial failure | < 1 hour |
| SEV3 | Non-critical feature broken | < 4 hours |
| SEV4 | Cosmetic, logging, monitoring gap | Next business day |

### SEV1: Service Down
```bash
# 1. Verify outage
curl -s https://counselconduit-767252945109.us-central1.run.app/enclave/v1/health

# 2. Check Cloud Run logs
gcloud run services logs read counselconduit --region=us-central1 --limit=50

# 3. Check for recent deploys
gcloud run revisions list --service=counselconduit --region=us-central1 --limit=5

# 4. Rollback to previous revision
gcloud run services update-traffic counselconduit \
  --region=us-central1 \
  --to-revisions=counselconduit-00009=100

# 5. Notify via Chat
# Message CounselConduit Ops space

# 6. Post-mortem within 24h
```

### SEV2: Degraded Performance
```bash
# 1. Check current metrics
gcloud monitoring dashboards list --project=shadowtag-omega-v4

# 2. Check Cloud Trace for slow spans
# Console: https://console.cloud.google.com/traces?project=shadowtag-omega-v4

# 3. Scale up if needed
gcloud run services update counselconduit \
  --region=us-central1 \
  --min-instances=2 --max-instances=20

# 4. Check Firestore quotas
gcloud firestore operations list --project=shadowtag-omega-v4
```

### SEV1: Auth/Payment Breach
```bash
# 1. Rotate ALL secrets immediately
gcloud secrets versions add stripe-secret-key --data-file=- --project=shadowtag-omega-v4
gcloud secrets versions add stripe-webhook-secret --data-file=- --project=shadowtag-omega-v4

# 2. Rotate GitHub App PEMs
# See docs/SECRET_ROTATION.md

# 3. Review audit logs
gcloud logging read 'resource.type="audited_resource"' --project=shadowtag-omega-v4 --limit=100

# 4. Disable compromised accounts
# 5. Legal notification (if PII involved)
```

## Deployment

### Standard Deploy (via Cloud Build)
```bash
git push origin main  # Triggers cloudbuild.yaml
```

### Manual Deploy
```bash
gcloud run deploy counselconduit \
  --source=apps/counselconduit \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --quiet
```

### Canary Deploy
```bash
# 1. Deploy new revision (0% traffic)
gcloud run deploy counselconduit --source=apps/counselconduit \
  --region=us-central1 --no-traffic

# 2. Split traffic 90/10
gcloud run services update-traffic counselconduit \
  --region=us-central1 --to-revisions=LATEST=10

# 3. Monitor for 30 minutes
# 4. Promote or rollback
gcloud run services update-traffic counselconduit \
  --region=us-central1 --to-latest
```

## Monitoring

### Alert Policies (7 active)
1. Secret Manager Access Anomaly (>100 ops/5min)
2. Firestore High Read Volume (>10K/5min)
3. Firestore High Write Volume (>5K/5min)
4. Cloud Run Error Rate
5. Cloud Run Latency P99
6. Uptime Check: kovelai.web.app
7. Uptime Check: shadowtagai.web.app

### Notification Channel
- Email: founder@shadowtagai.com (ID: 17531835029676919705)
- Chat: CounselConduit Ops (pending scope configuration)

## Contacts
- **On-call**: founder@shadowtagai.com
- **Escalation**: Same (solo founder stage)
