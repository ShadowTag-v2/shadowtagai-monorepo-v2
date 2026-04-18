# Rollback Procedure

## Purpose
This document defines the standard operating procedure for rolling back deployments in response to failures, performance degradation, or security incidents.

## When to Rollback

### Automatic Rollback Triggers
- Health check failures for >5 minutes
- Error rate >1% for >2 minutes
- P95 latency >2x baseline for >5 minutes
- Critical security vulnerability detected in production

### Manual Rollback Triggers
- Customer-reported data corruption or loss
- Unexpected behavior affecting >10% of users
- Compliance violation detected
- Executive decision (emergency response)

## Rollback Procedure

### 1. Identify the Issue
```bash
# Check recent deployments
gh api repos/ehanc69/ShadowTag-v2-fastapi-services/deployments \
  --jq '.[] | select(.created_at > "2025-11-01") | {id, sha, created_at, environment}'

# Check current production SHA
git log --oneline -10
```

### 2. Find Last Known Good Version
```bash
# List recent releases
gh release list --limit 10

# Or find last successful deployment
gh run list --workflow=deploy --status=success --limit 5
```

### 3. Execute Rollback

#### Option A: Feature Flag (Preferred)
```bash
# Disable risky feature flag via API or admin panel
curl -X PATCH https://api.ShadowTag-v2.com/admin/flags/new-feature \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -d '{"enabled": false}'
```

#### Option B: Git Revert + Redeploy
```bash
# Create rollback branch
git checkout main
git pull
git checkout -b rollback/incident-$(date +%Y%m%d-%H%M)

# Revert problematic commit(s)
git revert <bad-commit-sha> --no-edit

# Push and create PR
git push -u origin rollback/incident-*
gh pr create --title "Rollback: <incident-description>" \
  --body "Emergency rollback. See incident report: <link>"

# If approved, merge and deploy
gh pr merge --squash --delete-branch
```

#### Option C: Redeploy Previous Release
```bash
# Deploy previous release tag
gh workflow run deploy.yml \
  -f ref=v1.2.3 \
  -f environment=production
```

### 4. Verify Rollback Success
```bash
# Check health endpoints
curl https://api.ShadowTag-v2.com/health | jq '.status'

# Monitor error rates
# (Use your monitoring dashboard: Datadog, Grafana, etc.)

# Verify user-facing functionality
# Run smoke tests or manual verification
```

### 5. Post-Rollback Actions

#### Immediate (within 1 hour)
- [ ] Update status page: "Incident resolved via rollback"
- [ ] Notify stakeholders (engineering, customer success, leadership)
- [ ] Preserve logs and metrics from failed deployment

#### Within 24 hours
- [ ] Create incident postmortem (use `safety/postmortems/template.md`)
- [ ] Update risk register if new failure mode discovered
- [ ] Schedule blameless postmortem review meeting

#### Within 1 week
- [ ] Implement additional safeguards to prevent recurrence
- [ ] Update CI/CD pipeline with new tests/gates
- [ ] Conduct team training if process gaps identified

## Rollback Decision Matrix

| Condition | Rollback? | Method | Approval |
|-----------|-----------|--------|----------|
| Health check fails >5min | Yes | Auto (feature flag) | None (automated) |
| Error rate >1% sustained | Yes | Auto (redeploy) | None (automated) |
| Critical CVE in prod | Yes | Manual (revert) | Engineering Manager |
| UI bug affecting <1% users | No | Fix-forward | Team Lead |
| Performance regression 20% | Maybe | Feature flag test | Engineering Manager |
| Data corruption detected | Yes | Immediate (revert) | CTO + Incident Commander |

## Rollback Communication Template

### Internal (Slack/Teams)
```
🚨 ROLLBACK INITIATED
- Incident: <brief description>
- Trigger: <automated/manual>
- Action: Rolling back to <version/commit>
- ETA: <estimated time to complete>
- Incident Commander: @<name>
- Status updates: Every 15 minutes in #incidents
```

### External (Status Page)
```
We are currently experiencing [issue description].
Our team has identified the root cause and is rolling back
to a previous stable version. We expect full service restoration
within [timeframe]. We apologize for any inconvenience.

Updates:
- [timestamp] Issue detected
- [timestamp] Rollback initiated
- [timestamp] Rollback complete, monitoring recovery
```

## Prevention

### Pre-Deployment Safeguards
- Canary deployments (10% traffic for 15 minutes)
- Automated smoke tests in staging
- Feature flags for all major changes
- Peer review + automated security scans

### Monitoring & Alerting
- Real-time error rate monitoring
- Latency percentile tracking (P50, P95, P99)
- Health check endpoints with detailed status
- On-call rotation with escalation policy

## Compliance & Audit

- All rollbacks logged in `safety/audits/rollback-log.jsonl`
- Postmortems stored in `safety/postmortems/`
- Quarterly rollback drills to test procedure
- Annual review of rollback effectiveness metrics

## Document Ownership

- **Owner**: SRE/DevOps Team Lead
- **Approver**: VP Engineering / CTO
- **Last Updated**: 2025-11-08
- **Next Review**: 2026-02-08 (quarterly)

---

## Quick Reference

```bash
# Emergency rollback (one-liner)
gh workflow run deploy.yml -f ref=$(gh release list --limit 1 --json tagName --jq '.[0].tagName') -f environment=production
```

**Incident Hotline**: #incidents (Slack) | incidents@ShadowTag-v2.com
**On-Call**: PagerDuty rotation | +1-555-ONCALL
