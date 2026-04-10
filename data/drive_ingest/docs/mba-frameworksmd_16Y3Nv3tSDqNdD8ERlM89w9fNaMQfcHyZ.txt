# MBA Strategic Frameworks for AiYouJR

**Purpose:** Apply proven MBA frameworks to validate strategic decisions
**Integration:** Used in AiYouJR Reasons Gate + CRM-JR analysis
**Source:** Harvard Business School, McKinsey, BCG, Blue Ocean Strategy

---

## Framework Index

1. **VRIO** (Resource-Based View) - Sustainable competitive advantage
2. **Value Stick** (Pricing Power) - Capture vs. create value
3. **Blue Ocean Strategy** (Uncontested Markets) - Create new demand
4. **McKinsey Three Horizons** (Growth Portfolio) - Balance short/mid/long-term
5. **Strategy Diamond** (Hambrick & Fredrickson) - Integrated strategy check
6. **Porter's 5 Forces** (Competitive Forces) - Industry attractiveness
7. **BCG Growth-Share Matrix** (Portfolio Management) - Resource allocation

---

## 1. VRIO Framework

**Purpose:** Determine if a resource/capability creates sustainable competitive advantage

### Four Tests

```
Resource → [V] → [R] → [I] → [O] → Outcome
```

**V - Valuable:** Does it exploit opportunities or neutralize threats?
**R - Rare:** Do few competitors possess it?
**I - Inimitable:** Is it costly/difficult to copy?
**O - Organized:** Is the firm organized to capture value?

### Decision Matrix

| V | R | I | O | Competitive Implication | Economic Performance |
|---|---|---|---|-------------------------|----------------------|
| No | - | - | No | Competitive Disadvantage | Below Normal |
| Yes | No | - | | Competitive Parity | Normal |
| Yes | Yes | No | | Temporary Advantage | Above Normal (short-term) |
| Yes | Yes | Yes | No | Unused Advantage | Normal |
| Yes | Yes | Yes | Yes | **Sustained Advantage** | **Above Normal (long-term)** |

### Example: ActiveShield's Cryptographic Signing (ShadowTag)

**V - Valuable?** ✅ YES
- Exploits opportunity: Enterprise security compliance requirements
- Neutralizes threat: Document tampering, fraud

**R - Rare?** ✅ YES
- Competitors (DocuSign, Adobe Sign) use standard PKI
- ShadowTag's cryptographic approach is proprietary
- <5 competitors globally with similar tech

**I - Inimitable?** ✅ YES
- **Path Dependency:** 3 years R&D, multiple patents filed
- **Causal Ambiguity:** Complex interplay of algorithms (not easily reverse-engineered)
- **Social Complexity:** Team expertise (cryptography + compliance)
- **Cost:** $500k+ investment to replicate

**O - Organized?** ✅ YES
- Go-to-market: Sales team trained on technical differentiation
- Operations: Support team equipped for enterprise deployments
- Culture: Security-first mindset embedded in engineering

**VRIO Outcome:** ✅ **SUSTAINED COMPETITIVE ADVANTAGE**
**Strategic Implication:** Invest aggressively, build moat, premium pricing justified

### VRIO Analysis Template

```markdown
# VRIO Analysis: [Feature/Resource Name]

## V - Valuable
**Question:** Does this exploit an opportunity or neutralize a threat?
- Opportunity:
- Threat Neutralized:
- Customer WTP Impact:
- **Decision:** ☐ Yes ☐ No

## R - Rare
**Question:** Do <10% of competitors possess this?
- Competitors with similar capability:
- Our unique approach:
- **Decision:** ☐ Yes ☐ No

## I - Inimitable (Costly to Copy)
**Question:** Would it take >$100k and >6 months to replicate?
- Path dependency (historical investments):
- Causal ambiguity (complexity):
- Social complexity (team/culture):
- Patents/IP:
- **Decision:** ☐ Yes ☐ No

## O - Organized to Capture Value
**Question:** Can we actually execute and monetize this?
- GTM strategy:
- Operational readiness:
- Culture alignment:
- **Decision:** ☐ Yes ☐ No

## VRIO Outcome
| V | R | I | O | Result |
|---|---|---|---|--------|
| [Y/N] | [Y/N] | [Y/N] | [Y/N] | [Competitive Advantage Level] |

**Strategic Recommendation:**
- If Sustained Advantage → Invest heavily, premium pricing
- If Temporary Advantage → Monetize quickly before copied
- If Parity → Cost leadership or niche focus
- If Disadvantage → Divest or pivot
```

---

## 2. Value Stick (Pricing Power)

**Purpose:** Visualize value creation vs. value capture
**Source:** Felix Oberholzer-Gee (Harvard)

### The Value Stick Model

```
Willingness to Pay (WTP) ──────────────────┐
                                            │ Customer Surplus (Value uncaptured)
Price ─────────────────────────────────────┤
                                            │ Firm Margin (Value captured)
Willingness to Sell (Cost) ────────────────┘
```

**Key Insight:**
- Create value by increasing WTP OR decreasing Cost
- Capture value by optimizing Price (balance Customer Surplus vs Firm Margin)

### Value Stick Analysis: ActiveShield MFA Feature

```
Without MFA:
├─ WTP: $100/mo (baseline)
├─ Price: $100/mo
├─ Cost: $80/mo
└─ Firm Margin: $20/mo (20%)

With MFA:
├─ WTP: $150/mo (+50% due to security value)
│   └─ [Customer Surplus: $30/mo if priced at $120]
├─ Price: $120/mo (strategic)
│   └─ [Firm Margin: $40/mo if cost is $80]
└─ Cost: $80/mo (MFA dev amortized adds $0 marginal cost)

Value Created:
- WTP increased: +$50/mo (100% to customers before pricing)
- Cost unchanged: $80/mo

Value Captured (at $120 price):
- Customer Surplus: $30/mo (keeps customers happy)
- Firm Margin: $40/mo (2× improvement)

Decision: Raise price to $120/mo for MFA tier
→ Win-win: Customers get $30 surplus, firm doubles margin
```

### Strategic Pricing Scenarios

**Scenario A: Maximize Firm Margin**
- Price: $145/mo (near WTP ceiling)
- Customer Surplus: $5/mo (minimal)
- Firm Margin: $65/mo
- Risk: Low surplus → high churn, negative word-of-mouth

**Scenario B: Maximize Customer Surplus**
- Price: $100/mo (no price increase)
- Customer Surplus: $50/mo (huge)
- Firm Margin: $20/mo (unchanged)
- Risk: Leave money on table, unsustainable if costs rise

**Scenario C: Balanced (RECOMMENDED)**
- Price: $120/mo (+20%)
- Customer Surplus: $30/mo (attractive)
- Firm Margin: $40/mo (2× improvement)
- Result: ✅ Sustainable, high NPS, profitable

### Value Stick Template

```markdown
# Value Stick Analysis: [Feature Name]

## Current State (Without Feature)
| Layer | Value |
|-------|-------|
| Willingness to Pay (WTP) | $____ |
| Price | $____ |
| Cost (WTS) | $____ |
| **Customer Surplus** | $____ (WTP - Price) |
| **Firm Margin** | $____ (Price - Cost) |

## Future State (With Feature)
| Layer | Value | Change |
|-------|-------|--------|
| Willingness to Pay (WTP) | $____ | +$____ |
| Price (proposed) | $____ | +$____ |
| Cost (WTS) | $____ | +$____ |
| **Customer Surplus** | $____ | +/- $____ |
| **Firm Margin** | $____ | +/- $____ |

## Value Creation vs Capture

**Total Value Created:**
- WTP increase: $____
- Cost decrease: $____
- **Total:** $____

**Value Capture Strategy:**
- Price increase: $____ (X% of value created)
- Customer keeps: $____ (Y% of value created)
- Rationale: [Why this split?]

**Pricing Recommendation:**
- New Price: $____
- Expected Impact:
  - Customer Surplus: [High/Medium/Low] → [NPS impact]
  - Firm Margin: [X%] → [Profitability impact]
  - Competitive Position: [Comparison to competitors]

**Decision:** ☐ Implement pricing ☐ Adjust ☐ Reject
```

---

## 3. Blue Ocean Strategy

**Purpose:** Create uncontested market space (avoid red ocean competition)
**Source:** W. Chan Kim & Renée Mauborgne (INSEAD)

### The Four Actions Framework

```
        ELIMINATE                RAISE
┌─────────────────────┬─────────────────────┐
│ Which factors the   │ Which factors should│
│ industry takes for  │ be raised well      │
│ granted should be   │ above industry      │
│ eliminated?         │ standard?           │
├─────────────────────┼─────────────────────┤
│ Which factors       │ Which factors the   │
│ should be reduced   │ industry has never  │
│ well below industry │ offered should be   │
│ standard?           │ created?            │
└─────────────────────┴─────────────────────┘
        REDUCE                  CREATE
```

### Example: ActiveShield vs DocuSign (Blue Ocean)

#### ELIMINATE
- ❌ **Complex enterprise contracts** (DocuSign's barrier)
  - ActiveShield: Month-to-month, no annual commitment
  - Outcome: SMBs can afford it

- ❌ **Per-signature pricing** (industry standard)
  - ActiveShield: Flat monthly rate (unlimited signatures)
  - Outcome: Predictable costs, no usage anxiety

#### REDUCE
- 🔽 **Implementation time** (DocuSign: 2-4 weeks)
  - ActiveShield: <24 hours setup
  - Outcome: Faster time-to-value

- 🔽 **Feature bloat** (DocuSign: 200+ features)
  - ActiveShield: Core 20 features (80/20 rule)
  - Outcome: Easier onboarding, lower support burden

#### RAISE
- 🔼 **Security transparency** (industry: opaque)
  - ActiveShield: Open-source cryptography, public audits
  - Outcome: Trust differentiation

- 🔼 **API-first architecture** (industry: UI-first)
  - ActiveShield: Developer-friendly SDKs, webhooks
  - Outcome: Tech-savvy customers choose us

#### CREATE
- ✨ **ShadowTag compliance tagging** (industry first)
  - No competitor offers cryptographic compliance markers
  - Outcome: New category, defensible IP

- ✨ **Compliance-as-a-Service** (automated audit trails)
  - Industry: Manual compliance work
  - ActiveShield: Auto-generate SOC2/HIPAA reports
  - Outcome: 10× faster audits

### Strategy Canvas

```
High │                        ┌──── ActiveShield (Blue Ocean)
     │                       /│
     │                      / │
Value│    ┌────────────────/  │
     │   /│              /    │
     │  / │             /     │
     │ /  │            /      │
Low  │/   │           /       │
     └────┴──────────┴────────┴───────────────────
          │          │        │
       Features  Enterprise Security  Compliance
                 Contracts  Transparency Automation

     DocuSign (Red Ocean) ────
     ActiveShield (Blue Ocean) ────
```

**Strategic Implications:**
- Don't compete on features (red ocean)
- Win on security transparency + compliance automation (blue ocean)
- Price 30% below DocuSign (value pricing, not cost-plus)

### Blue Ocean Canvas Template

```markdown
# Blue Ocean Strategy: [Product/Feature Name]

## Competitive Landscape (Red Ocean)

| Factor | Industry Avg | Competitor A | Competitor B | Us (Current) |
|--------|--------------|--------------|--------------|--------------|
| Factor 1 | [Value] | [Value] | [Value] | [Value] |
| Factor 2 | [Value] | [Value] | [Value] | [Value] |
| ... | ... | ... | ... | ... |

## Four Actions Framework

### ELIMINATE (Industry Norms to Remove)
1. [Factor]: [Why eliminate?]
2. [Factor]: [Customer benefit]

### REDUCE (Below Industry Standard)
1. [Factor]: [New level vs industry]
2. [Factor]: [Cost/complexity savings]

### RAISE (Above Industry Standard)
1. [Factor]: [New level vs industry]
2. [Factor]: [Competitive advantage]

### CREATE (Never Offered Before)
1. [Factor]: [What makes this unique?]
2. [Factor]: [Defensibility/IP]

## New Value Curve (Blue Ocean)

| Factor | Industry | Us (New) | Change | Impact |
|--------|----------|----------|--------|--------|
| Factor 1 | 5 | 1 | REDUCE | -80% |
| Factor 2 | 3 | 8 | RAISE | +167% |
| Factor 3 | 7 | 0 | ELIMINATE | -100% |
| Factor 4 | 0 | 9 | CREATE | NEW |

## Strategic Validation

**Does this strategy...?**
- [ ] Focus on non-customers (expand market)?
- [ ] Break value-cost trade-off (better AND cheaper)?
- [ ] Align activities (internally consistent)?
- [ ] Create barriers to imitation (defensible)?

**Blue Ocean Tests:**
- [ ] Utility: Does it unlock latent demand?
- [ ] Price: Is it accessible to mass of buyers?
- [ ] Cost: Can we profit at this price point?
- [ ] Adoption: What blocks adoption? (address them)

**Decision:** ☐ Pursue Blue Ocean ☐ Refine ☐ Red Ocean competition
```

---

## 4. McKinsey Three Horizons

**Purpose:** Balance short-term performance with long-term growth
**Source:** McKinsey & Company

### The Three Horizons

```
Revenue
  ▲
  │     H1: Defend & Extend Core
  │    ●●●●●●●●●
  │   ●         ●●●
  │  ●             ●●●  H2: Build Emerging Business
  │ ●                 ●●●●●●
  │●                      ●●●●●  H3: Create Transformational Options
  │                           ●●●●●●●
  └───────────────────────────────────────────────▶
   Year 1   Year 2   Year 3   Year 4   Year 5   Time
```

**Horizon 1 (0-2 years):** Defend and extend core business
- Focus: Profitability, efficiency, incremental improvements
- Investment: 70% of resources
- Examples: ActiveShield bug fixes, minor features, sales optimization

**Horizon 2 (2-4 years):** Build emerging businesses
- Focus: New revenue streams adjacent to core
- Investment: 20% of resources
- Examples: ActiveShield API platform, compliance-as-a-service

**Horizon 3 (4-7 years):** Create transformational options
- Focus: Future bets, disruptive innovations
- Investment: 10% of resources
- Examples: AI-powered contract intelligence, blockchain notarization

### ShadowTagAi Portfolio Mapping

| Product/Feature | Horizon | Revenue (Current) | Revenue (Projected) | Investment | Strategic Role |
|-----------------|---------|-------------------|---------------------|------------|----------------|
| **H1 - Core** |
| ActiveShield (current) | H1 | $500k/year | $800k/year (Y2) | $200k/year | Cash cow, fund H2/H3 |
| ShadowTag signing | H1 | $300k/year | $450k/year (Y2) | $100k/year | Differentiation |
| **H2 - Emerging** |
| ActiveShield API | H2 | $0 | $200k/year (Y3) | $150k | Platform play |
| Compliance SaaS | H2 | $50k/year | $400k/year (Y3) | $120k | New market segment |
| **H3 - Transformational** |
| AI Contract Analysis | H3 | $0 | $1M/year (Y5) | $80k (R&D) | Future-proofing |
| Blockchain Notary | H3 | $0 | Unknown | $50k (exploration) | Option value |

### Resource Allocation Check

**Current Allocation:**
- H1: 65% ($300k / $460k total)
- H2: 25% ($115k)
- H3: 10% ($45k)
- Total: $460k/year

**McKinsey Recommendation:**
- H1: 70% (slightly increase core focus)
- H2: 20% (on track)
- H3: 10% (on track)

**Action:** Reallocate $20k from H2 to H1 (strengthen core before scaling)

### Three Horizons Decision Framework

```markdown
# Three Horizons Portfolio Review

## Current Portfolio

### Horizon 1 (Core Business, 0-2 years)
| Initiative | Revenue Now | Revenue Y2 | Investment | ROI |
|------------|-------------|------------|------------|-----|
| [Product 1] | $__k | $__k | $__k | __× |
| [Product 2] | $__k | $__k | $__k | __× |
| **H1 Subtotal** | $__k | $__k | $__k | __× |

### Horizon 2 (Emerging, 2-4 years)
| Initiative | Revenue Now | Revenue Y4 | Investment | Strategic Option Value |
|------------|-------------|------------|------------|------------------------|
| [Initiative 1] | $__k | $__k | $__k | [Platform/Market/Tech] |
| [Initiative 2] | $__k | $__k | $__k | [Platform/Market/Tech] |
| **H2 Subtotal** | $__k | $__k | $__k | |

### Horizon 3 (Transformational, 4-7 years)
| Initiative | Revenue Now | Revenue Y7 | Investment | Learning Goal |
|------------|-------------|------------|------------|---------------|
| [Moonshot 1] | $0 | $__M (?) | $__k | [What to validate?] |
| [Moonshot 2] | $0 | $__M (?) | $__k | [What to validate?] |
| **H3 Subtotal** | $0 | $__M (?) | $__k | |

## Resource Allocation

| Horizon | Actual | Target | Variance | Action |
|---------|--------|--------|----------|--------|
| H1 | __% | 70% | __% | [Increase/Decrease/OK] |
| H2 | __% | 20% | __% | [Increase/Decrease/OK] |
| H3 | __% | 10% | __% | [Increase/Decrease/OK] |

## Portfolio Health Checks

**H1 - Core:**
- [ ] Profitability improving? (target: ≥40% margin)
- [ ] Market share stable or growing?
- [ ] Customer retention ≥90%?

**H2 - Emerging:**
- [ ] At least 2 initiatives in flight?
- [ ] One H2 transitioning to H1 within 12 months?
- [ ] Revenue traction (>$50k ARR or 10+ customers)?

**H3 - Transformational:**
- [ ] At least 1 active bet?
- [ ] Learning milestones defined (not just revenue)?
- [ ] Kill criteria clear (when to abort)?

## Strategic Rebalancing

**Overinvested:** [Horizon X]
- Action: [Reallocate $__k to ...]

**Underinvested:** [Horizon Y]
- Action: [Add $__k from ...]

**Divest/Kill:** [Initiative Z in Horizon _]
- Reason: [Not hitting milestones / strategic misalignment]
- Savings: $__k → Redeploy to [...]

**Decision:** ☐ Rebalance ☐ Hold ☐ Major shift needed
```

---

## 5. Strategy Diamond (Hambrick & Fredrickson)

**Purpose:** Ensure strategy coherence across 5 integrated dimensions
**Source:** Hambrick & Fredrickson (Columbia Business School)

### The Five Elements

```
           ARENAS
         (Where to play)
               │
    ┌──────────┼──────────┐
    │                     │
 VEHICLES              DIFFERENTIATORS
(How to get there)    (How to win)
    │                     │
    └──────────┬──────────┘
               │
          STAGING & PACING
         (Speed & sequence)
               │
         ECONOMIC LOGIC
        (How to make money)
```

### ActiveShield Strategy Diamond Example

**1. ARENAS (Where to Play)**
- **Geography:** North America (primary), Europe (expansion Y3)
- **Product:** Document signing + compliance automation
- **Customer Segments:**
  - Primary: Tech-savvy SMBs (50-500 employees)
  - Secondary: Mid-market enterprises (500-2000 employees)
  - Tertiary: Developers (API-first users)
- **Vertical Markets:** SaaS, fintech, healthcare (compliance-heavy)
- **Value Chain:** Direct SaaS (no channel partners yet)

**2. VEHICLES (How to Get There)**
- **Organic Growth:** Product-led growth (PLG) → freemium model
- **Acquisitions:** None (bootstrap constraints)
- **Alliances:**
  - Zapier integration (distribution)
  - Stripe partnership (payment compliance)
  - Google Cloud partnership (infra credits)

**3. DIFFERENTIATORS (How to Win)**
- **ShadowTag cryptography** (unique tech)
- **Compliance automation** (SOC2/HIPAA reports in 1-click)
- **Developer-first** (API quality > UI polish)
- **Transparent security** (open-source algorithms, public audits)
- **Predictable pricing** (flat rate, no per-signature gouging)

**4. STAGING & PACING (Speed & Sequence)**
- **Phase 1 (Y1-Y2):** Nail SMB market
  - Launch: Core signing + ShadowTag
  - Traction: 500 customers, $500k ARR
- **Phase 2 (Y3-Y4):** Expand enterprise
  - Add: SSO, MFA, advanced compliance
  - Traction: 100 enterprise customers, $2M ARR
- **Phase 3 (Y5-Y7):** Platform play
  - Launch: API marketplace, partner integrations
  - Exit: Acquisition by DocuSign/Adobe ($50M-$100M)

**5. ECONOMIC LOGIC (How to Make Money)**
- **Revenue Model:** SaaS subscription (monthly/annual)
- **Pricing:**
  - Starter: $100/mo (small teams)
  - Professional: $300/mo (growing companies)
  - Enterprise: $1,200/mo (custom)
- **Unit Economics:**
  - CAC: $3,000 (content marketing + sales)
  - LTV: $16,000 (24-month retention, $100 ARPU)
  - LTV:CAC: 5.3:1 ✅
- **Margin Target:** 60% gross, 25% net (at scale)

### Coherence Check

**Does the strategy hang together?**

| Integration | Check | Pass? |
|-------------|-------|-------|
| Arenas ↔ Differentiators | Do our strengths fit chosen markets? | ✅ Yes (tech-savvy SMBs value API-first) |
| Vehicles ↔ Staging | Can PLG get us to $500k ARR in Y2? | ✅ Yes (freemium + virality) |
| Differentiators ↔ Economic Logic | Do unique features justify premium pricing? | ✅ Yes (ShadowTag = 30% price premium) |
| Staging ↔ Economic Logic | Does timeline align with cash flow needs? | ⚠️ Risk (may need bridge funding in Y3) |

**Strategic Tension Identified:**
- Phase 2 enterprise expansion requires $500k investment (sales team, enterprise features)
- Current LTV:CAC assumes bootstrapped growth
- **Resolution:** Raise seed round ($1M) in Y2, or slow expansion to Y4

### Strategy Diamond Template

```markdown
# Strategy Diamond: [Product/Business Name]

## 1. ARENAS (Where We Play)

**Geographies:**
- Primary: [Region]
- Secondary: [Region]
- Future: [Region]

**Products/Services:**
- Core: [Product]
- Adjacent: [Product]
- Future: [Product]

**Customer Segments:**
- Primary: [Segment] (__% of revenue)
- Secondary: [Segment] (__% of revenue)
- Tertiary: [Segment] (__% of revenue)

**Vertical Markets:**
- [Vertical 1]: [Why this vertical?]
- [Vertical 2]: [Why this vertical?]

**Value Chain Position:**
- ☐ Direct to customer
- ☐ Channel partners
- ☐ OEM/reseller
- ☐ Platform/marketplace

## 2. VEHICLES (How We Get There)

**Organic Growth:**
- [Method]: [Timeline/Investment]

**Inorganic Growth:**
- Acquisitions: [Target profile]
- Alliances: [Partner types]
- JVs: [Structure]

**Current Partnerships:**
1. [Partner]: [Strategic value]
2. [Partner]: [Strategic value]

## 3. DIFFERENTIATORS (How We Win)

**Core Strengths:**
1. [Strength]: [Proof point]
2. [Strength]: [Proof point]

**vs Competitor A:**
- We win on: [Factors]

**vs Competitor B:**
- We win on: [Factors]

**Defensibility:**
- ☐ Network effects
- ☐ Switching costs
- ☐ Patents/IP
- ☐ Brand
- ☐ Scale economies
- ☐ Data advantages

## 4. STAGING & PACING (Speed & Sequence)

**Phase 1 (Y1-Y2): [Name]**
- Goals: [Revenue/customer targets]
- Initiatives: [Key projects]
- Investment: $__k
- Success Metrics: [KPIs]

**Phase 2 (Y3-Y4): [Name]**
- Goals: [Targets]
- Initiatives: [Projects]
- Investment: $__k
- Success Metrics: [KPIs]

**Phase 3 (Y5-Y7): [Name]**
- Goals: [Targets]
- Initiatives: [Projects]
- Investment: $__k
- Success Metrics: [KPIs]

## 5. ECONOMIC LOGIC (How We Make Money)

**Revenue Model:**
- [Model type]: [Pricing]

**Unit Economics:**
- CAC: $____ (payback: __ months)
- LTV: $____ (retention: __%)
- LTV:CAC: __:1
- Gross Margin: __%
- Rule of 40: __ (growth% + margin%)

**Path to Profitability:**
- Breakeven: [Month/Year]
- Cash flow positive: [Month/Year]
- Assumptions: [Key drivers]

## Coherence Analysis

**Integration Checks:**

| Linkage | Question | Answer | Pass? |
|---------|----------|--------|-------|
| Arenas ↔ Differentiators | Do strengths fit markets? | [Analysis] | ☐ |
| Vehicles ↔ Staging | Can growth method hit timeline? | [Analysis] | ☐ |
| Differentiators ↔ Economic Logic | Do advantages justify pricing? | [Analysis] | ☐ |
| Staging ↔ Economic Logic | Does cash flow support plan? | [Analysis] | ☐ |

**Strategic Tensions:**
- [Tension 1]: [Resolution]
- [Tension 2]: [Resolution]

**Decision:** ☐ Strategy coherent ☐ Refine ☐ Major gaps
```

---

## Framework Selection Guide

**When to Use Each Framework:**

| Framework | Use Case | Time Required | Complexity |
|-----------|----------|---------------|------------|
| **VRIO** | Validate competitive advantage claims | 30 min | Low |
| **Value Stick** | Pricing decisions, value capture | 1 hour | Medium |
| **Blue Ocean** | Market positioning, avoid competition | 2 hours | High |
| **Three Horizons** | Portfolio balance, resource allocation | 1 hour | Medium |
| **Strategy Diamond** | Holistic strategy check | 2 hours | High |
| **Porter's 5 Forces** | Industry analysis, entry decisions | 1 hour | Medium |
| **BCG Matrix** | Product portfolio, divest/invest | 30 min | Low |

**Decision Tree:**

```
Need to decide on...?
│
├─ New feature → VRIO (is it defensible?) + Value Stick (how to price?)
│
├─ Market positioning → Blue Ocean (uncontested space?)
│
├─ Resource allocation → Three Horizons (balanced portfolio?)
│
├─ Overall strategy → Strategy Diamond (coherent plan?)
│
├─ Industry attractiveness → Porter's 5 Forces
│
└─ Product pruning → BCG Matrix (stars vs dogs?)
```

**Integration with AiYouJR:**

1. **Purpose Gate** → Use Strategy Diamond (arenas, staging)
2. **Reasons Gate** → Use VRIO, Value Stick, Three Horizons
3. **Brakes Gate** → Use Porter's 5 Forces (competitive threats)

---

**Last Updated:** 2025-11-15
**Source:** Harvard Business School, McKinsey, Blue Ocean Strategy Institute
**Integration:** AiYouJR Reasons Gate + CRM-JR strategic analysis
**Maintained By:** ShadowTagAi Strategy (Erik)
