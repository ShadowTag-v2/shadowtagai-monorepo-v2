# CounselConduit — Incident Response Drill Schedule

## Item #22: Monthly Drill Configuration

### Purpose

Tabletop exercises to verify runbook accuracy, response time, and team readiness.

### Monthly Schedule

| Month | Scenario | Scope |
|-------|----------|-------|
| Jan | Model provider outage (Gemini down) | Verify fallback routing, circuit breaker, provider-health endpoint |
| Feb | WAF blocking legitimate traffic | Review Cloud Armor rules, false positive handling |
| Mar | Billing overage (budget exceeded) | Budget alert response, cost analysis, scaling decisions |
| Apr | GDPR deletion request (real-world) | Full deletion pipeline, audit trail verification |
| May | Circuit breaker trip (sustained 5xx) | Response procedures, rollback, root cause analysis |
| Jun | Stripe webhook failure | Payment reconciliation, manual invoice handling |
| Jul | Admin credential compromise | Rotate creds, audit logs, incident communication |
| Aug | Data breach notification | Legal response, user notification, GDPR compliance |
| Sep | Cold start degradation | Min-instances tuning, scaling profile review |
| Oct | Full service outage | End-to-end recovery, DNS failover, status page |
| Nov | Rate limit bypass attempt | WAF rule validation, token budget verification |
| Dec | Year-end security audit | Full Cor.30 checklist, dependency updates, key rotation |

### Drill Execution Protocol

1. **T-7 days**: Announce drill date and scenario (no details)
2. **T-0**: Trigger simulated alert
3. **T+0 to T+30min**: Response execution
4. **T+30min**: Debrief
5. **T+2 days**: Written lessons learned + runbook updates

### Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Alert to acknowledgement | < 5 min | N/A (first drill pending) |
| Incident commander assigned | < 10 min | N/A |
| Root cause identified | < 30 min | N/A |
| Service restored | < 60 min | N/A |
| Postmortem published | < 48 hrs | N/A |

### Cloud Scheduler Reminder

```bash
# Monthly drill reminder (1st Monday of each month, 10 AM)
gcloud scheduler jobs create http counselconduit-drill-reminder \
  --location=us-central1 \
  --schedule="0 10 1-7 * 1" \
  --uri="https://hooks.googleapis.com/chat/v1/spaces/YOUR_SPACE_ID/messages?key=YOUR_KEY" \
  --http-method=POST \
  --message-body='{"text":"🚨 Monthly Incident Response Drill scheduled this week. Check docs/runbooks/incident-drill-schedule.md"}' \
  --project=shadowtag-omega-v4
```

### Sign-off

After each drill, the incident commander must update this file:

| Date | Scenario | Duration | Lessons | Updated By |
|------|----------|----------|---------|-----------|
| — | — | — | — | — |
