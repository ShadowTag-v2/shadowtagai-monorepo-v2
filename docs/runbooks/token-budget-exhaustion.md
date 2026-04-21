# Token Budget Exhaustion — Alerting Runbook

## Trigger
Token budget consumption exceeds 80% of tier limit within the billing period.

## Tiers & Limits
| Tier | Monthly Limit | Warning (80%) | Critical (95%) |
|------|---------------|---------------|----------------|
| Solo | 500K tokens | 400K | 475K |
| Practice | 2M tokens | 1.6M | 1.9M |
| Enterprise | 10M tokens | 8M | 9.5M |

## Alert Flow
1. **Warning (80%)**: Log metric fires → email notification → dashboard turns amber
2. **Critical (95%)**: Log metric fires → P2 alert → auto-suggest tier upgrade in-app
3. **Exhausted (100%)**: Requests degraded to gemini-flash only → user notified

## Response Procedure

### Automated
- System auto-degrades to cheapest model (gemini-flash) at 100%
- Token counter resets on billing period rollover (monthly)
- Usage summary email sent to firm admin

### Manual Escalation
1. Check Firestore `tenant_quotas/{firm_id}` for actual usage
2. Verify billing tier in Stripe (`customer.subscriptions`)
3. Contact firm admin about tier upgrade if repeated

## Prevention
- Weekly usage report in admin dashboard
- In-app budget meter (progress bar in client portal)
- 3-day usage trend projection (linear extrapolation)
