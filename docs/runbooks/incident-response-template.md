# CounselConduit — Incident Response Template

## Item #22: Circuit Breaker Incident Response

### Incident Metadata

| Field | Value |
|-------|-------|
| **Incident ID** | CC-INC-{YYYY}-{NNN} |
| **Severity** | P1 / P2 / P3 |
| **Status** | Investigating / Identified / Monitoring / Resolved |
| **Start Time** | |
| **End Time** | |
| **Duration** | |
| **Incident Commander** | |
| **Impact** | |

### Timeline

| Time | Action | Who |
|------|--------|-----|
| T+0 | Alert fired: {alert name} | Automated |
| T+? | Investigation started | |
| T+? | Root cause identified | |
| T+? | Fix deployed | |
| T+? | Normal operation resumed | |

### Impact Assessment

- **Users affected**: Approximate number of firms/attorneys
- **Requests failed**: Count from Cloud Monitoring
- **Error budget consumed**: % of monthly SLO budget
- **Revenue impact**: Estimated (if billing impacted)

### Root Cause Analysis

#### What happened?
(Describe the technical root cause)

#### Why did detection take X minutes?
(Analyze alert effectiveness)

#### Why did recovery take Y minutes?
(Analyze response process)

### Circuit Breaker Specific Checks

```bash
# 1. Check circuit breaker status
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://counselconduit-767252945109.us-central1.run.app/admin/circuit-breaker

# 2. Check error logs
gcloud logging read 'resource.type="cloud_run_revision"
  resource.labels.service_name="counselconduit"
  severity>=ERROR' --limit=50 --format=json

# 3. Check model provider health
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://counselconduit-767252945109.us-central1.run.app/admin/provider-health

# 4. Check dispatch metrics
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://counselconduit-767252945109.us-central1.run.app/admin/metrics

# 5. Force circuit reset (deploy new revision)
gcloud run deploy counselconduit --source=apps/counselconduit \
  --region=us-central1 --project=shadowtag-omega-v4 --quiet
```

### Prevention Measures

- [ ] Alert threshold adjusted?
- [ ] Circuit breaker parameters tuned?
- [ ] Model provider failover added?
- [ ] Runbook updated?
- [ ] Postmortem shared?

### Postmortem Actions

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| | | | |

### Communication Template

```
Subject: [RESOLVED] CounselConduit Service Degradation - {date}

Team,

We experienced a service degradation on {date} from {start} to {end} ({duration}).

Impact: {X} firms experienced intermittent errors for dispatch requests.

Root Cause: {brief description}

Resolution: {what fixed it}

Prevention: {what we're doing to prevent recurrence}

Timeline and full postmortem: {link}
```
