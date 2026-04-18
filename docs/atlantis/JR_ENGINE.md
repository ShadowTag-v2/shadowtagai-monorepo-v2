# JR_ENGINE - Justification-Reasoning Engine

**Version**: 1.0
**Last Updated**: 2025-11-14
**Purpose**: Systematic decision validation framework for strategic, technical, and operational choices

---

## OVERVIEW

The JR_ENGINE is Pnkln's core decision-making framework. It ensures every significant choice is grounded in clear purpose, supported by evidence, and constrained by predefined limits.

**Three-Stage Validation**: PURPOSE → REASONS → BRAKES

**When to Use JR_ENGINE**:

- Feature prioritization (what to build next)

- Technical architecture decisions (how to build it)

- Resource allocation (spending time or money)

- Partnership/vendor selection (who to work with)

- Strategic pivots (major direction changes)

**When NOT to Use** (overkill for):

- Minor bug fixes

- Standard operational tasks

- Previously validated patterns

- Emergency responses (triage first, validate later)

---

## STAGE 1: PURPOSE

**Question**: What strategic outcome does this serve?

### Validation Criteria

Every decision must map to **at least one** of these strategic outcomes:

#### 1. Revenue Generation


- Directly increases ARR (Annual Recurring Revenue)

- Reduces customer acquisition cost (CAC)

- Increases customer lifetime value (LTV)

- Enables new revenue stream

**Examples**:

- ✅ "Build Gulfstream ERCOT integration" → New revenue stream, target $50K ARR

- ❌ "Rewrite admin dashboard in new framework" → No direct revenue impact

#### 2. Bootstrap Viability


- Reduces burn rate

- Extends runway

- Improves capital efficiency

- De-risks path to profitability

**Examples**:

- ✅ "Migrate to cheaper cloud provider" → Reduces burn $500/month

- ❌ "Hire full-time designer" → Increases burn, deferred until revenue

#### 3. Technical Foundation


- Enables future revenue opportunities

- Improves system reliability/performance

- Reduces technical debt blocking progress

- Achieves critical SLA targets

**Examples**:

- ✅ "Optimize Judge #6 to p99≤90ms" → Enables enterprise sales, SLA requirement

- ❌ "Migrate to microservices" → Premature complexity, no blocked opportunities

#### 4. Learning/Validation


- Tests core business assumption

- Validates customer willingness to pay

- Proves technical feasibility

- Reduces strategic uncertainty

**Examples**:

- ✅ "Ship MVP to 10 beta customers" → Validates product-market fit

- ❌ "Build perfect onboarding flow" → Optimizing before validation

### Purpose Template

```

PURPOSE: [Strategic outcome category]
IMPACT: [Quantified expected result]
TIMELINE: [When impact measurable]
ALIGNMENT: [How this serves bootstrap mission]

```

**Example**:

```

PURPOSE: Revenue Generation
IMPACT: $50K ARR from first 10 ERCOT customers
TIMELINE: 90 days post-launch
ALIGNMENT: Proves market fit, validates pricing, funds next phase

```

---

## STAGE 2: REASONS

**Question**: What evidence supports this decision?

### Evidence Hierarchy (Tier 1-4)

#### Tier 1: Direct Evidence (Strongest)


- **User feedback**: Direct quotes, interviews, observed behavior

- **Production metrics**: Real system performance data

- **Financial data**: Actual revenue, costs, conversion rates

- **Market data**: Signed contracts, committed customers

**Quality Markers**:

- First-hand observation

- Quantified and specific

- Recent (within 90 days preferred)

- Representative sample size

**Examples**:

- "3 of 5 beta users requested ERCOT integration in exit interviews"

- "p99 latency currently 150ms, measured over 10K production requests"

- "Customer churn rate 15% monthly, exit surveys cite 'slow performance'"

#### Tier 2: Secondary Evidence (Strong)


- **Industry benchmarks**: Published studies, analyst reports

- **Competitive analysis**: Direct competitor feature/pricing comparison

- **Advisor input**: Domain expert recommendations

- **Vendor data**: Published specifications, case studies

**Quality Markers**:

- Credible source (named, verifiable)

- Relevant to your market/context

- Recent (within 12 months)

- Comparable scale/stage

**Examples**:

- "Gartner reports 68% of energy traders prioritize real-time pricing APIs"

- "Primary competitor charges $500/month, our pricing $300/month undercuts"

- "Energy sector advisor recommends ERCOT before MISO expansion"

#### Tier 3: Reasoned Inference (Moderate)


- **First principles reasoning**: Logical deduction from known facts

- **Analogies**: Similar situations in adjacent markets

- **Best practices**: Established patterns from credible sources

- **Expert intuition**: Based on relevant experience

**Quality Markers**:

- Logic chain is explicit and testable

- Assumptions clearly stated

- Analogies are truly comparable

- Expert has relevant domain experience

**Examples**:

- "If latency >100ms, likely violates enterprise SLA standards (industry norm)"

- "SaaS pricing models work in adjacent FinTech, likely transferable to energy"

- "AWS best practices recommend caching for <100ms API response"

#### Tier 4: Speculation (Weak - Flag Explicitly)


- **Assumptions**: Unvalidated beliefs about market/users

- **Intuition**: Gut feeling without evidence

- **Trends**: Extrapolation without supporting data

- **Hopes**: Desired outcomes without pathway

**Quality Markers**:

- **MUST be flagged** as Tier 4 / speculation

- Articulate what would validate/invalidate

- Use sparingly, never as sole justification

- State confidence level (e.g., "30% confident")

**Examples**:

- "Assume enterprise customers will pay 10× SMB pricing (UNVALIDATED)"

- "Intuit users prefer dark mode (no data, speculative)"

- "Energy market growing 20% annually (trend, unverified in our segment)"

### Evidence Template

```

REASONS:
[Tier 1 - Direct Evidence]

- [Statement] (Source: [specific], Date: [YYYY-MM-DD])

[Tier 2 - Secondary Evidence]

- [Statement] (Source: [specific], Date: [YYYY-MM-DD])

[Tier 3 - Reasoned Inference]

- [Statement] (Logic: [explicit reasoning])

[Tier 4 - Speculation] **FLAG**

- [Statement] (Assumption, confidence: [X%], validate by: [method])

CONFIDENCE: [High/Medium/Low based on evidence mix]

```

**Example**:

```

REASONS:
[Tier 1]

- 3/5 beta users explicitly requested real-time ERCOT pricing (Source: User interviews, 2025-11-01 to 2025-11-10)

- Current p99 latency 150ms measured across 10,000 production requests (Source: Datadog, 2025-11-07)

[Tier 2]

- Gartner: 68% of energy traders prioritize real-time APIs (Source: Gartner Energy Tech Report 2025, published 2025-09-15)

- Competitor "GridPulse" charges $500/month for similar ERCOT integration (Source: Public pricing page, verified 2025-11-12)

[Tier 3]

- Enterprise SLAs typically require p99<100ms for API dependencies (Logic: Review of 10 public SaaS SLAs in FinTech/Energy showed 9/10 had <100ms requirements)

[Tier 4] **FLAG**

- Assume 20% of ERCOT participants will adopt in first year (Speculation, confidence: 40%, validate by: Outreach to 50 prospects in 30 days)

CONFIDENCE: High (strong Tier 1 + Tier 2 evidence, minimal reliance on speculation)

```

---

## STAGE 3: BRAKES

**Question**: What constraints and kill-switch criteria apply?

### Constraint Categories

#### 1. Bootstrap Financial Gates

**From**: BOOTSTRAP_GATES.md

**Pre-Decision Questions**:

- Does this fit within $60-65K total burn?

- Is ROI ≥3× measurable within 6 months?

- Does LTV:CAC ratio stay ≥4:1?

- Can we afford this in worst-case revenue scenario?

- Is there a cheaper validation path?

**Kill-Switch**:

- If monthly burn trends >$12K for 2 consecutive months → HALT

- If spend has no measurable ROI within 6 months → CANCEL

#### 2. Technical SLA Requirements

**From**: TECHNICAL_SLA.md

**Pre-Decision Questions**:

- Does this help achieve p99≤90ms for Judge #6?

- Does this maintain 99.9% uptime requirement?

- Is this compatible with core stack (Python 3.11+, FastAPI, PostgreSQL)?

- Does this add complexity that degrades performance?

- Is this testable in isolation (modularity principle)?

**Kill-Switch**:

- If change causes p99 latency >200ms for 7 days → ROLLBACK

- If availability drops below 99.5% for 30 days → REVERT

#### 3. Risk Framework Triggers

**From**: RISK_FRAMEWORK.md (ATP 5-19)

**Pre-Decision Questions**:

- What's the worst-case failure scenario?

- Probability × Severity = Risk Level?

- Is risk level acceptable (Low/Moderate vs. High/Extreme)?

- What mitigation controls exist?

- Is this reversible if assumptions prove wrong?

**Kill-Switch**:

- **Extreme risk** identified → STOP immediately, escalate

- **High risk** without adequate mitigation → DEFER until controls in place

- **Legal/compliance** risk flagged → HALT, consult advisor

#### 4. Strategic Alignment

**From**: Cor_vX.md STRATEGIC_LOAD

**Pre-Decision Questions**:

- Does this align with current priorities (Gulfstream, Judge #6)?

- Is this "nice to have" vs. "must have" for next milestone?

- Does this create dependency/lock-in we want to avoid?

- Is timing right, or should we defer 90 days?

- Does this distract from revenue validation?

**Kill-Switch**:

- If core assumption invalidated (e.g., ERCOT market access blocked) → PIVOT

- If key person departure creates execution risk → PAUSE

- If competitive landscape shifts dramatically → REASSESS

### Brakes Template

```

BRAKES:
[Bootstrap Gates]

- Burn impact: $[amount] ([one-time/monthly])

- ROI timeline: [X months to measurable return]

- LTV:CAC impact: [increase/decrease/neutral]

- Worst-case affordable: [yes/no]

- Cheaper alternative: [none identified / [alternative]]

[Technical SLA]

- Judge #6 latency impact: [improves/degrades/neutral by Xms]

- Uptime risk: [low/medium/high]

- Stack compatibility: [yes/no, notes]

- Complexity added: [low/medium/high]

- Testability: [isolated/integration required]

[Risk Framework]

- Worst-case scenario: [description]

- Probability: [low/medium/high]

- Severity: [low/medium/high/extreme]

- Risk level: [low/moderate/high/extreme]

- Mitigation: [controls in place]

[Strategic Alignment]

- Priority alignment: [Gulfstream/Judge #6/backlog]

- Urgency: [must-have/nice-to-have]

- Dependencies created: [none/[list]]

- Deferral option: [can defer [X] days/must do now]

- Distraction risk: [low/medium/high]

KILL-SWITCH CRITERIA:

- [Specific metric] exceeds [threshold] → [action]

- [Event occurs] → [action]

```

**Example**:

```

BRAKES:
[Bootstrap Gates]

- Burn impact: $8,000 (one-time development cost)

- ROI timeline: 4 months to first revenue

- LTV:CAC impact: Neutral (enables revenue, doesn't reduce CAC)

- Worst-case affordable: Yes ($8K within $60-65K envelope)

- Cheaper alternative: None identified (MVP already scoped minimally)

[Technical SLA]

- Judge #6 latency impact: Improves by ~30ms (database optimization)

- Uptime risk: Low (caching layer is additive, not replacement)

- Stack compatibility: Yes (Redis standard in Python ecosystem)

- Complexity added: Low (well-understood pattern)

- Testability: Isolated (can test cache layer independently)

[Risk Framework]

- Worst-case scenario: Integration fails, lose 2 weeks + $8K

- Probability: Low (well-trodden technical path)

- Severity: Medium (burn impact acceptable, time delay manageable)

- Risk level: Low-Moderate

- Mitigation: Spike/POC first (2 days, $500), then commit

[Strategic Alignment]

- Priority alignment: Gulfstream (enables launch)

- Urgency: Must-have (blocking beta customer deployment)

- Dependencies created: None (ERCOT API consumption only)

- Deferral option: Cannot defer (customer commitment)

- Distraction risk: Low (focused execution, clear scope)

KILL-SWITCH CRITERIA:

- If development exceeds 3 weeks → STOP, reassess scope

- If first 10 customers don't convert → CANCEL expansion

- If ERCOT API reliability <99% → PAUSE, escalate to vendor

```

---

## FULL JR_ENGINE WORKFLOW

### Step-by-Step Process


1. **Trigger**: Major decision point identified

   - Feature request from customer

   - Technical architecture choice

   - Budget allocation decision

   - Strategic pivot consideration


2. **PURPOSE Validation** (5-10 minutes)

   - Map to strategic outcome (Revenue/Bootstrap/Technical/Learning)

   - Quantify expected impact

   - Set timeline for measurement

   - Confirm alignment with bootstrap mission

   - **PASS**: Proceed to REASONS | **FAIL**: Reject or refine


3. **REASONS Assessment** (15-30 minutes)

   - Gather evidence across Tier 1-4

   - Classify each piece of evidence

   - Flag Tier 4 speculation explicitly

   - Assess overall confidence

   - Identify gaps (what additional evidence would help?)

   - **PASS**: Strong evidence (mostly Tier 1-2) | **CONDITIONAL**: Moderate (mix of Tier 2-3) | **FAIL**: Weak (mostly Tier 3-4)


4. **BRAKES Check** (10-20 minutes)

   - Run through all constraint categories

   - Identify kill-switch criteria

   - Assess risk level and mitigation

   - Check strategic alignment and timing

   - **PASS**: All gates satisfied | **CONDITIONAL**: Mitigatable concerns | **FAIL**: Hard constraints violated


5. **Decision Output**

   - **RECOMMEND**: PURPOSE clear + REASONS strong + BRAKES pass

   - **CONDITIONAL**: PURPOSE clear + REASONS moderate + BRAKES conditional (specify conditions)

   - **DEFER**: PURPOSE clear + REASONS weak → gather more evidence

   - **REJECT**: PURPOSE unclear OR BRAKES fail OR REASONS insufficient

### Decision Output Template

```

JR_ENGINE DECISION: [Feature/Decision Name]
=========================================

PURPOSE: [Strategic outcome]
IMPACT: [Quantified result]
TIMELINE: [Measurement window]

REASONS:
[Tier 1] - [Key evidence]
[Tier 2] - [Supporting evidence]
[Tier 3] - [Inference]
[Tier 4] **FLAG** - [Speculation, if any]
CONFIDENCE: [High/Medium/Low]

BRAKES:
Bootstrap: [Pass/Conditional/Fail] - [Key constraint]
Technical: [Pass/Conditional/Fail] - [Key constraint]
Risk: [Level] - [Mitigation]
Strategic: [Aligned/Misaligned] - [Note]

KILL-SWITCH:

- [Criterion 1] → [Action]

- [Criterion 2] → [Action]

DECISION: [RECOMMEND / CONDITIONAL / DEFER / REJECT]
RATIONALE: [1-2 sentence summary]
NEXT STEPS: [If recommend/conditional, what's next?]

```

---

## EXAMPLES

### Example 1: RECOMMEND Decision

```

JR_ENGINE DECISION: Build Gulfstream ERCOT Integration
======================================================

PURPOSE: Revenue Generation
IMPACT: $50K ARR from first 10 ERCOT customers
TIMELINE: 90 days post-launch

REASONS:
[Tier 1]

- 3/5 beta users explicitly requested ERCOT integration (User interviews, 2025-11-01 to 2025-11-10)

- 2 prospects signed LOI contingent on ERCOT support (Signed letters, 2025-11-08)

[Tier 2]

- Competitor GridPulse charges $500/month for similar integration (Public pricing, verified 2025-11-12)

- Industry advisor recommends ERCOT before MISO expansion (Advisor meeting, 2025-11-05)

[Tier 3]

- Energy market SaaS typically see 15-20% conversion from beta to paid (Inference from 5 comparable SaaS products)

CONFIDENCE: High (strong Tier 1 evidence, customer pull)

BRAKES:
Bootstrap: PASS - $8K one-time cost within budget, 4-month ROI timeline acceptable
Technical: PASS - Standard API integration, proven pattern, low complexity
Risk: LOW-MODERATE - Well-understood technical path, market validated by competitors
Strategic: ALIGNED - Top priority, directly enables revenue validation

KILL-SWITCH:

- If development exceeds 3 weeks → STOP, reassess scope

- If first 10 customers <20% conversion → CANCEL expansion plans

- If ERCOT API reliability <99% → PAUSE, escalate to vendor

DECISION: RECOMMEND
RATIONALE: Strong customer pull, clear revenue path, acceptable cost/risk, strategic priority.
NEXT STEPS:

1. Scope MVP to 3-week timeline

2. Spike ERCOT API integration (2 days, $500)

3. If spike successful, commit to full build

```

### Example 2: DEFER Decision

```

JR_ENGINE DECISION: Implement Multi-Region Deployment
=====================================================

PURPOSE: Technical Foundation
IMPACT: 99.99% uptime via redundancy, enable global customers
TIMELINE: Benefits realized over 12 months

REASONS:
[Tier 3]

- Industry best practice for SaaS at scale (General pattern, not specific to our market)

- Competitors likely have multi-region (Assumption, not verified)

[Tier 4] **FLAG**

- Assume global customers will emerge (No evidence yet, confidence: 30%)

- Speculate uptime issues will arise (No current uptime problems, <0.1% error rate)

CONFIDENCE: Low (mostly Tier 3-4, no direct evidence of need)

BRAKES:
Bootstrap: FAIL - $15K setup cost, no measurable ROI within 6 months
Technical: CONDITIONAL - Adds complexity, no current uptime issues (99.95% actual vs. 99.9% target)
Risk: LOW - Well-understood technical pattern, but unnecessary at current scale
Strategic: MISALIGNED - Backlog item, deferred until 50 customers

KILL-SWITCH:

- N/A (not proceeding)

DECISION: DEFER
RATIONALE: No evidence of current need, violates bootstrap constraints, not strategic priority. Revisit at 50 customers or if uptime drops below 99.5%.
NEXT STEPS:

1. Monitor uptime monthly

2. Reassess at 50 customer milestone

3. If global customer appears, spike cost/effort at that time

```

### Example 3: REJECT Decision

```

JR_ENGINE DECISION: Rewrite Backend in Rust
===========================================

PURPOSE: Technical Foundation (claimed)
IMPACT: Improved performance (unquantified)
TIMELINE: 6 months development time

REASONS:
[Tier 3]

- Rust is faster than Python (General truth, but context matters)

- Industry trend toward Rust (Observation, not applicable to our situation)

[Tier 4] **FLAG**

- Assume performance issues will emerge (No current performance issues, speculative)

- Believe team will learn Rust quickly (Team has no Rust experience, confidence: 20%)

CONFIDENCE: Very Low (no direct evidence, speculative)

BRAKES:
Bootstrap: FAIL - $30K+ opportunity cost, no revenue impact, violates capital efficiency
Technical: FAIL - Current p99=150ms (target 90ms achievable with optimization, not rewrite)
Risk: HIGH - Team inexperience, 6-month delay to revenue features, no fallback
Strategic: MISALIGNED - No customer demand, distracts from Gulfstream priority

KILL-SWITCH:

- N/A (not proceeding)

DECISION: REJECT
RATIONALE: No evidence of need, massive opportunity cost, high risk, strategic misalignment. Solve performance with optimization (caching, queries) not rewrite.
NEXT STEPS:

1. Focus on Judge #6 optimization to p99≤90ms (current plan)

2. If performance targets still missed after optimization, revisit

3. Never rewrite without customer/revenue driver

```

---

## ANTI-PATTERNS (Common Mistakes)

### 1. Skipping PURPOSE

**Mistake**: "This is a good idea, let's build it."
**Fix**: Force articulation of strategic outcome. "Good idea" is not a purpose.

### 2. Tier 4 Disguised as Tier 1

**Mistake**: "Users want this" (based on 1 anecdotal comment)
**Fix**: Classify evidence honestly. 1 comment = weak Tier 1 or strong Tier 4, not gospel.

### 3. Ignoring BRAKES

**Mistake**: "Great idea, but we're out of money... oops."
**Fix**: Check constraints BEFORE falling in love with the idea.

### 4. Analysis Paralysis

**Mistake**: "We need more evidence before we can decide anything."
**Fix**: JR_ENGINE is decision support, not decision avoidance. Set evidence threshold, decide.

### 5. Retrofitting Justification

**Mistake**: "I already decided, now let me fill out JR_ENGINE to justify it."
**Fix**: Run JR_ENGINE BEFORE committing. Be willing to change your mind.

---

## INTEGRATION WITH OTHER FRAMEWORKS

**JR_ENGINE** is the decision validation engine.
**BOOTSTRAP_GATES** provides financial constraints for BRAKES.
**TECHNICAL_SLA** provides performance constraints for BRAKES.
**RISK_FRAMEWORK** provides risk assessment methodology for BRAKES.
**Cor_vX.md** provides strategic context for PURPOSE alignment.

**Workflow**:

1. Decision arises → Run JR_ENGINE

2. PURPOSE maps to Cor_vX.md strategic priorities

3. BRAKES check against BOOTSTRAP_GATES, TECHNICAL_SLA, RISK_FRAMEWORK

4. Output decision with full validation trail

---

## MAINTENANCE

**Update Triggers**:

- Strategic priorities change (update PURPOSE categories)

- Bootstrap constraints change (update BRAKES)

- New evidence hierarchy needed (extend Tier structure)

- Kill-switch criteria evolve (update BRAKES template)

**Version Control**:

- Track changes in Cor_vX.md version history

- Document rationale for framework changes

- Ensure all team members use same JR_ENGINE version

---

**END JR_ENGINE.md**
