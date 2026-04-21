# CounselConduit — PagerDuty / Notification Escalation Runbook

## Item #6: Alert Routing + Escalation Path

### Current Alert Architecture

```
Cloud Monitoring Alerts
    │
    ├── Email: founder@shadowtagai.com (immediate)
    ├── Budget Alerts: GCP Billing → same email
    └── Future: PagerDuty integration (Phase 2)
```

### PagerDuty Setup (When Ready)

1. **Create Service in PagerDuty:**
   - Service name: `counselconduit-production`
   - Escalation policy: Founder → CTO → Engineering Lead
   - Integration: Google Cloud Monitoring

2. **Connect to GCP:**
   ```bash
   # Get PagerDuty integration key from PagerDuty admin
   # Create notification channel in Cloud Monitoring
   TOKEN=$(gcloud auth print-access-token)
   curl -X POST \
     "https://monitoring.googleapis.com/v3/projects/shadowtag-omega-v4/notificationChannels" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "pagerduty",
       "displayName": "CounselConduit PagerDuty",
       "labels": {
         "service_key": "YOUR_PAGERDUTY_SERVICE_KEY"
       }
     }'
   ```

3. **Add to Terraform** (in `main.tf`):
   ```hcl
   resource "google_monitoring_notification_channel" "pagerduty" {
     display_name = "CounselConduit PagerDuty"
     type         = "pagerduty"
     labels = {
       service_key = var.pagerduty_service_key
     }
   }
   ```

### Current Escalation Tiers

| Severity | Alert Source | Notification | Response SLA |
|----------|------------|-------------|-------------|
| **P1 Critical** | SLO burn rate > 10x | Email + (future: PagerDuty page) | 15 min |
| **P2 High** | Uptime check failure (5+ min) | Email | 30 min |
| **P3 Medium** | WAF rate limit spike, fallback rate > 10/5min | Email | 2 hours |
| **P4 Low** | Admin auth failures, budget 50% | Email | Next business day |

### Alert Policies Active

| Alert | Condition | Channel |
|-------|-----------|---------|
| Uptime Failure | `/health` down > 5min | Email ✅ |
| High Error Burn Rate | 5xx > 5/min for 5min | Email ✅ |
| Fallback Rate | > 10 fallbacks/5min | Email ✅ |
| Admin Auth Failures | > 5 failures/5min | Email ✅ |
| Budget 50% | $25 of $50 monthly | Email ✅ |
| Budget 90% | $45 of $50 monthly | Email ✅ |
| SLO Burn Rate | Error budget consumption > 2x | Email ✅ (via SLO alert) |

### Response Playbooks

#### P1: SLO Burn Rate Breach
1. Check `/admin/circuit-breaker` — is circuit open?
2. Check `/admin/provider-health` — any providers down?
3. Check Cloud Run logs for 5xx spike
4. If provider down → circuit breaker auto-handles
5. If Cloud Run issue → rollback to previous revision: `gcloud run services update-traffic counselconduit --to-revisions=PREVIOUS_REVISION=100`

#### P2: Uptime Check Failure
1. Verify from local: `curl -v https://counselconduit-767252945109.us-central1.run.app/health`
2. Check Cloud Run console for cold start issues
3. Verify `min-instances=1` is active: `gcloud run services describe counselconduit --format="value(spec.template.metadata.annotations.autoscaling\.knative\.dev/minScale)"`
4. If DNS issue → check Global External ALB
5. If Cloud Run issue → scale up or force new deployment

#### P3: High Fallback Rate
1. Check specific provider failures in logs
2. Verify API keys are valid for affected provider
3. Check provider status pages (Google Cloud Status, OpenAI Status)
4. If prolonged → adjust routing weights in firm policies

#### P4: Admin Auth Failures
1. Check source IPs in Cloud Armor logs
2. If brute force → add IP to WAF deny list
3. If legitimate → verify admin OIDC configuration
4. Rotate any compromised credentials

### Monthly Review Checklist

- [ ] Verify all alert policies are active
- [ ] Test email delivery for each alert type
- [ ] Review alert volume and false positive rate
- [ ] Update escalation contacts if team changes
- [ ] Validate SLO burn rate calculation accuracy
