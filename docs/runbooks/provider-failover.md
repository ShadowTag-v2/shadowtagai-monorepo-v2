# Provider Failover Runbook

## Purpose
Emergency procedures for LLM provider outages affecting CounselConduit.

## Detection
- **Alert**: "CounselConduit Providers Health — Uptime Failing" fires
- **Dashboard**: CounselConduit Operations → Provider Health widget
- **Manual**: `curl https://counselconduit-767252945109.us-central1.run.app/health/providers`

## Provider Priority (Failover Order)
1. **Google Gemini** (primary) — `gemini-2.0-flash`
2. **Anthropic Claude** (secondary) — `claude-sonnet-4-20250514`
3. **OpenAI GPT** (tertiary) — `gpt-4o`

## Failover Procedure

### Single Provider Down
1. Check provider status page:
   - Gemini: https://status.cloud.google.com
   - Claude: https://status.anthropic.com
   - OpenAI: https://status.openai.com
2. No action needed — model_router auto-fails to next provider
3. Monitor `/health/providers` for recovery

### All Providers Down
1. **Severity**: P1 — page on-call
2. Check local network/DNS: `dig api.openai.com +short`
3. Check Cloud Run egress: `gcloud run services logs read counselconduit --limit=50`
4. If Cloud Run networking issue:
   ```bash
   gcloud run services update counselconduit \
     --region=us-central1 \
     --set-env-vars="FALLBACK_MODE=true" \
     --quiet
   ```
5. Fallback mode returns cached responses with disclaimer

### Gemini Quota Exhausted
1. Check quota: GCP Console → IAM & Admin → Quotas → Vertex AI
2. Request increase: `gcloud alpha services quota update`
3. Temporary: route 100% to Claude via env var:
   ```bash
   gcloud run services update counselconduit \
     --set-env-vars="MODEL_ROUTING_OVERRIDE=claude" \
     --region=us-central1 --quiet
   ```

## Recovery
1. Verify all 3 providers return "reachable" on `/health/providers`
2. Remove any `MODEL_ROUTING_OVERRIDE` or `FALLBACK_MODE` env vars
3. Close incident in GCP Console → Error Reporting

## Contacts
- **On-call**: Erik (founder) — see PagerDuty
- **GCP Support**: Premium support case via Console
- **Anthropic**: support@anthropic.com
- **OpenAI**: support@openai.com
