# JULES_CRISIS_RESPONSE_PLAYBOOK.md

**Version**: 1.0  
**Date**: May 6, 2026

---

## Jules Crisis Response Playbook

**Core Principle**: Stay calm, act fast, communicate clearly, protect the company.

---

### Crisis Levels

| Level | Severity     | Examples                              | Response Time |
|-------|--------------|---------------------------------------|---------------|
| 1     | Minor        | Minor bug, small metric dip           | < 2 hours     |
| 2     | Moderate     | Major feature broken, credit spike    | < 1 hour      |
| 3     | Serious      | Security incident, major outage       | < 30 min      |
| 4     | Critical     | Data breach, regulatory action, cash crisis | Immediate |

---

### General Response Protocol (All Levels)

1. **Assess** (5–10 min)
   - What exactly happened?
   - How bad is it? (users affected, revenue impact, reputation risk)
   - Is this a one-time event or ongoing?

2. **Contain** (Immediate)
   - Stop the bleeding (rollback, disable feature, pause spending)
   - Protect users and data

3. **Communicate** (Within 30–60 min)
   - Internal: Post in #crisis channel
   - External: Prepare holding statement if needed
   - Users: Transparent update if service is affected

4. **Fix** (Fastest possible)
   - Root cause analysis
   - Implement fix
   - Test thoroughly (use Browser Subagent)

5. **Recover** (Next 24–48 hours)
   - Monitor closely
   - Communicate resolution
   - Document lessons learned

6. **Prevent** (Within 7 days)
   - Add safeguards / monitoring
   - Update this playbook if needed
   - Run simulation if high-risk

---

### Specific Crisis Scenarios

#### Scenario A: Major Google API / Credit Crisis

**Symptoms**: Sudden 4x+ increase in credit costs or access restrictions

**Immediate Actions**:
1. Pause all non-essential asset generation
2. Switch to lower-cost fallback models (open-source)
3. Notify B2B customers of potential temporary quality impact
4. Run emergency cost optimization
5. Activate "Google Exit Plan" (pre-built diversification strategy)

#### Scenario B: Security Incident / Data Breach

**Immediate Actions**:
1. Isolate affected systems
2. Revoke all tokens and rotate secrets
3. Engage security team / external experts
4. Prepare regulatory notifications (if required)
5. Communicate transparently with users

#### Scenario C: Major Reputation Crisis (Viral Backlash)

**Immediate Actions**:
1. Acknowledge the issue publicly within 1 hour
2. Take responsibility (never blame users or Google)
3. Deploy fix + compensation plan (credits, refunds)
4. Over-communicate updates for 48 hours
5. Run internal post-mortem within 7 days

#### Scenario D: Cash / Runway Crisis

**Immediate Actions**:
1. Cut all non-essential spending (including credit usage)
2. Accelerate B2B sales pipeline
3. Explore bridge financing options (if needed)
4. Prioritize highest-ROI features only
5. Communicate honestly with any remaining team members

---

### Communication Templates

**Internal (Slack / Email)**:
```
🚨 CRISIS ALERT - Level [X]

Issue: [Short description]
Impact: [Users / Revenue / Reputation affected]
Status: [What we're doing right now]
ETA for Update: [Time]
Owner: Jules
```

**External (X / Website)**:
```
We’re aware of [issue] and are working on it right now. 
We expect to have a full update within [X] hours. 
Thank you for your patience.
```

---

**End of Crisis Response Playbook**
```