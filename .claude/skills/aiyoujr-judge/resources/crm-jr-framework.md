# CRM-JR Decision Framework

**Purpose:** Enhanced decision-making with 160-IQ board + Treadstone/Blackbriar analytical rigor
**Integration:** Works alongside AiYouJR Purpose • Reasons • Brakes gates
**Activation:** Automatic for strategic decisions (>$50k investment or >3 month timeline)

---

## Framework Overview

CRM-JR combines classical decision analysis with enhanced pattern recognition:

```
┌────────────────────────────────────────────────────────┐
│          CONTEXT (Current Reality Matrix)              │
│  What is actually happening right now?                 │
│  • Market conditions                                   │
│  • Resource availability                               │
│  • Competitive landscape                               │
│  • Technical constraints                               │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│          REASONS (Multi-Dimensional Analysis)          │
│  Why should we act? What's the evidence?               │
│  • Financial (ROI, NPV, LTV:CAC)                       │
│  • Strategic (VRIO, Blue Ocean, Value Stick)           │
│  • Risk (Monte Carlo, Army RM Stage IV)                │
│  • Competitive (Porter's 5 Forces)                     │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│          MENTAL MODELS (Pattern Recognition)           │
│  What frameworks apply? What analogies work?           │
│  • Second-order thinking                               │
│  • Inversion (what could go wrong?)                    │
│  • Circle of competence                                │
│  • Opportunity cost                                    │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│          JUDGMENT (Decision Synthesis)                 │
│  What should we do?                                    │
│  • GO / NO-GO / CONDITIONAL                            │
│  • Confidence level (0-100%)                           │
│  • Kill-switch triggers                                │
│  • Validation milestones                               │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│          REVERSAL (Contingency Planning)               │
│  How do we get out if this fails?                     │
│  • Rollback procedures                                 │
│  • Blast radius containment                            │
│  • Learning capture (post-mortem)                      │
└────────────────────────────────────────────────────────┘
```

---

## 1. Context Analysis

### Current Reality Matrix

**Objective:** Establish ground truth before making decisions

#### Four Quadrants

```
                 Known                    Unknown
        ┌──────────────────┬──────────────────────┐
  Known │  FACTS           │  QUESTIONS           │
        │  (We know them)  │  (We know to ask)    │
        ├──────────────────┼──────────────────────┤
Unknown │  INSIGHTS        │  BLINDSPOTS          │
        │  (Discoverable)  │  (Unknown unknowns)  │
        └──────────────────┴──────────────────────┘
```

#### Example: Adding MFA to ActiveShield

**FACTS (Known Knowns):**
- Current auth: Username/password only
- Enterprise customers asking for MFA (12 requests in Q4)
- Competitors offer MFA (Auth0, Okta, etc.)
- Team has OAuth 2.0 experience (implemented for PNKLN API)

**QUESTIONS (Known Unknowns):**
- Will customers pay premium for MFA? (needs pricing research)
- What adoption rate in first 90 days? (needs beta validation)
- Which MFA methods to support? (SMS, authenticator app, hardware tokens?)

**INSIGHTS (Unknown Knowns - Discoverable):**
- Customer support time saved from password resets (check historical tickets)
- Reduced security incidents (benchmark against industry data)
- Competitive win rate improvement (ask sales team)

**BLINDSPOTS (Unknown Unknowns - High Risk):**
- Regulatory changes requiring MFA (monitor compliance landscape)
- UX friction causing churn (needs user testing)
- Integration issues with enterprise SSO (technical discovery needed)

**Action:** Convert QUESTIONS → research tasks, INSIGHTS → data queries, BLINDSPOTS → monitoring/early warnings

---

## 2. Reasons Analysis (Multi-Dimensional)

### 2.1 Financial Layer (AiYouJR Reasons Gate)

Already covered in main SKILL.md:
- ROI ≥3× in 18 months
- LTV:CAC ≥4:1 in 12-18 months
- NPV ≥70% positive probability

### 2.2 Strategic Layer (MBA Frameworks)

**VRIO Analysis** (see resources/mba-frameworks.md for details):
- **V**aluable: Does MFA increase customer willingness to pay?
- **R**are: Do competitors lack this feature?
- **I**nimitable: Is our implementation defensible?
- **O**rganized: Can we execute effectively?

**Value Stick** (Buyer Value vs. Seller Cost):
```
Willingness to Pay (WTP):  $150/mo (with MFA)
Current Price:             $100/mo (without MFA)
→ Customer Surplus:        $50/mo (value capture opportunity)

Current Price:             $100/mo
Cost to Deliver:           $80/mo (including MFA dev amortized)
→ Firm Margin:            $20/mo (profitable)

Decision: Raise price to $120/mo for MFA tier
→ Customer Surplus: $30/mo (still attractive)
→ Firm Margin: $40/mo (2× improvement)
```

**Blue Ocean Strategy** (Create new demand):
- Eliminate: Password reset support costs
- Reduce: Manual security audit requirements
- Raise: Enterprise-grade security positioning
- Create: Compliance-as-a-feature (SOC2, HIPAA ready)

### 2.3 Competitive Layer (Porter's 5 Forces)

**Threat of New Entrants:** HIGH
- MFA is table stakes for enterprise SaaS
- Without it, losing deals to competitors

**Bargaining Power of Buyers:** MEDIUM
- Enterprise customers demand MFA
- SMBs less price-sensitive for security

**Threat of Substitutes:** LOW
- No substitute for strong authentication
- Build vs. buy decision (Auth0 integration vs. custom)

**Competitive Rivalry:** HIGH
- All major competitors offer MFA
- Differentiation: Ease of implementation, UX

**Bargaining Power of Suppliers:** LOW
- Open standards (TOTP, WebAuthn)
- Multiple vendor options (Twilio, Authy)

**Conclusion:** Must implement to remain competitive (defensive move)

### 2.4 Risk Layer (Monte Carlo + Army RM Stage IV)

See resources/monte-carlo-templates.md for detailed simulations.

**Additional CRM-JR Risk Factors:**

**Second-Order Consequences:**
- MFA increases security → reduces breaches → lower insurance premiums (bonus)
- MFA adds friction → some users disable → support burden increases (downside)
- Enterprise MFA → requires SSO integration → sales cycle lengthens (consideration)

**Inversion (Charlie Munger): What could make this fail?**
1. Poor UX design → users abandon signup
2. SMS delivery issues → support nightmare
3. Enterprise SSO conflicts → lose current customers
4. Dev timeline slips → miss Q1 sales season

**Mitigation:**
1. User testing with 20 beta customers before launch
2. Support authenticator apps first (no SMS dependency)
3. Compatibility testing with top 5 SSO providers
4. Agile sprints with weekly reviews (detect slippage early)

---

## 3. Mental Models (Pattern Recognition)

### Circle of Competence

**Inside Our Circle:**
- Backend authentication (implemented OAuth 2.0)
- Security best practices (AES-256, TLS 1.3, zero-trust)
- FastAPI/Node.js implementation
- SaaS pricing optimization

**Outside Our Circle:**
- Hardware token integration (YubiKey, etc.)
- Biometric authentication (fingerprint, Face ID)
- Quantum-resistant cryptography
- Mobile app development (if building native MFA app)

**Decision:** Stay inside circle. Use TOTP (time-based one-time passwords) with standard libraries. Defer hardware tokens to Phase 2 (when demand proven).

### Opportunity Cost

**Option A:** Build custom MFA ($50k dev cost)
**Option B:** Integrate Auth0 ($2k/mo SaaS fee)
**Option C:** Do nothing (lose enterprise deals)

**Analysis:**
```
Option A (Custom):
- Upfront: $50k
- Ongoing: $500/mo (maintenance)
- Control: Full
- Differentiation: High (customizable UX)
- Time to market: 3 months

Option B (Auth0):
- Upfront: $5k (integration)
- Ongoing: $2,000/mo (scales with users)
- Control: Limited
- Differentiation: Low (same as everyone)
- Time to market: 2 weeks

Option C (Nothing):
- Upfront: $0
- Ongoing: Lost deals ($50k/quarter)
- Control: N/A
- Differentiation: Negative (lacking feature)
- Time to market: N/A
```

**Opportunity Cost Calculation:**
```
If we choose Option B (Auth0):
- Opportunity cost = Option A benefits foregone
- Lost: Custom UX differentiation, long-term cost savings
- Gained: Faster time to market (11 weeks earlier)

3-Year Total Cost:
- Option A: $50k + ($500 × 36) = $68k
- Option B: $5k + ($2,000 × 36) = $77k
- Difference: $9k (Option A cheaper long-term)

But: Option B ships 11 weeks earlier → capture $50k in Q1 deals
Net advantage: $50k - $9k = $41k in favor of Option B

HOWEVER: Strategic consideration
- Year 4+: Option A saves $18k/year vs Option B
- If ActiveShield runs 5+ years, Option A wins
- If exiting in Y5-Y7, Option A delivers $90k-$126k savings

Decision: Option A (custom) aligns with PNKLN long-term strategy
```

### Second-Order Thinking

**First Order:** MFA improves security
**Second Order:** Improved security → insurance discounts → $5k/year savings
**Third Order:** MFA requirement → integrates with enterprise SSO → opens Fortune 500 market
**Fourth Order:** Fortune 500 customers → reference logos → easier Series A fundraising

**Unexpected Consequences:**
- MFA lockouts → support burden +15% (hire 0.5 FTE support)
- Compliance certifications now achievable → SOC2 audit → $25k additional cost
- Marketing angle: "Bank-grade security" → repositioning from SMB to enterprise

**Net Effect:** Second/third-order benefits (+$30k/year) outweigh first-order costs

---

## 4. Judgment (Decision Synthesis)

### Confidence Scoring (0-100%)

**Factors:**

| Factor | Weight | Score | Weighted |
|--------|--------|-------|----------|
| Financial ROI (≥3×) | 30% | 95% | 28.5% |
| Strategic Fit | 25% | 90% | 22.5% |
| Execution Capability | 20% | 85% | 17.0% |
| Market Timing | 15% | 80% | 12.0% |
| Risk Mitigation | 10% | 75% | 7.5% |
| **TOTAL** | 100% | | **87.5%** |

**Interpretation:**
- 90-100%: High confidence → GO
- 70-89%: Medium confidence → CONDITIONAL GO (with milestones)
- 50-69%: Low confidence → DEFER (more research needed)
- <50%: Very low confidence → NO-GO

**Decision: CONDITIONAL GO (87.5% confidence)**

### Validation Milestones

Before proceeding to full implementation:

**Phase 0: Validation (2 weeks, $5k budget)**
- [ ] Customer interviews: 10 enterprise prospects (confirm WTP for MFA)
- [ ] Technical spike: TOTP library integration (prove feasibility)
- [ ] Competitive analysis: Feature comparison (ensure parity)

**Gate: If ≥7/10 customers confirm WTP ≥$120/mo → Proceed to Phase 1**

**Phase 1: MVP (6 weeks, $20k budget)**
- [ ] Backend: TOTP generation/validation
- [ ] Frontend: QR code setup flow
- [ ] Beta: 20 customers (measure adoption rate)

**Gate: If ≥60% beta adoption in 30 days → Proceed to Phase 2**

**Phase 2: Enterprise (6 weeks, $25k budget)**
- [ ] SSO integration (Okta, Azure AD)
- [ ] Admin controls (enforce MFA, recovery codes)
- [ ] Launch to all customers

**Gate: If <15% churn in first 90 days → Full rollout**

### Kill-Switch Triggers (Auto-Abort)

Abort if ANY occur:

- [ ] Customer interviews: <5/10 confirm WTP (demand validation failed)
- [ ] Beta adoption: <40% in 30 days (low interest)
- [ ] Churn spike: >10% increase vs. baseline (UX friction too high)
- [ ] Timeline slip: >30% (6 weeks → 8+ weeks per phase)
- [ ] Security incident: MFA implementation has vulnerability (CVSS ≥7.0)
- [ ] Competitive shift: Major player makes MFA free (pricing power lost)

---

## 5. Reversal (Contingency Planning)

### Rollback Procedures

**Scenario 1: Beta goes poorly (adoption <40%)**

```markdown
IMMEDIATE (Day 1):
1. Pause beta expansion (cap at current 20 users)
2. User interviews: Why low adoption? (UX issues? Unclear value?)
3. Feature flag: Disable for new signups

WEEK 1-2:
4. Iterate on feedback (simplify setup flow? Better onboarding?)
5. Re-launch to same 20 users
6. Target: 70% adoption (higher bar after improvements)

IF STILL FAILS:
7. Full rollback: Remove MFA from product roadmap
8. Pivot: Integrate Auth0 instead (Option B)
9. Refund beta customers (goodwill)
```

**Scenario 2: Enterprise rollout causes churn spike**

```markdown
IMMEDIATE (within 24 hours):
1. Feature flag: Disable MFA requirement for existing customers
2. Grandfather old customers (no forced migration)
3. Support: Prioritize MFA-related tickets (SLA <2 hours)

WEEK 1:
4. Root cause analysis: What triggered churn? (specific SSO conflicts?)
5. Hotfixes: Address top 3 issues
6. Customer outreach: Personal calls to affected accounts

RECOVERY (Month 1):
7. Opt-in model: MFA optional, incentivize adoption ($10/mo discount)
8. Monitor churn: Should return to baseline within 60 days
9. Post-mortem: Update gates/thresholds to prevent repeat
```

### Learning Capture (Treadstone Protocol)

**After-Action Review Template:**

```markdown
# MFA Implementation - After-Action Review

**Date:** [Completion date]
**Outcome:** [GO / NO-GO / PARTIAL]
**Actual ROI:** [X.XX×] vs Projected: [Y.YY×]

## What Went Right

- [Specific success #1 + why]
- [Specific success #2 + why]
- [Specific success #3 + why]

## What Went Wrong

- [Specific failure #1 + root cause]
- [Specific failure #2 + root cause]
- [Specific failure #3 + root cause]

## Surprises (Unknown Unknowns Discovered)

- [Unexpected outcome #1]
- [Unexpected outcome #2]

## Gate Accuracy Analysis

| Gate | Projected | Actual | Variance | Notes |
|------|-----------|--------|----------|-------|
| ROI | 4.2× | 3.8× | -9.5% | Customer acquisition slower than expected |
| LTV:CAC | 5.1:1 | 6.2:1 | +21.6% | Lower churn than modeled (5% vs 10%) |
| Timeline | 12 weeks | 14 weeks | +16.7% | SSO integration took longer |

## Lessons Learned (Update Framework)

1. **Threshold Adjustments:**
   - Beta adoption gate: 60% → 70% (too lenient)
   - Timeline buffer: Add 20% for enterprise integrations

2. **New Kill-Switch Triggers:**
   - SSO compatibility: Test top 10 providers before beta (not just top 5)

3. **Process Improvements:**
   - Customer interviews: Do before dev (not during beta)

## Knowledge Transfer

- Document: SSO integration patterns (add to backend-dev-guidelines)
- Share: Customer WTP research findings (product team)
- Archive: Beta feedback (Notion: /MFA-Beta-Results)

**Reviewed By:** [Strategy team]
**Applied To:** [Next feature: X]
```

---

## CRM-JR vs AiYouJR: When to Use Each

### Use AiYouJR (Purpose • Reasons • Brakes) for:
- Standard features (<$50k, <3 months)
- Clear precedent (similar features shipped before)
- Low strategic ambiguity

### Use CRM-JR (Full Framework) for:
- Strategic decisions (>$50k investment, >3 month timeline)
- High uncertainty (entering new markets, unproven technology)
- Irreversible choices (architecture decisions, vendor lock-in)
- Board-level decisions (fundraising, exits, pivots)

### Combined Approach (Recommended for Major Features):

```markdown
STEP 1: Run AiYouJR Gates (fast filter)
→ If any gate fails, stop or pivot

STEP 2: If all gates pass, run CRM-JR deep dive
→ Context: Current Reality Matrix (fill blindspots)
→ Reasons: Multi-dimensional analysis (financial + strategic + risk)
→ Mental Models: Opportunity cost, second-order thinking
→ Judgment: Confidence scoring + validation milestones
→ Reversal: Contingency plans + learning capture

STEP 3: Decision
→ High confidence (>85%) + all gates pass → GO
→ Medium confidence (70-85%) → CONDITIONAL GO with milestones
→ Low confidence (<70%) → DEFER for more research
```

---

## Integration with Tools

### Automated CRM-JR Checks (Future: Hooks)

```bash
# When creating dev docs for features >$50k
# Automatically trigger CRM-JR framework questions

.claude/hooks/on-dev-docs-create.sh:
  if [ "$INVESTMENT" -gt 50000 ]; then
    echo "🧠 CRM-JR Framework activated (high-value decision)"
    echo "Please complete:"
    echo "1. Context: Current Reality Matrix (4 quadrants)"
    echo "2. Reasons: Multi-dimensional analysis"
    echo "3. Mental Models: Circle of competence + opportunity cost"
    echo "4. Judgment: Confidence scoring"
    echo "5. Reversal: Rollback procedures"
  fi
```

### Notion Integration (Decision Log)

Track all CRM-JR decisions in Notion database:

| Feature | Investment | Confidence | Decision | Actual ROI | Variance |
|---------|------------|------------|----------|------------|----------|
| MFA | $50k | 87.5% | COND GO | 3.8× | -9.5% |
| AI Contract Analysis | $120k | 72% | COND GO | (pending) | - |
| Custom CRM | $80k | 35% | NO-GO | N/A | N/A |

**Purpose:** Learn which confidence levels correlate with success (calibrate over time)

---

## Treadstone Enhancement: Pattern Recognition

Over time, build a pattern library:

**Successful Patterns:**
- Features with 80%+ confidence → 90% success rate
- Enterprise features → LTV:CAC beats projections by 20% (sticky customers)
- Security features → adoption slower but churn lower (long-term value)

**Anti-Patterns:**
- Features with <60% confidence → 70% failure rate (trust the numbers)
- Internal tools → ROI always overstated by 2-3× (adjust projections)
- "Nice-to-have" features → never launched (kill early or commit fully)

**Usage:** Before scoring new feature, check pattern library for similar decisions

---

## Quick Reference Card

```
CRM-JR DECISION CHECKLIST

□ CONTEXT
  □ Facts documented
  □ Questions converted to research tasks
  □ Insights gathered from data
  □ Blindspots identified + monitored

□ REASONS
  □ Financial (ROI, LTV:CAC, NPV)
  □ Strategic (VRIO, Value Stick, Blue Ocean)
  □ Competitive (Porter's 5 Forces)
  □ Risk (Monte Carlo, Army RM)

□ MENTAL MODELS
  □ Circle of competence check
  □ Opportunity cost calculated
  □ Second-order effects mapped
  □ Inversion analysis (what could go wrong?)

□ JUDGMENT
  □ Confidence score calculated
  □ Validation milestones defined
  □ Kill-switch triggers set

□ REVERSAL
  □ Rollback procedures documented
  □ Contingency plans ready
  □ Learning capture process defined

DECISION: _______________
CONFIDENCE: ___%
NEXT ACTION: _______________
```

---

**Last Updated:** 2025-11-15
**Framework:** CRM-JR (Context • Reasons • Mental Models • Judgment • Reversal)
**Integration:** Works with AiYouJR gates, MBA frameworks, Monte Carlo simulations
**Source:** Treadstone/Blackbriar analytical protocols adapted for startup decision-making
