# BOOTSTRAP_GATES - Financial Constraints & Validation Metrics

**Version**: 1.0
**Last Updated**: 2025-11-14
**Purpose**: Define hard financial constraints and success metrics for bootstrap path to profitability

---

## OVERVIEW

Pnkln is bootstrap-funded with strict capital constraints. This document defines the financial gates that govern every spending decision, resource allocation, and strategic commitment.

**Core Principle**: Every dollar spent must have a measurable path to 3× return within the bootstrap timeline.

**Exit Requirement**: Profitable, sustainable business (NOT raising VC, NOT selling at loss)

---

## PRIMARY CONSTRAINTS

### 1. BURN LIMIT

**Total Capital Available**: $60,000 - $65,000

**Current Burn Rate**: [Track Weekly]

- **Target**: ≤$10,000/month average

- **Warning Threshold**: $11,000/month (2 consecutive months triggers review)

- **Kill-Switch**: $12,000/month (2 consecutive months triggers immediate halt)

**Burn Tracking**:

```

Monthly Burn = (Payroll + Infrastructure + Services + Development Costs)
Runway Months = (Remaining Capital) / (Average Monthly Burn)
Decision Point = 6 months runway remaining → activate contingency plan

```

**Reporting**:

- **Weekly**: Burn rate snapshot

- **Monthly**: Burn vs. budget review

- **Quarterly**: Runway projection update

### 2. ROI THRESHOLD

**Minimum Required ROI**: 3× return on invested capital

**Measurement**:

```

ROI = (Revenue Generated - Cost of Investment) / Cost of Investment

Example:
Investment: $10,000 in feature development
Revenue Generated: $40,000 over 12 months
ROI = ($40,000 - $10,000) / $10,000 = 3.0× ✅ PASS

Investment: $10,000 in feature development
Revenue Generated: $25,000 over 12 months
ROI = ($25,000 - $10,000) / $10,000 = 1.5× ❌ FAIL

```

**Timeline**: ROI must be measurable within 6 months

- **Exception**: Core infrastructure investments (1-time, <$5K) may have 12-month window

**Pre-Spend Questions**:

1. What revenue will this generate?

2. When will that revenue be measurable?

3. Is the ROI ≥3× within 6 months?

4. What's the worst-case revenue scenario? (still ≥3×?)

### 3. LTV:CAC RATIO

**Minimum Required Ratio**: 4:1 (Lifetime Value to Customer Acquisition Cost)

**Definitions**:

```

LTV (Lifetime Value) = (Average Monthly Revenue per Customer) × (Average Customer Lifespan in Months)
CAC (Customer Acquisition Cost) = (Total Sales & Marketing Spend) / (Number of Customers Acquired)

LTV:CAC Ratio = LTV / CAC

```

**Target**:

- **Minimum Acceptable**: 4:1

- **Good**: 6:1

- **Excellent**: 8:1+

**Example Calculation**:

```

Customer pays $500/month
Average customer stays 18 months
LTV = $500 × 18 = $9,000

Acquisition cost (sales time + ads + discounts) = $2,000
CAC = $2,000

LTV:CAC = $9,000 / $2,000 = 4.5:1 ✅ PASS (above 4:1 threshold)

```

**Tracking**:

- Calculate for each customer segment (e.g., SMB vs. Enterprise)

- Update monthly as retention data improves

- Flag if ratio drops below 4:1 for any segment

### 4. RUNWAY MANAGEMENT

**Minimum Acceptable Runway**: 6 months

**Triggers**:

- **12 months runway**: Monitor monthly

- **9 months runway**: Review contingencies

- **6 months runway**: Activate contingency plan (revenue acceleration or cost cuts)

- **3 months runway**: Emergency mode (halt all non-essential spend)

**Contingency Plan** (activate at 6 months runway):

1. **Revenue Acceleration**:

   - Aggressive outreach to warm leads

   - Discount offers for prepayment (3-month minimum)

   - Shift to higher-margin services (consulting buffer)


2. **Cost Reduction**:

   - Cut non-essential infrastructure (dev environments, etc.)

   - Defer all feature work except revenue-critical

   - Reduce founder draw to minimum sustainable


3. **Strategic Options**:

   - Seek strategic partnership (revenue share, not equity)

   - Pivot to faster revenue model (services vs. product)

   - Prepare wind-down plan (if revenue acceleration fails)

---

## DECISION GATES

Before approving **any** spending decision, validate against these gates:

### Gate 1: Budget Fit

**Question**: Does this fit within remaining capital budget?

**Check**:

```

Remaining Capital = $60,000 - (Total Spent to Date)
This Decision Cost = $[amount]
Remaining After = Remaining Capital - This Decision Cost

IF Remaining After < (6 months × $10K) THEN FAIL
ELSE IF This Decision Cost > 10% of Remaining Capital THEN ESCALATE
ELSE PASS

```

**Example**:

```

Remaining Capital: $45,000
Decision Cost: $8,000 (Gulfstream ERCOT development)
Remaining After: $45,000 - $8,000 = $37,000

Check: $37,000 ≥ (6 × $10,000) = $60,000? NO, but ≥ $30,000 (3 months)
Status: CONDITIONAL (runway concern, but offset by revenue expectation)

```

### Gate 2: ROI Validation

**Question**: Is ROI ≥3× measurable within 6 months?

**Check**:

```

Expected Revenue = $[amount over 6 months]
Investment Cost = $[amount]
ROI = (Expected Revenue - Investment Cost) / Investment Cost

IF ROI < 3.0× THEN FAIL
ELSE PASS

```

**Example**:

```

Expected Revenue: $50,000 ARR from Gulfstream (first 10 customers × $5K annual)
  → $25,000 in first 6 months (50% recognized)
Investment Cost: $8,000
ROI = ($25,000 - $8,000) / $8,000 = 2.125× ❌ FAIL (below 3×)

REVISION:
Expected Revenue: $60,000 ARR from Gulfstream (12 customers × $5K annual)
  → $30,000 in first 6 months
ROI = ($30,000 - $8,000) / $8,000 = 2.75× ❌ STILL FAIL

REVISION 2:
Expected Revenue: $80,000 ARR from Gulfstream (16 customers × $5K annual)
  → $40,000 in first 6 months
ROI = ($40,000 - $8,000) / $8,000 = 4.0× ✅ PASS

ACTION: Validate 16-customer pipeline before committing spend

```

### Gate 3: LTV:CAC Impact

**Question**: Does this maintain or improve LTV:CAC ≥4:1?

**Check**:

```

IF Decision INCREASES CAC THEN
  New LTV:CAC = (Current LTV) / (Current CAC + CAC Increase)
  IF New LTV:CAC < 4.0 THEN FAIL

IF Decision INCREASES LTV THEN
  New LTV:CAC = (Current LTV + LTV Increase) / (Current CAC)
  [Generally PASS, confirm numbers]

IF Decision NEUTRAL THEN PASS

```

**Example**:

```

Current: LTV = $9,000, CAC = $2,000, Ratio = 4.5:1

Decision: Invest $5K in marketing campaign to acquire 5 customers
CAC Impact: +$1,000 per customer ($5K / 5)
New CAC = $2,000 + $1,000 = $3,000
New LTV:CAC = $9,000 / $3,000 = 3.0:1 ❌ FAIL (below 4:1)

REVISION: Campaign must acquire 8+ customers
CAC Impact: +$625 per customer ($5K / 8)
New CAC = $2,000 + $625 = $2,625
New LTV:CAC = $9,000 / $2,625 = 3.43:1 ❌ STILL FAIL

REVISION 2: Campaign must acquire 10+ customers
CAC Impact: +$500 per customer ($5K / 10)
New CAC = $2,000 + $500 = $2,500
New LTV:CAC = $9,000 / $2,500 = 3.6:1 ❌ BORDERLINE (close to 4:1, but not there)

REVISION 3: Campaign must acquire 12+ customers OR reduce campaign cost to $4K
Option A: 12 customers → CAC = $2,000 + $417 = $2,417 → Ratio = 3.72:1 (still < 4:1)
Option B: $4K campaign, 10 customers → CAC = $2,000 + $400 = $2,400 → Ratio = 3.75:1 (still < 4:1)

FINAL: Target 15 customers or cut campaign to $3K
Option: $3K campaign, 10 customers → CAC = $2,000 + $300 = $2,300 → Ratio = 3.91:1 ≈ 4:1 ✅ CONDITIONAL PASS

```

### Gate 4: Cheaper Alternative?

**Question**: Is there a cheaper way to validate this?

**Check**:

- Can we build an MVP instead of full feature? (Cost: [reduced amount])

- Can we manual-process instead of automate? (Cost: time, not money)

- Can we partner instead of build? (Cost: revenue share vs. upfront)

- Can we defer 90 days and still hit goals? (Cost: $0 now)

**Decision Rule**:

- If cheaper alternative exists AND achieves 80%+ of outcome → CHOOSE CHEAPER

- If no cheaper alternative AND gates 1-3 pass → PROCEED

- If cheaper alternative BUT significantly delays revenue → ESCALATE (trade-off decision)

**Example**:

```

Decision: Build automated ERCOT data ingestion ($8K, 3 weeks)
Alternative: Manual CSV import for first 10 customers ($0 dev cost, 2 hours/week manual labor)

Analysis:

- Manual approach: $0 upfront, ~$500/month opportunity cost (founder time)

- Automated approach: $8K upfront, $0 ongoing

- Breakeven: 16 months of manual work = $8K automated investment

DECISION: Start manual, automate at 20 customers (proven demand)
Savings: $8K deferred, validate market first

```

### Gate 5: Worst-Case Affordable?

**Question**: Can we afford this if revenue assumptions are 50% wrong?

**Check**:

```

Assumed Revenue = $[amount]
Worst-Case Revenue = Assumed Revenue × 0.5
Investment Cost = $[amount]

Worst-Case ROI = (Worst-Case Revenue - Investment Cost) / Investment Cost

IF Worst-Case ROI < 1.5× THEN FAIL (too risky)
ELSE PASS

```

**Example**:

```

Assumed Revenue: $80K ARR from Gulfstream (first 6 months: $40K)
Investment: $8K development
Expected ROI: 4.0×

Worst-Case Revenue: $40K ARR (half of assumption, first 6 months: $20K)
Worst-Case ROI = ($20K - $8K) / $8K = 1.5× ✅ PASS (breakeven acceptable in worst case)

If Investment were $15K:
Worst-Case ROI = ($20K - $15K) / $15K = 0.33× ❌ FAIL (loss in worst case, too risky)

```

---

## GATE DECISION MATRIX

| Gate | Pass | Conditional | Fail |
|------|------|-------------|------|
| **Budget Fit** | Remaining ≥ 6mo runway | Remaining ≥ 3mo runway + revenue plan | Remaining < 3mo runway |
| **ROI Validation** | ROI ≥ 3× within 6mo | ROI ≥ 2× within 6mo + path to 3× | ROI < 2× |
| **LTV:CAC Impact** | Ratio ≥ 4:1 maintained | Ratio ≥ 3.5:1, plan to restore 4:1 | Ratio < 3.5:1 |
| **Cheaper Alternative** | No cheaper option | Cheaper exists, strategic reason to pay more | Cheaper exists, no justification |
| **Worst-Case Affordable** | ROI ≥ 1.5× in worst case | ROI ≥ 1.0× (breakeven) in worst case | ROI < 1.0× in worst case |

**Decision Rules**:

- **All PASS** → APPROVE

- **Any FAIL** → REJECT or REVISE

- **Mix of PASS + CONDITIONAL** → APPROVE WITH CONDITIONS (document conditions clearly)

---

## SPENDING CATEGORIES

### Category 1: Revenue-Critical (Highest Priority)

**Definition**: Directly enables revenue generation or customer retention

**Examples**:

- Customer-requested features blocking sales

- Infrastructure scaling to support paid customers

- Support/success resources to prevent churn

**Approval Threshold**: Must pass Gates 1, 2, 5 (can flex on Gate 3-4 if critical)

### Category 2: Revenue-Enabling (High Priority)

**Definition**: Indirectly supports revenue through efficiency, quality, or market positioning

**Examples**:

- Sales/marketing tools that reduce CAC

- Performance optimizations that improve conversion

- Quality improvements that increase LTV (retention)

**Approval Threshold**: Must pass all 5 gates

### Category 3: Technical Debt (Medium Priority)

**Definition**: Reduces ongoing costs or future risks, no direct revenue impact

**Examples**:

- Refactoring to improve maintainability

- Upgrading dependencies for security

- Improving test coverage

**Approval Threshold**: Must pass Gates 1, 4, 5 + demonstrate cost savings > investment within 12 months

### Category 4: Innovation/Exploration (Low Priority)

**Definition**: Validates new opportunities, experiments, learning

**Examples**:

- Proof-of-concept for new market

- Prototype for new feature category

- Research spikes

**Approval Threshold**: Micro-budget only (<$500), defer until post-revenue unless strategic

### Category 5: Discretionary (Deferred)

**Definition**: "Nice to have" improvements, team morale, branding

**Examples**:

- Office upgrades, team events, swag

- Non-essential tooling, conveniences

- Branding, design polish beyond MVP

**Approval Threshold**: Defer until profitable (exception: critical recruiting/retention)

---

## REAL-WORLD EXAMPLES

### Example 1: APPROVE (Gulfstream ERCOT Integration)

```

DECISION: Build Gulfstream ERCOT Integration
CATEGORY: Revenue-Critical (Category 1)

GATE ASSESSMENT:
[Gate 1: Budget Fit]

- Remaining Capital: $45,000

- Decision Cost: $8,000

- Remaining After: $37,000

- Runway Check: $37K ÷ $10K/mo = 3.7 months (below 6, but revenue offsets)

- STATUS: CONDITIONAL (revenue plan required)

[Gate 2: ROI Validation]

- Expected Revenue: $80K ARR (16 customers × $5K), $40K in 6 months

- Investment: $8,000

- ROI: ($40K - $8K) / $8K = 4.0×

- STATUS: PASS

[Gate 3: LTV:CAC Impact]

- Current: LTV $9K, CAC $2K, Ratio 4.5:1

- Impact: Neutral (product improvement, CAC unchanged)

- STATUS: PASS

[Gate 4: Cheaper Alternative]

- Alternative: Manual CSV import ($0 dev, $500/month labor)

- Analysis: Manual viable for first 10, but blocks scale to 16+

- Decision: Critical for revenue target, automation needed

- STATUS: PASS (strategic justification)

[Gate 5: Worst-Case Affordable]

- Worst-Case Revenue: $40K ARR (8 customers), $20K in 6 months

- Worst-Case ROI: ($20K - $8K) / $8K = 1.5×

- STATUS: PASS (breakeven in worst case)

OVERALL: APPROVE WITH CONDITIONS
CONDITIONS:

1. Validate 16-customer pipeline before committing spend

2. Scope to 3-week timeline (kill-switch if exceeds)

3. Monthly revenue tracking, reassess at 3 months

```

### Example 2: REJECT (Rewrite Backend in Rust)

```

DECISION: Rewrite Backend in Rust
CATEGORY: Technical Debt (Category 3, but claimed as Category 2)

GATE ASSESSMENT:
[Gate 1: Budget Fit]

- Remaining Capital: $45,000

- Decision Cost: $30,000 (6 months opportunity cost)

- Remaining After: $15,000

- Runway Check: $15K ÷ $10K/mo = 1.5 months

- STATUS: FAIL (violates 6-month runway requirement)

[Gate 2: ROI Validation]

- Expected Revenue: $0 (no direct revenue impact)

- Investment: $30,000

- ROI: ($0 - $30K) / $30K = -100%

- STATUS: FAIL (no revenue justification)

[Gate 3: LTV:CAC Impact]

- Impact: Neutral (no customer-facing change)

- STATUS: PASS (not relevant, but not harmful)

[Gate 4: Cheaper Alternative]

- Alternative: Optimize existing Python codebase ($5K, 2 weeks)

- Analysis: Can achieve p99≤90ms target with optimization, no rewrite needed

- STATUS: FAIL (much cheaper alternative exists)

[Gate 5: Worst-Case Affordable]

- Worst-Case Revenue: $0

- Worst-Case ROI: -100%

- STATUS: FAIL (loss in all scenarios)

OVERALL: REJECT
RATIONALE:

- Violates multiple hard gates (Budget, ROI, Alternative)

- No revenue justification

- Cheaper optimization path available

- High opportunity cost (delays Gulfstream by 6 months)

ALTERNATIVE: Approve $5K optimization effort, target p99≤90ms in 2 weeks

```

### Example 3: DEFER (Multi-Region Deployment)

```

DECISION: Implement Multi-Region Deployment
CATEGORY: Technical Debt / Revenue-Enabling (unclear)

GATE ASSESSMENT:
[Gate 1: Budget Fit]

- Remaining Capital: $45,000

- Decision Cost: $15,000

- Remaining After: $30,000

- Runway Check: $30K ÷ $10K/mo = 3 months

- STATUS: CONDITIONAL (tight, but possible)

[Gate 2: ROI Validation]

- Expected Revenue: $0 in 6 months (no current global demand)

- Potential Future Revenue: Unknown

- ROI: Cannot measure within 6 months

- STATUS: FAIL (no measurable ROI timeline)

[Gate 3: LTV:CAC Impact]

- Impact: Neutral

- STATUS: PASS

[Gate 4: Cheaper Alternative]

- Alternative: Defer until global customer appears, spike at that time

- Cost: $0 now, $15K when needed

- STATUS: FAIL (much cheaper to defer)

[Gate 5: Worst-Case Affordable]

- Worst-Case Revenue: $0

- Worst-Case ROI: -100%

- STATUS: FAIL

OVERALL: DEFER
RATIONALE:

- No current customer need (all customers US-based)

- ROI not measurable (speculative future benefit)

- Cheaper to wait and build when needed

- Capital better spent on revenue features (Gulfstream)

DEFERRAL CRITERIA: Revisit when:

1. First non-US customer appears, OR

2. 50 total customers reached (scale justification), OR

3. Uptime drops below 99.5% (reliability justification)

```

---

## MONITORING & REPORTING

### Weekly Burn Report (Every Monday)

```

WEEK ENDING: [Date]
====================

BURN THIS WEEK: $[amount]
BURN THIS MONTH (MTD): $[amount]
MONTHLY RUN RATE: $[projected monthly burn]

BUDGET STATUS:

- Target Monthly Burn: $10,000

- Actual Run Rate: $[amount]

- Variance: [over/under budget]

- STATUS: [GREEN: <$10K | YELLOW: $10-11K | RED: >$11K]

RUNWAY:

- Remaining Capital: $[amount]

- Months Remaining: [amount] months

- STATUS: [GREEN: >9mo | YELLOW: 6-9mo | RED: <6mo]

ACTIONS REQUIRED:

- [If YELLOW or RED, list specific actions]

```

### Monthly ROI Review (First of Month)

```

MONTH: [Month Year]
====================

INVESTMENTS THIS MONTH:

- [Investment 1]: $[amount] → Expected ROI: [X×] by [date]

- [Investment 2]: $[amount] → Expected ROI: [X×] by [date]

MATURING INVESTMENTS (6 months ago):

- [Investment]: $[amount] → Actual Revenue: $[amount] → Actual ROI: [X×]

- STATUS: [MET/MISSED] target

LTV:CAC TRACKING:

- Current LTV: $[amount]

- Current CAC: $[amount]

- Ratio: [X:1]

- STATUS: [GREEN: ≥4:1 | YELLOW: 3.5-4:1 | RED: <3.5:1]

GATE COMPLIANCE:

- Gate 1 (Budget): [PASS/CONDITIONAL/FAIL]

- Gate 2 (ROI): [X] investments on track, [Y] at risk

- Gate 3 (LTV:CAC): [PASS/CONDITIONAL/FAIL]

- Gate 5 (Worst-Case): [All investments survivable: YES/NO]

```

### Quarterly Strategic Review

```

QUARTER: [Q# Year]
====================

CAPITAL DEPLOYED: $[amount this quarter]
REVENUE GENERATED: $[amount this quarter]
BLENDED ROI: [X×]

TOP INVESTMENTS:

1. [Investment]: $[cost] → $[revenue] → [ROI×]

2. [Investment]: $[cost] → $[revenue] → [ROI×]

3. [Investment]: $[cost] → $[revenue] → [ROI×]

MISSED BETS:

1. [Investment]: $[cost] → $[revenue] → [ROI×] (Target was [X×])

   - Lesson: [What we learned]

STRATEGIC ADJUSTMENTS:

- [Any changes to gates, thresholds, priorities based on learnings]

NEXT QUARTER BUDGET:

- Projected Burn: $[amount]

- Projected Revenue: $[amount]

- Net Cash Flow: [positive/negative $amount]

- Runway End of Quarter: [X] months

```

---

## CONTINGENCY PLAN ACTIVATION

### Trigger: Runway Drops to 6 Months

**PHASE 1: ASSESSMENT (Week 1)**

1. Confirm runway calculation (burn rate × months)

2. Identify all committed spend (cannot cancel)

3. Identify all discretionary spend (can cut immediately)

4. Project revenue next 90 days (conservative estimate)

**PHASE 2: REVENUE ACCELERATION (Weeks 2-4)**

1. Outreach to all warm leads (target: 50 contacts)

2. Offer prepayment discounts (10% off for 3-month prepay)

3. Upsell existing customers (new features, higher tiers)

4. Explore consulting/services buffer (trade time for cash)

5. TARGET: $20K revenue in 30 days

**PHASE 3: COST REDUCTION (Weeks 5-8)**

1. Cut all Category 4-5 spend (Innovation, Discretionary)

2. Defer all Category 3 spend (Technical Debt)

3. Review Category 2 spend (Revenue-Enabling), cut 50%

4. Reduce infrastructure to essentials (dev → production only)

5. Founder draw to minimum sustainable (~$3K/month)

6. TARGET: Reduce burn to $6K/month

**PHASE 4: DECISION POINT (Week 12)**

- **IF** revenue acceleration successful ($20K+ in 90 days) → CONTINUE, monitor monthly

- **IF** cost reduction extended runway to 12+ months → CONTINUE, resume measured growth

- **IF** runway still <6 months AND revenue <$10K/month → ACTIVATE PHASE 5

**PHASE 5: STRATEGIC OPTIONS (Week 13+)**

1. **Option A: Pivot** to faster revenue model (SaaS → Services, Product → Consulting)

2. **Option B: Partner** with strategic player (revenue share, channel partnership)

3. **Option C: Wind Down** gracefully (fulfill customer obligations, return remaining capital)

---

## MAINTENANCE

**Update Schedule**:

- **Monthly**: Burn targets, LTV:CAC calculations

- **Quarterly**: ROI thresholds (if market data changes)

- **Ad-hoc**: Gate criteria (if strategic priorities shift)

**Change Log**:

- Track all changes to gates, thresholds, formulas

- Document rationale for changes

- Version control in Cor_vX.md

---

## INTEGRATION WITH OTHER FRAMEWORKS

**BOOTSTRAP_GATES** provides BRAKES for **JR_ENGINE**.
**TECHNICAL_SLA** provides performance constraints that may have cost implications.
**RISK_FRAMEWORK** identifies risks that may require budget reserves.

**Workflow**:

1. Decision proposed

2. Run JR_ENGINE (PURPOSE → REASONS → BRAKES)

3. BRAKES check includes BOOTSTRAP_GATES (this document)

4. All 5 gates must PASS or CONDITIONAL (document conditions)

5. Approved decisions tracked in monthly ROI review

---

**END BOOTSTRAP_GATES.md**
