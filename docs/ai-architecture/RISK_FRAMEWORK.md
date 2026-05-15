# RISK_FRAMEWORK - Compliance Framework Gates & Kill-Switch Protocols

**Version**: 1.0
**Last Updated**: 2025-11-14
**Purpose**: Systematic risk assessment and mitigation framework based on US Army Compliance Framework risk management doctrine

---

## OVERVIEW

This document adapts **Compliance Framework (Army Techniques Publication: Risk Management)** for Pnkln's strategic, technical, and operational decision-making.

**Core Principle**: Identify risks early, assess systematically, mitigate proactively, and monitor continuously.

**Five-Step Process**:

1. **Identify Hazards**: What could go wrong?

2. **Assess Hazards**: Probability × Severity = Risk Level

3. **Develop Controls**: Mitigation strategies

4. **Implement Controls**: Execute mitigation plan

5. **Supervise & Evaluate**: Ongoing monitoring

---

## STEP 1: IDENTIFY HAZARDS

### Hazard Categories

#### 1. Financial Hazards

**Definition**: Risks that impact capital, burn rate, revenue, or profitability

**Common Hazards**:

- **Burn Overrun**: Monthly spend exceeds budget ($10K target, $12K kill-switch)

- **Revenue Shortfall**: Customers don't convert, churn exceeds forecast

- **Cost Surprise**: Unexpected infrastructure, legal, or operational costs

- **Payment Risk**: Customer non-payment, delayed payment, disputes

- **Economic Shock**: Market downturn, customer budget cuts

**Identification Methods**:

- Weekly burn tracking (compare actual vs. budget)

- Monthly revenue forecast vs. actual analysis

- Quarterly financial scenario planning (best/base/worst case)

#### 2. Technical Hazards

**Definition**: Risks that impact system performance, reliability, or security

**Common Hazards**:

- **Performance Degradation**: Latency exceeds SLA (p99>90ms for Judge 6)

- **Downtime**: System unavailable (uptime <99.9%)

- **Data Loss**: Database corruption, backup failure

- **Security Breach**: Unauthorized access, data leak, CVE exploit

- **Scaling Failure**: System can't handle growth (load exceeds capacity)

- **Dependency Risk**: Third-party API failure (ERCOT, payment processor)

**Identification Methods**:

- Real-time monitoring (Datadog, CloudWatch)

- Dependency audits (Dependabot, Snyk for CVEs)

- Load testing (simulate 2×-5× current traffic)

- Incident post-mortems (learn from failures)

#### 3. Market/Customer Hazards

**Definition**: Risks that impact product-market fit, customer satisfaction, or competitive position

**Common Hazards**:

- **Product-Market Misfit**: Building features customers don't want

- **Competitor Disruption**: Competitor launches superior product or undercuts pricing

- **Customer Concentration**: Over-reliance on single customer (>25% of revenue)

- **Regulatory Change**: New regulations impact business model (energy market rules)

- **Market Saturation**: Addressable market smaller than assumed

**Identification Methods**:

- Monthly customer feedback review (NPS, exit interviews)

- Quarterly competitive analysis (pricing, features, positioning)

- Revenue concentration tracking (flag if 1 customer >25%)

- Industry news monitoring (regulatory, competitive moves)

#### 4. Team/Execution Hazards

**Definition**: Risks that impact team capacity, knowledge, or operational execution

**Common Hazards**:

- **Key Person Dependency**: Critical knowledge in one person's head (founder, specialist)

- **Burnout**: Team working unsustainable hours, quality degrading

- **Skill Gap**: Lack expertise for critical task (security, compliance, scaling)

- **Operational Errors**: Manual processes prone to mistakes (deploy, config)

- **Communication Breakdown**: Misalignment on priorities, assumptions

**Identification Methods**:

- Weekly team health check (workload, blockers, morale)

- Documentation audit (what's only in someone's head?)

- Skill matrix review (identify gaps quarterly)

- Post-incident reviews (root cause often human error)

#### 5. Legal/Compliance Hazards

**Definition**: Risks that impact legal standing, regulatory compliance, or IP

**Common Hazards**:

- **IP Infringement**: Using code, data, or content without rights

- **Regulatory Violation**: GDPR, CCPA, energy market compliance

- **Contract Breach**: Failing to deliver on customer commitments

- **Liability Exposure**: Customer financial loss due to system failure

- **Employment Issues**: Misclassification (contractor vs. employee), labor laws

**Identification Methods**:

- Quarterly legal/compliance review (advisor or counsel)

- Contract audit (what are we committed to?)

- License audit (all dependencies properly licensed?)

- Privacy impact assessment (handling PII correctly?)

### Hazard Identification Template

```

HAZARD: [Brief description]
CATEGORY: [Financial/Technical/Market/Team/Legal]
TRIGGER: [What event would cause this?]
IMPACT AREA: [What gets damaged if this occurs?]
DETECTION: [How would we know this happened?]
LIKELIHOOD: [How often could this occur?]

```

**Example**:

```

HAZARD: ERCOT API becomes unavailable for 24+ hours
CATEGORY: Technical (dependency risk)
TRIGGER: ERCOT infrastructure failure, network issues, rate limiting
IMPACT AREA: Gulfstream product non-functional, customer SLA breach
DETECTION: Health check failures, customer complaints, error rate spike
LIKELIHOOD: Low (ERCOT reports 99.9% uptime), but non-zero

```

---

## STEP 2: ASSESS HAZARDS

### Risk Assessment Matrix

**Formula**: Risk Level = Probability × Severity

#### Probability Scale

```

FREQUENT (5):    Occurs often (>1× per month)
LIKELY (4):      Occurs several times (1× per quarter)
OCCASIONAL (3):  Occurs sometimes (1× per year)
SELDOM (2):      Unlikely but possible (1× per 5 years)
UNLIKELY (1):    Rare, almost impossible (<1× per 10 years)

```

#### Severity Scale

```

CATASTROPHIC (5): Business failure, total loss, unrecoverable
CRITICAL (4):     Severe damage, major loss, long recovery (>30 days)
MODERATE (3):     Significant impact, manageable loss, short recovery (7-30 days)
MINOR (2):        Limited impact, small loss, immediate recovery (<7 days)
NEGLIGIBLE (1):   Minimal impact, no real loss, instant recovery

```

#### Risk Level Matrix

| Probability ↓ / Severity → | Negligible (1) | Minor (2) | Moderate (3) | Critical (4) | Catastrophic (5) |
|----------------------------|----------------|-----------|--------------|--------------|------------------|
| **Frequent (5)**           | MODERATE (5)   | HIGH (10) | EXTREME (15) | EXTREME (20) | EXTREME (25)     |
| **Likely (4)**             | LOW (4)        | MODERATE (8) | HIGH (12) | EXTREME (16) | EXTREME (20)     |
| **Occasional (3)**         | LOW (3)        | MODERATE (6) | MODERATE (9) | HIGH (12)   | EXTREME (15)     |
| **Seldom (2)**             | LOW (2)        | LOW (4)   | MODERATE (6) | MODERATE (8) | HIGH (10)        |
| **Unlikely (1)**           | LOW (1)        | LOW (2)   | LOW (3)      | MODERATE (4) | MODERATE (5)     |

**Risk Levels**:

- **EXTREME (15-25)**: Unacceptable risk, STOP immediately

- **HIGH (10-14)**: Serious risk, mitigate before proceeding

- **MODERATE (5-9)**: Manageable risk, have contingency plan

- **LOW (1-4)**: Acceptable risk, document and monitor

### Risk Assessment Template

```

HAZARD: [Name]
PROBABILITY: [1-5] [Unlikely/Seldom/Occasional/Likely/Frequent]

  - Rationale: [Why this probability score?]
SEVERITY: [1-5] [Negligible/Minor/Moderate/Critical/Catastrophic]

  - Rationale: [What's the worst-case impact?]
RISK LEVEL: [Probability × Severity = X] [LOW/MODERATE/HIGH/EXTREME]

```

**Example 1: EXTREME Risk**

```

HAZARD: Founder incapacitation (illness, accident)
PROBABILITY: 2 (Seldom) - Unlikely but possible

  - Rationale: Statistically rare, but sole founder = single point of failure
SEVERITY: 5 (Catastrophic) - Business halts entirely

  - Rationale: No one else can access systems, make decisions, serve customers
RISK LEVEL: 2 × 5 = 10 (HIGH, bordering EXTREME)

ACTION: MITIGATE BEFORE PROCEEDING (see Step 3)

```

**Example 2: MODERATE Risk**

```

HAZARD: ERCOT API unavailable 24+ hours
PROBABILITY: 2 (Seldom) - ERCOT reports 99.9% uptime

  - Rationale: Historical data shows rare but non-zero outages
SEVERITY: 3 (Moderate) - Gulfstream non-functional, but recoverable

  - Rationale: Customers inconvenienced, SLA breach, but data intact
RISK LEVEL: 2 × 3 = 6 (MODERATE)

ACTION: HAVE CONTINGENCY PLAN (see Step 3)

```

**Example 3: LOW Risk**

```

HAZARD: Minor UI bug in admin dashboard
PROBABILITY: 4 (Likely) - Bugs happen frequently in new features

  - Rationale: Active development, manual testing only (no automated)
SEVERITY: 1 (Negligible) - Cosmetic issue, no data impact

  - Rationale: Internal tool, founder can work around, fix in next sprint
RISK LEVEL: 4 × 1 = 4 (LOW)

ACTION: ACCEPT AND MONITOR (fix opportunistically)

```

---

## STEP 3: DEVELOP CONTROLS

### Control Strategies

#### 1. Avoid

**Strategy**: Eliminate the hazard entirely (don't do the risky thing)

**When to Use**: EXTREME or HIGH risk that can't be mitigated acceptably

**Example**:

```

HAZARD: Store customer credit cards directly (PCI compliance risk)
RISK LEVEL: EXTREME (Probability: Occasional, Severity: Catastrophic)
CONTROL: AVOID - Use Stripe (third-party payment processor)
OUTCOME: Risk eliminated (PCI compliance is Stripe's problem)

```

#### 2. Transfer

**Strategy**: Shift risk to third party (insurance, outsourcing, contracts)

**When to Use**: HIGH or MODERATE risk, specialized expertise needed

**Example**:

```

HAZARD: Data breach exposes customer PII
RISK LEVEL: HIGH (Probability: Seldom, Severity: Critical)
CONTROL: TRANSFER - Purchase cyber liability insurance ($1M coverage)
OUTCOME: Financial impact transferred to insurer

```

#### 3. Mitigate

**Strategy**: Reduce probability or severity (technical controls, process improvements)

**When to Use**: HIGH or MODERATE risk, acceptable residual risk

**Example**:

```

HAZARD: Founder incapacitation
RISK LEVEL: HIGH (Probability: Seldom, Severity: Catastrophic)
CONTROL: MITIGATE

  - Probability reduction: Health insurance, work-life balance

  - Severity reduction: Document critical processes, grant co-founder system access
OUTCOME: Severity reduced from Catastrophic → Critical (business survives 30 days)

```

#### 4. Accept

**Strategy**: Acknowledge risk, monitor, but take no action (risk acceptable)

**When to Use**: LOW or MODERATE risk, cost of mitigation > cost of risk

**Example**:

```

HAZARD: Minor UI bug in admin dashboard
RISK LEVEL: LOW (Probability: Likely, Severity: Negligible)
CONTROL: ACCEPT - Document bug, fix in next sprint (not urgent)
OUTCOME: Risk accepted, no immediate action

```

### Control Development Template

```

HAZARD: [Name]
RISK LEVEL: [LOW/MODERATE/HIGH/EXTREME]
CONTROL STRATEGY: [Avoid/Transfer/Mitigate/Accept]

CONTROLS:

1. [Specific action to reduce probability or severity]

2. [Backup control if primary fails]

3. [Monitoring to detect if risk materializes]

RESIDUAL RISK: [Risk level AFTER controls implemented]
COST: $[implementation cost] + $[ongoing cost/month]
TIMELINE: [How long to implement controls?]
RESPONSIBLE: [Who owns this mitigation?]

```

**Example: Founder Incapacitation Mitigation**

```

HAZARD: Founder incapacitation (illness, accident, burnout)
RISK LEVEL: HIGH (10: Seldom × Catastrophic)
CONTROL STRATEGY: MITIGATE (can't avoid, can reduce severity)

CONTROLS:

1. REDUCE SEVERITY:

   - Document all critical processes (deploy, customer support, billing)

   - Grant co-founder/advisor emergency access to systems (AWS, Stripe, domain)

   - Maintain customer contact list + communication template

   - Set up auto-response for emergencies ("Unexpected delay, updates in 48h")


2. REDUCE PROBABILITY:

   - Health insurance (catastrophic coverage minimum)

   - Work sustainable hours (max 60h/week, enforce 1 day off)

   - Regular exercise, sleep, stress management (track weekly)


3. MONITORING:

   - Weekly health check-in (workload, stress level, warning signs)

   - Deadman switch (weekly check-in with co-founder, alert if missed)

RESIDUAL RISK: MODERATE (6: Seldom × Moderate)

  - Severity reduced: Catastrophic → Moderate (business survives 30-60 days vs. immediate halt)

  - Probability unchanged: Seldom (still unlikely)

COST: $500/month (health insurance) + 4 hours (documentation)
TIMELINE: 2 weeks (documentation + access setup)
RESPONSIBLE: Founder (self), Co-founder (backup access)

```

---

## STEP 4: IMPLEMENT CONTROLS

### Implementation Checklist

**Before Implementation**:

- [ ] Controls defined clearly (who, what, when, how)

- [ ] Responsible party assigned and acknowledged

- [ ] Resources allocated (budget, time)

- [ ] Success criteria defined (how do we know it worked?)

**During Implementation**:

- [ ] Follow implementation plan (don't cut corners)

- [ ] Document as you go (runbooks, process docs)

- [ ] Test controls (simulate failure, verify mitigation works)

- [ ] Communicate changes (team, customers, stakeholders)

**After Implementation**:

- [ ] Verify controls in place (audit, inspection)

- [ ] Train relevant parties (how to use controls)

- [ ] Document residual risk (what's left after mitigation?)

- [ ] Set monitoring cadence (weekly, monthly, quarterly?)

### Implementation Template

```

CONTROL: [Name]
STATUS: [Not Started / In Progress / Completed / Verified]

PLAN:

- Step 1: [Action] (Owner: [name], Due: [date])

- Step 2: [Action] (Owner: [name], Due: [date])

- Step 3: [Action] (Owner: [name], Due: [date])

VERIFICATION:

- Test 1: [How to verify control works?] (Pass/Fail: [result])

- Test 2: [Simulate failure, control activates?] (Pass/Fail: [result])

DOCUMENTATION:

- Location: [Where is this documented? e.g., docs/runbooks/incident-response.md]

- Training: [Who needs to know this? When trained?]

MONITORING:

- Frequency: [How often to check control still works?]

- Responsibility: [Who monitors this?]

- Alert: [What triggers re-assessment?]

```

**Example: ERCOT API Failure Mitigation**

```

CONTROL: Circuit Breaker for ERCOT API Calls
STATUS: Completed (2025-11-12)

PLAN:

- Step 1: Implement circuit breaker library (pybreaker) [Founder, 2025-11-10] ✅

- Step 2: Add Redis cache for last-known-good ERCOT data [Founder, 2025-11-11] ✅

- Step 3: Configure fallback to cached data when circuit open [Founder, 2025-11-12] ✅

- Step 4: Add customer-facing "delayed data" warning [Founder, 2025-11-12] ✅

VERIFICATION:

- Test 1: Simulate ERCOT API timeout → Circuit opens, fallback activates ✅ PASS

- Test 2: Cache returns 15-min-old data → UI shows "delayed data" warning ✅ PASS

- Test 3: ERCOT API recovers → Circuit auto-closes after 60s ✅ PASS

DOCUMENTATION:

- Location: docs/architecture/circuit-breaker.md

- Runbook: docs/runbooks/ercot-api-failure.md

- Training: Founder (developer), no additional training needed (solo)

MONITORING:

- Frequency: Real-time (circuit breaker state in Datadog)

- Responsibility: Founder (on-call)

- Alert: Circuit open >30 minutes → Slack warning

```

---

## STEP 5: SUPERVISE & EVALUATE

### Ongoing Risk Monitoring

**Daily**:

- System health checks (uptime, latency, error rates)

- Burn tracking (flag anomalies immediately)

**Weekly**:

- Team health check (workload, stress, blockers)

- Customer feedback review (satisfaction, complaints)

- Incident log review (any new risks surfaced?)

**Monthly**:

- Financial review (burn vs. budget, revenue vs. forecast)

- Risk register update (new hazards, changed probabilities/severities)

- Control effectiveness audit (are mitigations working?)

**Quarterly**:

- Comprehensive risk assessment (re-run full Compliance Framework process)

- Strategic risk review (market, competitive, regulatory changes)

- Lessons learned (what surprised us? what can we predict better?)

### Risk Register

**Maintain a Living Document**:

```

PNKLN RISK REGISTER
===================
Last Updated: [Date]

[RISK-001] Founder Incapacitation

  - Level: MODERATE (was HIGH, mitigated)

  - Controls: Documentation, emergency access, health insurance

  - Status: MONITORED (weekly health check-in)

  - Next Review: [Date]

[RISK-002] ERCOT API Failure

  - Level: MODERATE (6: Seldom × Moderate)

  - Controls: Circuit breaker, cache, fallback

  - Status: MONITORED (real-time, Datadog)

  - Next Review: [Date]

[RISK-003] Revenue Shortfall (Gulfstream)

  - Level: HIGH (12: Occasional × Critical)

  - Controls: Diversified customer pipeline, monthly forecasting

  - Status: ACTIVE (Q4 2025 critical period)

  - Next Review: [Date]

[RISK-004] Judge 6 Performance Degradation

  - Level: LOW (4: Occasional × Minor)

  - Controls: Monitoring, performance budget, optimization playbook

  - Status: MONITORED (weekly p99 tracking)

  - Next Review: [Date]

```

### Control Effectiveness Review

**Questions to Ask Monthly**:

1. **Did controls work?** (Any incidents where controls prevented/mitigated impact?)

2. **Did controls fail?** (Any incidents where controls should have activated but didn't?)

3. **Are controls still relevant?** (Has risk landscape changed?)

4. **Are controls cost-effective?** (Cost of control < expected loss?)

**Example Review**:

```

CONTROL: Circuit Breaker for ERCOT API
REVIEW DATE: 2025-12-01

EFFECTIVENESS:

- Activated 2 times in November (ERCOT API timeouts)

- Fallback to cache worked as designed (customer impact: minimal)

- No customer complaints related to stale data

CHANGES NEEDED:

- Increase cache TTL from 15 min → 30 min (customer feedback: delays acceptable)

- Add proactive alert to ERCOT when circuit opens (improve resolution time)

COST-BENEFIT:

- Implementation cost: $500 (4 hours dev time)

- Ongoing cost: $50/month (Redis cache)

- Estimated prevented loss: $2,000/incident × 2 = $4,000

- ROI: 8× (cost-effective ✅)

NEXT REVIEW: 2026-03-01 (quarterly)

```

---

## KILL-SWITCH PROTOCOLS

### Definition

**Kill-Switch**: Pre-defined criteria that trigger immediate halt or rollback of operations.

**Purpose**: Prevent catastrophic losses by acting fast when risk materializes.

### Financial Kill-Switches

**KS-F1: Burn Overrun**

```

TRIGGER: Monthly burn >$12,000 for 2 consecutive months
ACTION:

  1. Immediate spending freeze (all discretionary spend)

  2. Emergency team meeting (identify cuts)

  3. Activate BOOTSTRAP_GATES contingency plan

  4. Weekly burn tracking until burn <$10K/month

```

**KS-F2: Revenue Collapse**

```

TRIGGER: Monthly revenue <50% of forecast for 2 consecutive months
ACTION:

  1. Customer outreach (understand churn/non-conversion)

  2. Pivot assessment (is product-market fit broken?)

  3. Reduce burn to minimum viable (defer all non-critical)

  4. 30-day decision: Fix, pivot, or wind down

```

**KS-F3: Runway Critical**

```

TRIGGER: Runway drops below 3 months
ACTION:

  1. Emergency mode (halt all development except revenue-critical)

  2. Aggressive revenue acceleration (discounts, prepayment offers)

  3. Co-founder/advisor consultation (options assessment)

  4. Prepare wind-down plan (if revenue acceleration fails)

```

### Technical Kill-Switches

**KS-T1: Latency Breach**

```

TRIGGER: p99 latency >200ms for Judge 6 for 7 consecutive days
ACTION:

  1. Immediate rollback of last 3 deploys

  2. Emergency optimization sprint (5-day max)

  3. If optimization fails → defer features, focus on performance

  4. If still failing → escalate to architectural review

```

**KS-T2: Downtime Crisis**

```

TRIGGER: System downtime >15 minutes consecutive OR uptime <99% in 7 days
ACTION:

  1. Activate incident response (diagnose, mitigate, resolve)

  2. Customer communication (status page, email if >30 min)

  3. Postmortem within 48 hours (root cause, prevention)

  4. If recurring → architectural changes required

```

**KS-T3: Security Breach**

```

TRIGGER: Unauthorized access detected OR critical CVE (CVSS ≥9.0) in production
ACTION:

  1. Immediate containment (isolate affected systems)

  2. Assess scope (data accessed, systems compromised)

  3. Patch/remediate within 24 hours (critical CVE)

  4. Customer notification (if PII exposed, within 72 hours per GDPR)

  5. Postmortem + security audit

```

### Market Kill-Switches

**KS-M1: Product-Market Misfit**

```

TRIGGER: Customer conversion <10% after 50 trials OR churn >25%/month
ACTION:

  1. Deep customer research (why not converting/churning?)

  2. Pivot assessment (can we fix with features, or fundamental misfit?)

  3. 60-day validation window (try fixes, measure improvement)

  4. If no improvement → major pivot or wind down

```

**KS-M2: Competitive Disruption**

```

TRIGGER: Competitor launches superior product OR undercuts pricing by 50%+
ACTION:

  1. Competitive analysis (what's their advantage?)

  2. Differentiation strategy (can we compete on value, not price?)

  3. Customer retention focus (lock in current customers)

  4. 90-day assessment (can we survive? do we pivot?)

```

### Team Kill-Switches

**KS-TM1: Key Person Departure**

```

TRIGGER: Founder incapacitated >30 days OR critical team member quits
ACTION:

  1. Activate emergency access protocols

  2. Customer communication (transparency + reassurance)

  3. Assess continuity (can we operate without key person?)

  4. If not → pause growth, stabilize, recruit replacement

```

**KS-TM2: Burnout Crisis**

```

TRIGGER: Team member working >70 hours/week for 4 consecutive weeks
ACTION:

  1. Immediate workload reduction (defer non-critical)

  2. Health check-in (mental, physical, sustainability)

  3. Scope cut (what can we NOT do?)

  4. If persistent → hire support (contractor, part-time) or pivot to sustainable pace

```

### Legal Kill-Switches

**KS-L1: Compliance Violation**

```

TRIGGER: Regulatory notice (GDPR, CCPA, energy market rules) OR potential IP infringement
ACTION:

  1. Legal counsel consultation (within 24 hours)

  2. Remediation plan (cure period if available)

  3. Customer impact assessment (notification required?)

  4. If material risk → pause operations until resolved

```

---

## RISK FRAMEWORK INTEGRATION

**RISK_FRAMEWORK** provides:

- **BRAKES** for **JR_ENGINE** (risk assessment informs decision constraints)

- **Monitoring inputs** for **BOOTSTRAP_GATES** (financial risk tracking)

- **Failure modes** for **TECHNICAL_SLA** (what could go wrong technically?)

**Workflow**:

1. Decision proposed

2. Run Compliance Framework: Identify hazards → Assess → Develop controls

3. Risk level informs JR_ENGINE BRAKES (EXTREME → REJECT, HIGH → CONDITIONAL, etc.)

4. Implement controls, monitor via risk register

5. Kill-switches pre-defined, auto-trigger if criteria met

---

## EXAMPLES

### Example 1: HIGH Risk Decision (Mitigate Before Proceeding)

```

DECISION: Launch Gulfstream ERCOT Integration

STEP 1: IDENTIFY HAZARDS

- ERCOT API dependency (technical)

- Revenue assumptions unvalidated (market)

- Burn impact if customers don't convert (financial)

STEP 2: ASSESS HAZARDS
[HAZARD 1: ERCOT API Failure]

- Probability: 2 (Seldom) - 99.9% uptime historical

- Severity: 3 (Moderate) - Product non-functional, but recoverable

- Risk Level: 2 × 3 = 6 (MODERATE)

[HAZARD 2: Revenue Shortfall]

- Probability: 3 (Occasional) - Unvalidated market, 30-50% miss likely

- Severity: 4 (Critical) - Burns capital, threatens runway

- Risk Level: 3 × 4 = 12 (HIGH)

STEP 3: DEVELOP CONTROLS
[HAZARD 1: ERCOT API]

- Strategy: MITIGATE

- Controls: Circuit breaker, cache, fallback, customer communication

- Residual Risk: LOW-MODERATE (6 → 4)

[HAZARD 2: Revenue Shortfall]

- Strategy: MITIGATE

- Controls:

  1. Validate 16-customer pipeline BEFORE committing $8K spend

  2. Phased launch (10 beta → measure conversion → expand if >20%)

  3. Monthly revenue tracking, kill-switch if <50% forecast for 2 months

- Residual Risk: MODERATE (12 → 6)

STEP 4: IMPLEMENT CONTROLS

- ✅ Circuit breaker implemented (2025-11-12)

- ✅ Customer pipeline validated (16 warm leads, 8 LOIs)

- ✅ Phased launch plan documented

- ✅ Monthly revenue tracking cadence set

STEP 5: SUPERVISE & EVALUATE

- Monthly: Revenue vs. forecast (kill-switch if <50%)

- Weekly: ERCOT API uptime (circuit breaker monitoring)

- Quarterly: Risk register update (re-assess probabilities)

JR_ENGINE DECISION: RECOMMEND (with controls)
RATIONALE: HIGH risk mitigated to MODERATE, controls in place, monitoring active

```

### Example 2: EXTREME Risk Decision (REJECT)

```

DECISION: Accept Single Customer Representing 60% of Revenue

STEP 1: IDENTIFY HAZARDS

- Customer concentration risk (market)

- Revenue collapse if customer churns (financial)

STEP 2: ASSESS HAZARDS
[HAZARD: Customer Churn]

- Probability: 3 (Occasional) - All customers eventually churn

- Severity: 5 (Catastrophic) - 60% revenue loss = business failure

- Risk Level: 3 × 5 = 15 (EXTREME)

STEP 3: DEVELOP CONTROLS

- Strategy: AVOID (don't take this customer at this concentration)

- Alternative 1: Cap single customer at 25% revenue (reject excess)

- Alternative 2: Delay acceptance until diversified (10+ customers)

- Alternative 3: Accept, but accelerate diversification (6 new customers in 90 days)

STEP 4: IMPLEMENT CONTROLS
[CONTROL: AVOID]

- Decision: Reject customer OR cap contract size

- Communication: "We'd love to work with you, but our risk framework prevents over-concentration. We can start with [25% of proposed contract size], and grow as we diversify."

JR_ENGINE DECISION: REJECT (as proposed)
ALTERNATIVE: Accept at 25% revenue concentration, diversify aggressively
RATIONALE: EXTREME risk unacceptable, AVOID strategy required

```

---

## MAINTENANCE

**Update Schedule**:

- **Weekly**: Risk register (new hazards, status changes)

- **Monthly**: Control effectiveness review

- **Quarterly**: Full Compliance Framework re-assessment (all risks)

- **Ad-hoc**: After major incidents (update hazards, controls)

**Change Log**:

- Track changes to risk levels, controls, kill-switch criteria

- Document rationale (why did MODERATE become HIGH?)

- Version control in Cor_vX.md

---

## QUICK REFERENCE

**Compliance Framework Steps**:

1. Identify → 2. Assess → 3. Develop Controls → 4. Implement → 5. Supervise

**Risk Levels**:

- EXTREME (15-25): STOP immediately

- HIGH (10-14): Mitigate before proceeding

- MODERATE (5-9): Have contingency

- LOW (1-4): Accept and monitor

**Control Strategies**:

- AVOID: Eliminate hazard

- TRANSFER: Shift to third party

- MITIGATE: Reduce probability or severity

- ACCEPT: Monitor, no action

**Kill-Switches**:

- Financial: Burn >$12K/mo (2 months), revenue <50% forecast (2 months), runway <3 months

- Technical: p99 >200ms (7 days), uptime <99% (7 days), security breach

- Market: Conversion <10% (50 trials), churn >25%/month

- Team: Key person >30 days, burnout >70h/week (4 weeks)

---

**END RISK_FRAMEWORK.md**
