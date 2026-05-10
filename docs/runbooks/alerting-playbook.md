# CounselConduit — Alerting Playbook (On-Call Rotation)

## Item #8: Alerting Playbook for On-Call Rotation

### Alert Channels

| Channel | Type | Destination |
|---------|------|-------------|
| Primary | Email | founder@shadowtagai.com |
| Resource ID | notificationChannels | 4615832086798366980 |

### Alert Policies

| Alert | Severity | Condition | Action |
|-------|----------|-----------|--------|
| Circuit Breaker | P1 | 5xx rate > 5% for 5min | Check Cloud Run logs, verify model provider connectivity |
| Uptime Check | P1 | /health fails 2 consecutive checks | Verify Cloud Run revision, check Firestore connectivity |
| Fallback Saturation | P2 | Log metric `counselconduit_fallback_rate` > 0 | Check primary model provider (Gemini), review dispatch metrics |
| Admin Auth Failures | P2 | Log metric `counselconduit_admin_auth_failures` > 5/5min | Review admin logs, check for brute force, verify OIDC tokens |

### Response Procedures

#### P1 — Service Down
1. Check Cloud Run console: `https://console.cloud.google.com/run/detail/us-central1/counselconduit`
2. Verify health: `curl https://counselconduit-767252945109.us-central1.run.app/health`
3. Check logs: `gcloud logging read 'resource.type="cloud_run_revision" severity>=ERROR' --limit=20`
4. If Firestore: check `https://console.cloud.google.com/firestore` for outages
5. Escalate if unresolved after 15 minutes

#### P2 — Degraded Performance
1. Check dispatch metrics: admin auth required
2. Review fallback hits in Cloud Monitoring dashboard
3. Check model provider status pages:
   - Gemini: `https://status.cloud.google.com/`
   - Anthropic: `https://status.anthropic.com/`
   - OpenAI: `https://status.openai.com/`
4. If saturation persists 30+ min, consider scaling `max-instances`

#### P3 — Security Event
1. Admin auth failures → check WAF logs in Cloud Armor
2. Rate limit violations → review WAF rule `counselconduit-waf`
3. If sustained attack: enable Cloud Armor adaptive protection

### On-Call Schedule

| Day | Primary |
|-----|---------|
| Mon-Fri 9am-6pm | Founder |
| After-hours | Email alerts (no PagerDuty yet) |
| Weekends | Email alerts |

### Escalation Contacts

- **Founder**: founder@shadowtagai.com
- **GCP Support**: Premium support via console
- **Firebase**: firebase-support@google.com
