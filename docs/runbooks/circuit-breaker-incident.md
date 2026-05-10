# Circuit Breaker OPEN — Incident Response Runbook

## Detection
- Cloud Monitoring alert fires: "Circuit Breaker OPEN"
- `/admin/circuit-breaker-status` shows `state: "open"` for a model
- Dispatch errors spike in `/admin/metrics`

## Severity Classification
| Condition | Severity |
|-----------|----------|
| Single model CB open, others healthy | P3 — Low |
| >50% models CB open | P2 — Medium |
| All models CB open | P1 — High (service degraded) |
| Primary model (gemini-flash) CB open | P2 — Medium |

## Immediate Response (P2+)

### Step 1: Assess
```bash
curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://counselconduit-767252945109.us-central1.run.app/admin/circuit-breaker-status | jq
```

### Step 2: Check Provider Status
```bash
curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://counselconduit-767252945109.us-central1.run.app/admin/provider-health | jq
```

### Step 3: Force Reset (if provider is back)
The circuit breaker auto-resets after the cooldown window (half-open probe).
If you need to force-reset, redeploy:
```bash
gcloud run services update counselconduit \
  --project=shadowtag-omega-v4 \
  --region=us-central1 \
  --update-env-vars="FORCE_CB_RESET=$(date +%s)" \
  --quiet
```

### Step 4: Monitor Recovery
- Watch `/admin/metrics` for dispatch success rate recovery
- Verify error budget consumption in SLO dashboard
- Update #incidents Workspace Chat thread

## Root Cause Analysis Template
1. Which model(s) triggered CB?
2. What was the error type? (timeout, 429, 500, network)
3. Was it provider-side or our-side?
4. Duration of outage?
5. Tokens/requests affected?
6. Error budget consumed?

## Escalation
- P2+: Notify via FCM admin topic
- P1: Page founder via email
