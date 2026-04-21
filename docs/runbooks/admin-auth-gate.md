# CounselConduit Admin Auth Gate — Runbook

## Overview
Admin endpoints (`/admin/*`) are protected by OIDC Bearer token validation in production.
Dev bypass is available when `APP_ENV != production`.

## Architecture

```
Cloud Scheduler → OIDC Token → /admin/session-cleanup
Firebase Admin → JWT → /admin/firm-policy, /admin/metrics, etc.
Unauthenticated → 401 Unauthorized
```

## Protected Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/metrics` | GET | Dispatch metrics (counts, fallbacks, uptime) |
| `/admin/models` | GET | Available model list |
| `/admin/firm-policy` | POST | Set firm routing policy |
| `/admin/session-cleanup` | POST | Evict expired session pins |
| `/admin/circuit-breaker` | POST | Force open/close circuit |
| `/admin/firm-policies` | GET | List all cached policies |
| `/admin/firm-policies/reload` | POST | Force reload from Firestore |

## Troubleshooting

### 1. Cloud Scheduler Returns 401

**Symptom:** Scheduler job shows `lastAttemptTime` but status has error code.

**Fix:**
```bash
# Verify SA has invoker role
gcloud projects get-iam-policy shadowtag-omega-v4 \
  --flatten="bindings[].members" \
  --filter="bindings.members:counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com AND bindings.role:roles/run.invoker"

# Verify CLOUD_RUN_URL env var matches audience
gcloud run services describe counselconduit --region=us-central1 --format="value(status.url)"

# Check scheduler job config
gcloud scheduler jobs describe counselconduit-session-cleanup --location=us-central1
```

### 2. All Admin Calls Return 401

**Symptom:** Even legitimate OIDC tokens are rejected.

**Fix:**
```bash
# Check CLOUD_RUN_URL is set correctly
gcloud run services describe counselconduit --region=us-central1 --format="yaml(spec.template.spec.containers[0].env)"

# The audience in the OIDC token MUST match CLOUD_RUN_URL exactly
# Common issue: missing trailing slash or scheme mismatch
```

### 3. Dev Bypass Not Working

**Symptom:** Local dev returns 401.

**Fix:** Ensure `APP_ENV` is NOT set to `production`:
```bash
unset APP_ENV
# or
export APP_ENV=development
```

### 4. Structured Log Queries

```bash
# All admin auth events
gcloud logging read 'jsonPayload.event="admin_auth"' --project=shadowtag-omega-v4 --limit=20

# Failed auth attempts
gcloud logging read 'jsonPayload.event="admin_auth" AND jsonPayload.outcome="rejected"' --project=shadowtag-omega-v4

# Missing credentials (probing/scanning)
gcloud logging read 'jsonPayload.event="admin_auth" AND jsonPayload.outcome="no_credentials"' --project=shadowtag-omega-v4

# Successful auth by specific caller
gcloud logging read 'jsonPayload.event="admin_auth" AND jsonPayload.outcome="success"' --project=shadowtag-omega-v4 --limit=10
```

## Monitoring

- **Dashboard:** "CounselConduit Operations" in Cloud Monitoring
- **Uptime Check:** `counselconduit-health-8tRsKZV3dY8` (5-min interval)
- **Alert: Circuit Breaker:** Fires on >5% 5xx error rate over 5 min
- **Alert: Uptime:** Fires when /health fails for 5 min
- **Alert: Fallback Saturation:** Fires when >30% of dispatches use fallback model
- **Cloud Scheduler:** `counselconduit-session-cleanup` every 5 min

## Error Budget SLO

- **Target:** 99.5% availability (monthly)
- **Budget:** ~219 min/month downtime allowed
- **Burn rate alert:** >2x burn rate over 1h triggers pager
