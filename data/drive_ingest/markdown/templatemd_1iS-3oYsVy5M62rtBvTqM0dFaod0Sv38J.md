# Incident Postmortem Template

## Incident Overview

- **Incident ID**: INC-YYYY-MM-DD-NNN
- **Date/Time**: YYYY-MM-DD HH:MM UTC
- **Duration**: X hours Y minutes
- **Severity**: [Critical / High / Medium / Low]
- **Services Affected**: [List services/APIs]
- **User Impact**: [Description and % of users affected]
- **Incident Commander**: @username
- **Participants**: @user1, @user2, @user3

## Summary (TL;DR)

_One-paragraph summary of what happened, root cause, and resolution._

Example:
> On 2025-11-08 at 14:32 UTC, the ShadowTag API experienced a 15-minute outage affecting ~30% of users due to a database connection pool exhaustion. The root cause was a deployment that increased query complexity without adjusting pool size. The issue was resolved by rolling back the deployment and increasing the connection pool limit.

---

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 14:32 | First alerts: elevated error rate |
| 14:35 | On-call engineer paged |
| 14:38 | Incident declared, war room opened |
| 14:42 | Root cause identified (DB connection pool) |
| 14:45 | Rollback initiated |
| 14:47 | Rollback complete, error rate normalizing |
| 14:52 | Services fully recovered |
| 15:00 | Incident closed |

---

## Root Cause Analysis (5-Whys)

1. **Why did the outage occur?**
   - The database connection pool was exhausted.

2. **Why was the connection pool exhausted?**
   - A new query pattern created by the recent deployment held connections longer.

3. **Why did the new query pattern hold connections longer?**
   - The query included a complex JOIN that wasn't optimized.

4. **Why wasn't the query optimized before deployment?**
   - Load testing in staging didn't replicate production traffic patterns.

5. **Why didn't staging replicate production traffic patterns?**
   - **Root Cause**: Staging environment uses a smaller dataset and lower concurrency, missing the performance regression.

---

## What Went Wrong

- **Immediate Cause**: Database connection pool exhaustion under production load.
- **Contributing Factors**:
  - Insufficient load testing with production-scale data.
  - No query performance regression tests in CI.
  - Connection pool size not reviewed during code review.
- **Detection Delay**: 3 minutes (alerting threshold was set too high).

---

## What Went Right

- Automated rollback procedure worked as expected.
- On-call engineer responded within 3 minutes.
- Clear communication in #incidents channel.
- Customer-facing status page updated within 5 minutes.
- No data loss or corruption.

---

## Impact Assessment

### User Impact
- **Users Affected**: ~30% of active users (~1,500 users)
- **Requests Failed**: ~12,000 requests
- **Error Types**: 503 Service Unavailable, timeout errors
- **User Complaints**: 23 support tickets filed

### Business Impact
- **Revenue**: Estimated $XXX in lost transactions
- **SLA**: Error budget consumed: 15 minutes (~1% of monthly budget)
- **Reputation**: Minor Twitter mentions, no press coverage

### Technical Debt Created
- Need to refactor query before re-deploying feature.
- Need to scale staging environment for realistic load tests.

---

## Action Items

| Action | Owner | Deadline | Status | Priority |
|--------|-------|----------|--------|----------|
| Optimize JOIN query and add index | @eng-lead | 2025-11-10 | 🟡 In Progress | P0 |
| Increase DB connection pool to 200 | @sre | 2025-11-08 | ✅ Done | P0 |
| Add query performance tests to CI | @qa-eng | 2025-11-15 | 🔴 Not Started | P1 |
| Scale staging DB to 50% of prod size | @platform | 2025-11-20 | 🔴 Not Started | P1 |
| Lower alerting threshold to 0.5% error rate | @sre | 2025-11-09 | ✅ Done | P2 |
| Document query review checklist | @eng-lead | 2025-11-12 | 🟡 In Progress | P2 |
| Conduct load testing training | @qa-lead | 2025-11-30 | 🔴 Not Started | P3 |

---

## Lessons Learned

### What We'll Change
1. **Load Testing**: All PRs touching database queries must include load test results.
2. **Staging Parity**: Increase staging database size to 50% of production.
3. **Alerting**: Lower error rate threshold to detect issues faster.
4. **Code Review**: Add connection pool impact to review checklist.

### What We'll Keep
1. **Rollback Procedure**: Current automated rollback worked well.
2. **Incident Communication**: Clear, timely updates on status page and internal channels.
3. **On-Call Response**: Fast acknowledgment and escalation.

---

## Supporting Evidence

- **Logs**: [Link to CloudWatch/Datadog logs]
- **Metrics**: [Link to Grafana dashboard]
- **PR**: [Link to problematic PR]
- **Rollback PR**: [Link to rollback PR]
- **Slack Thread**: [Link to #incidents thread]

---

## Follow-Up Review

- **Postmortem Review Meeting**: Scheduled for YYYY-MM-DD
- **Attendees**: Engineering team, SRE, QA, Product
- **Recording**: [Link to Zoom recording]
- **Blameless Culture Reminder**: This is a learning opportunity, not a blame session.

---

## Sign-Off

- **Postmortem Author**: @username
- **Reviewed By**: @eng-manager, @sre-lead
- **Approved By**: @vp-engineering
- **Date Finalized**: YYYY-MM-DD

---

## Appendix

### Technical Details

```sql
-- Problematic query (before optimization)
SELECT u.*, p.*, c.count
FROM users u
JOIN profiles p ON u.id = p.user_id
JOIN (SELECT user_id, COUNT(*) as count FROM comments GROUP BY user_id) c ON u.id = c.user_id
WHERE u.created_at > NOW() - INTERVAL '30 days';

-- Optimized query (with index on comments.user_id)
-- (details in PR #XXX)
```

### Monitoring Snapshots

![Error Rate Spike](link-to-screenshot.png)
![DB Connection Pool Usage](link-to-screenshot.png)

---

**Document Location**: `safety/postmortems/YYYY-MM-DD-incident-description.md`
**Retention**: Permanent (required for compliance and historical analysis)