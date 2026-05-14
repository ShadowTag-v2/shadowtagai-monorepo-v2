# ADR 001: Enforcement-First Agent Architecture

**Status:** ✅ ACCEPTED

**Date:** 2025-11-15

**Decision Makers:** Pnkln Engineering Team

**Context:** Thread rollup from agent architecture analysis and decision package

---

## Context and Problem Statement

Indie hacker "start simple" agent frameworks lack enforcement layers, creating liability in regulated verticals (finance, healthcare, defense). Enterprises need enforceable governance with audit trails that are defensible in court.

**Key Gap Identified:** No agent framework provides compliance enforcement as a first-class feature.

**Revenue Opportunity:** $997/mo prompt templates (godofprompt.ai) vs $9,970/mo governance-as-service.

---

## Decision

Implement **enforcement-first agent architecture** with mandatory validation gates:

1. **JR Engine** (Purpose/Reasons/Brakes validator) - <500μs latency
2. **Judge #6 Lite** (Rule-based enforcement) - <90ms p99 SLA
3. **Agent Pattern** (Integrated enforcement workflow)
4. **First Use Case:** Compliance-First SDR Agent (GDPR/CAN-SPAM)

---

## Architecture Pattern

```python
def pnkln_agent_pattern():
    task = parse_user_intent()
    jr_decision = jr_engine.validate(task)  # Purpose/Reasons/Brakes

    if jr_decision.brake_triggered:
        return escalate_to_human(jr_decision.audit)

    result = execute(task, guardrails=jr_decision.constraints)

    if not judge_six.verify(result, sla_p99=90):
        return rollback_and_log(result)

    return result + shadowtag_v2.watermark()
```

---

## Technical Stack

| Component | Technology | Reasoning |
|-----------|-----------|-----------|
| **State Management** | LangGraph | Industry standard for agent state |
| **Inference** | Gemini Flash | 40% LLM allocation, $0.50/1M tokens |
| **Enforcement** | Judge #6 Lite | Rule-based (pre-ML), <90ms target |
| **Validation** | JR Engine | ATP 5-19 risk assessment, <500μs |
| **Memory** | ChromaDB | Self-hosted, $0 cost |
| **Edge Compute** | CloudFlare Workers | <50ms latency target |

---

## Revenue Model

| Tier | Price | Features |
|------|-------|----------|
| **Base** | $297/mo | Core enforcement, basic audit trails |
| **Usage** | $0.10/lead | Validated leads (Compliance SDR) |
| **White-glove** | $997/mo | Human review of audit trails |
| **Enterprise** | $9,970/mo | Custom rules + legal review |

### Target Customers
- SaaS companies with EU customers (GDPR fear)
- US healthcare (HIPAA compliance)
- Financial services (SOC2/audit requirements)

### LTV/CAC Projection
- **Churn:** <5%/mo (compliance = non-negotiable)
- **LTV:** $297 × 18mo = $5,346 base tier
- **CAC:** <$1,000 (outbound to YC batch)
- **Ratio:** 5.3:1 (exceeds 4:1 bootstrap gate)

---

## Bootstrap Constraints

| Constraint | Target | Status |
|------------|--------|--------|
| **Monthly Burn** | $60-65K | Active |
| **ROI Gate** | ≥3× (18mo) | Must meet |
| **LTV:CAC Gate** | ≥4:1 (12mo) | Must meet |
| **SLA Gate** | p99 ≤90ms | Must meet |
| **Security Gate** | 100% | Mission-critical |

### Agent Monthly Costs
- Gemini Flash inference: $800-1,200/mo
- ChromaDB hosting: $0 (self-hosted on GKE)
- CloudFlare Workers: $200-400/mo
- Judge #6 rules maintenance: $0 (no ML training yet)
- **TOTAL:** $1,000-1,600/mo operational cost

### Break-Even Analysis
- **Need:** 4-6 customers at $297/mo base tier
- **Or:** 10,000-16,000 validated leads at $0.10/lead
- **Timeline:** 30-45 days (aggressive outbound)

---

## First Use Case: Compliance-First SDR Agent

### Job To Be Done
Generate B2B leads without GDPR/CAN-SPAM violations

### Workflow
1. User query: "Find 100 German fintech CTOs"
2. JR Engine validates budget/purpose
3. Agent scrapes LinkedIn/Apollo/Clearbit
4. Judge #6 filters personal emails, flags EU contacts
5. Output: N approved + M blocked + audit PDF

### Pricing
- $0.10/approved lead
- Block EU personal emails (GDPR risk)
- Flag EU contacts without consent (needs review)

### Timeline
- 7-day MVP sprint
- Target: First paying customer

---

## JR Engine: Purpose/Reasons/Brakes Validator

**Target Latency:** <500μs

**Method:** ATP 5-19 risk assessment (Probability × Severity → Level)

**Function:** Validates all agent actions before execution

### Components

1. **Purpose**
   - Intent and goal of action
   - Business value
   - Customer attribution
   - Cost estimate
   - Expected outcome

2. **Reasons**
   - Justification
   - Risk probability (0.0-1.0)
   - Risk severity (0.0-1.0)
   - Mitigation strategy

3. **Brakes**
   - Security violation
   - Compliance violation
   - Budget exceeded
   - Unauthorized action
   - Data privacy risk
   - Rate limit exceeded

### Risk Levels (ATP 5-19)

| Risk Score | Level | Action |
|------------|-------|--------|
| ≥0.8 | Extremely High | Requires human approval |
| ≥0.6 | High | Requires mitigation strategy |
| ≥0.4 | Moderate | Enhanced logging |
| ≥0.2 | Low | Standard execution |
| <0.2 | Extremely Low | Fast-path execution |

---

## Judge #6 Lite: Rule-Based Enforcement

**Target Latency:** <50ms (production <90ms p99)

**Coverage:**
- CAN-SPAM regex
- GDPR checks
- Budget constraints
- Content policies

**Output:** Exportable PDF compliance report

### Compliance Rules

#### CAN-SPAM
- [x] Unsubscribe link required
- [x] Physical mailing address required
- [x] Non-deceptive subject lines

#### GDPR
- [x] Explicit consent for EU PII
- [x] Data minimization
- [x] Personal email filtering

#### Budget
- [x] Cost limit enforcement
- [x] Human approval thresholds

### Violation Severity

| Severity | Action | Example |
|----------|--------|---------|
| **Critical** | Block execution, legal risk | EU PII without consent |
| **High** | Block execution, compliance risk | Missing unsubscribe link |
| **Medium** | Warn, log, may execute | Personal email without consent |
| **Low** | Log only | Minor content issues |

---

## Competitive Moat

### Defensibility
1. **Audit Trails:** Exportable PDF compliance reports (defensible in court)
2. **Legal Expertise:** Erik's JD matters for enterprise trust
3. **Enforcement-First:** Can't be added as afterthought
4. **Compliance Artifacts:** SOC2/HIPAA/GDPR documentation

### Commoditization Risk
- **Window:** 12-18 months before Anthropic/OpenAI add "compliance mode"
- **Mitigation:** Move fast, win enterprise contracts, build switching costs

---

## Technical Debt Identified

### Missing Components
- [ ] Cold-start handling (no training data for Judge #6 ML)
- [ ] Memory strategy (Redis short-term + Postgres audit trail)
- [ ] Multi-tenancy (customer-specific enforcement rules)
- [ ] Legal review (Pnkln liability if enforcement fails?)
- [ ] CI/CD pipeline
- [ ] Monitoring and alerting
- [ ] PDF export for audit reports (placeholder implementation)

### Integration Points
- [ ] LinkedIn Sales Navigator API
- [ ] Apollo.io API
- [ ] Clearbit API
- [ ] LangGraph installation
- [ ] Production database setup

---

## Alternative Approaches Considered

1. **Build Judge #6 as Zapier integration** (no agent, pure middleware)
   - PRO: Faster time-to-market
   - CON: Lower margins, commoditized

2. **Sell audit trail export as standalone SaaS** ($49/mo, volume play)
   - PRO: Simple, low CAC
   - CON: Low LTV, high churn

3. **White-label enforcement to existing platforms** (B2B2B model)
   - PRO: Leverage existing distribution
   - CON: Complex partnerships, slower

4. **Skip to enterprise** ($100K+ contracts, slower but higher margin)
   - PRO: High LTV, low churn
   - CON: Long sales cycles, high CAC

**Decision:** Start with Compliance SDR Agent (7-day MVP), validate market, then expand.

---

## Consequences

### Positive
- **Differentiated positioning:** Only enforcement-first agent framework
- **Enterprise trust:** Audit trails = compliance artifacts
- **Revenue arbitrage:** 10× pricing vs templates
- **Low churn:** Compliance = non-negotiable (hard to leave)
- **Defensible moat:** 12-18 month window

### Negative
- **Complex sales:** Requires compliance pain point
- **Legal liability:** If enforcement fails, Pnkln may be liable
- **Commoditization risk:** Big players may add compliance mode
- **Technical debt:** Many missing components (multi-tenancy, ML, etc.)

### Neutral
- **Bootstrap constraints:** Must hit 4-6 customers in 30-45 days
- **SLA pressure:** <90ms p99 is aggressive for rule engine
- **Operational cost:** $1,000-1,600/mo requires break-even focus

---

## Kill Decision Criteria

**Proceed if:**
- [ ] First customer within 7 days of MVP launch
- [ ] 3+ customers within 30 days
- [ ] LTV:CAC ≥4:1 after 90 days
- [ ] p99 latency <90ms maintained

**Pivot if:**
- [ ] No customers after 14 days
- [ ] CAC >$2,000 (2× target)
- [ ] Churn >10%/mo

**Kill if:**
- [ ] No customers after 30 days
- [ ] LTV:CAC <2:1 after 90 days
- [ ] Legal liability incident
- [ ] Security breach (mission abort)

---

## Next Steps

1. **Immediate (Days 1-7):**
   - [x] Implement JR Engine
   - [x] Implement Judge #6 Lite
   - [x] Implement Agent Pattern
   - [x] Implement Compliance SDR Agent
   - [ ] Write tests (unit + integration)
   - [ ] Set up CI/CD
   - [ ] Deploy MVP

2. **Short-term (Days 8-30):**
   - [ ] Integrate real lead sources (LinkedIn, Apollo)
   - [ ] Build PDF audit export
   - [ ] Launch to first customer
   - [ ] Measure LTV/CAC
   - [ ] Iterate on pricing

3. **Medium-term (Days 31-90):**
   - [ ] Add multi-tenancy
   - [ ] Build customer dashboard
   - [ ] Implement ML training for Judge #6
   - [ ] Scale to 10+ customers
   - [ ] Validate revenue model

---

## References

- Thread Rollup: AGENT ARCHITECTURE DECISION PACKAGE
- Revenue Analysis: godofprompt.ai ($997/mo) vs Pnkln ($9,970/mo)
- Technical Stack: LangGraph + Gemini Flash + Judge #6 Lite
- Bootstrap Constraints: $60-65K burn, 3× ROI, 4:1 LTV:CAC
- ATP 5-19: Army risk assessment methodology
- GDPR: EU General Data Protection Regulation
- CAN-SPAM: US email marketing law
- HIPAA: US healthcare data protection law

---

**Validation Layer:**

## Critique
- Restart prompt may be too dense for non-technical readers
- Missing specific file structure for 7-day MVP
- Assumption: Customer pain (GDPR fear) is strong enough to pay 10×

## Weaknesses
- No contingency if first 10 customers reject pricing
- Competitive moat defensibility window (12-18mo) is aggressive
- Technical debt list incomplete (no CI/CD, monitoring, alerting)
- Revenue projections assume 30-45 day sales cycle (may be 90-120 days)

## Assumptions
- Enterprises will trust startup for compliance (high-risk vendor eval)
- Judge #6 Lite rules can achieve 90%+ compliance without ML
- Erik has time for 7-day sprint while maintaining $60-65K burn ops
- YC batch outbound will convert at >5% (industry standard is 1-3%)

## What Could Be Wrong
- Agent use case commoditizing faster than we can ship
- Compliance pain isn't monetizable (legal teams buy, not CFOs)
- Enforcement creates false negatives → customer churn (too strict)
- Bootstrap constraints make 7-day sprint impossible (context switching)

---

**Status:** ✅ IMPLEMENTED

**Last Updated:** 2025-11-15
