# CounselConduit — Cloud Run Jobs for Periodic Tasks

## Item #20: Cloud Run Jobs Configuration

### Job: Session Pin Cleanup (Weekly)

Already configured via Cloud Scheduler → HTTP. If direct Cloud Run Jobs preferred:

```bash
# Create a Cloud Run Job for session cleanup
gcloud run jobs create counselconduit-cleanup \
  --image=us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/cleanup:latest \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --service-account=counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=shadowtag-omega-v4,TASK=cleanup_sessions" \
  --memory=256Mi \
  --cpu=0.5 \
  --max-retries=1 \
  --task-timeout=300s \
  --quiet

# Run manually
gcloud run jobs execute counselconduit-cleanup \
  --region=us-central1 \
  --project=shadowtag-omega-v4 \
  --quiet

# Schedule via Cloud Scheduler
gcloud scheduler jobs create http counselconduit-cleanup-cron \
  --location=us-central1 \
  --schedule="0 3 * * 0" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/shadowtag-omega-v4/jobs/counselconduit-cleanup:run" \
  --http-method=POST \
  --oauth-service-account-email=counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com \
  --project=shadowtag-omega-v4
```

### Current Approach (Cloud Scheduler → HTTP Endpoints)

We use Cloud Scheduler hitting Cloud Run *service* endpoints instead of standalone Jobs.
This avoids building a separate container image and keeps all logic in the existing service.

| Job Name | Schedule | Endpoint | Status |
|----------|----------|----------|--------|
| `counselconduit-session-cleanup` | `0 3 * * 0` (Sun 3AM) | `/admin/session-cleanup` | ✅ Active |
| `counselconduit-policy-reload` | `*/5 * * * *` (every 5min) | `/admin/firm-policies/reload` | ✅ Active |

### Future Jobs (Phase 2)

| Job | Schedule | Purpose |
|-----|----------|---------|
| GDPR data purge | `0 2 * * *` (daily 2AM) | Delete expired 30-day GDPR queued data |
| Metrics export | `0 */6 * * *` (every 6hrs) | Export dispatch analytics to BigQuery |
| Token budget reset | `0 0 * * *` (midnight) | Reset any stuck token budget windows |
| Attestation archive | `0 4 * * 1` (Mon 4AM) | Archive old Kovel attestations to GCS |

### When to Use Cloud Run Jobs vs Cloud Scheduler + Service

| Use Cloud Run Jobs | Use Scheduler + Service |
|-------------------|------------------------|
| Long-running batch operations (>10 min) | Short tasks (<60s) |
| Requires different container/dependencies | Same code as service |
| CPU-intensive processing | Simple HTTP endpoint |
| Needs different resource limits | Same resource profile |
