# Template 09: Revenue Optimization (Existing Product)

## Purpose
Optimize existing product revenue through pricing, packaging, and expansion strategies.

## When to Use
- Revenue growth has stalled
- Want to increase ARPU
- Need to reduce churn
- Exploring new pricing models
- Maximizing existing customer value

---

## Copy-Paste Prompt

```
Optimize revenue for existing product:

**Product Overview**:
- Product: [Name and description]
- Business Model: [SaaS / Usage-based / etc.]
- Stage: [Early-stage / Growth / Mature]

**Current Revenue Metrics**:
- MRR/ARR: [$X]
- Number of Customers: [X]
- ARPU: [$X/month]
- Churn Rate: [X%/month]
- LTV/CAC: [X:1]
- Gross Margin: [X%]

**Current Pricing**:
- [Tier 1]: [$X/month] - [Features]
- [Tier 2]: [$Y/month] - [Features]
- [Tier 3]: [$Z/month] - [Features]

**Revenue Challenges**:
1. [Challenge 1 - e.g., high churn]
2. [Challenge 2 - e.g., low upgrade rate]
3. [Challenge 3 - e.g., revenue concentration risk]

**Revenue Goals**:
- Target MRR/ARR: [$X in Y months]
- Target ARPU: [$X/month] (up from $Y)
- Target Churn: [X%] (down from Y%)
- Target LTV/CAC: [X:1]

**Opportunities** (what you suspect):
- [ ] Pricing is too low
- [ ] Missing value-based tier
- [ ] No expansion revenue strategy
- [ ] Packaging doesn't match usage
- [ ] [Other opportunities]

**Constraints**:
- Can't alienate existing customers
- Limited engineering resources for new features
- [Other constraints]

**Deliverables**:
1. Revenue analysis (where revenue is leaking)
2. Optimized pricing strategy
3. Expansion revenue playbook
4. Migration plan (how to implement changes)
5. Expected revenue impact (projections)
```

---

## Example Usage

```
Optimize revenue for existing product:

**Product Overview**:
- Product: DevMetrics - Analytics platform for engineering teams
- Business Model: SaaS subscription with usage-based overage
- Stage: Early-stage (12 months post-launch)

**Current Revenue Metrics**:
- MRR: $15K
- Number of Customers: 50
- ARPU: $300/month
- Churn Rate: 8%/month (high!)
- LTV/CAC: 2:1 (need to improve)
- Gross Margin: 85%

**Current Pricing**:
- Starter: $99/month - 1 team, 10 developers, basic metrics
- Team: $299/month - 3 teams, 30 developers, advanced metrics
- Enterprise: $999/month - Unlimited, custom integrations, SSO

**Revenue Challenges**:
1. High churn (8%/month) - losing ~4 customers/month
2. Most customers on Starter plan (70% of customers)
3. Very few customers upgrade to Enterprise
4. No expansion revenue from existing customers
5. Revenue concentration (top 5 customers = 40% of revenue)

**Revenue Goals**:
- Target MRR: $50K in 6 months, $100K in 12 months
- Target ARPU: $600/month (double current)
- Target Churn: 3%/month (reduce by 60%)
- Target LTV/CAC: 5:1

**Opportunities** (what you suspect):
- [X] Pricing is too low (customers say we're cheap)
- [X] Missing value-based tier (teams with 50+ devs have nowhere to go)
- [X] No expansion revenue strategy (no upsells, no add-ons)
- [X] Packaging doesn't match usage (customers hit limits, churn instead of upgrade)
- [X] Not charging for key value drivers (integrations, data retention)

**Constraints**:
- Can't raise prices on existing customers without providing value
- Limited engineering (2 engineers, focused on core product)
- Must maintain indie/startup friendliness (can't price out small teams)

**Deliverables**:
1. Revenue analysis (where revenue is leaking)
2. Optimized pricing strategy
3. Expansion revenue playbook
4. Migration plan (how to implement changes)
5. Expected revenue impact (projections)
```

---

## Expected Output Structure

```
# REVENUE ANALYSIS (Research + Revenue Agents)

## Current State Diagnosis

### Revenue Breakdown
- Starter (35 customers @ $99): $3,465/month (23%)
- Team (12 customers @ $299): $3,588/month (24%)
- Enterprise (3 customers @ $999): $2,997/month (20%)
- **Problem**: 70% of customers on lowest tier

### Churn Analysis
**Current Churn**: 8%/month (~4 customers)

**Churn Reasons** (from analysis):
1. [Reason 1]: Hit usage limits, didn't upgrade (40% of churn)
2. [Reason 2]: Didn't see value (30% of churn)
3. [Reason 3]: Price increase request (20% of churn)
4. [Reason 4]: Other (10%)

**Churn Prevention Opportunities**:
- Better usage limit warnings → automatic upgrade suggestions
- Improved onboarding → faster time-to-value
- Usage-based pricing → no hard limits

---

## Revenue Leak Identification

### Leak #1: Underpriced Value
**Problem**: Customers say product is "cheap" - willingness to pay is higher
**Annual Revenue Lost**: ~$36K (estimated)
**Fix**: Raise prices 20-30%

### Leak #2: No Expansion Revenue
**Problem**: No way to extract more value from happy customers
**Annual Revenue Lost**: ~$50K (estimated)
**Fix**: Add expansion paths (add-ons, usage-based components)

### Leak #3: Wrong Value Metric
**Problem**: Charging per developer, but value is in integrations and data
**Annual Revenue Lost**: ~$24K (estimated)
**Fix**: Add integration-based pricing

### Leak #4: Churn Before Upgrade
**Problem**: Customers hit limits, churn instead of upgrading
**Annual Revenue Lost**: ~$40K (estimated)
**Fix**: Usage-based overage pricing

**Total Revenue Leak**: ~$150K/year

---

# OPTIMIZED PRICING STRATEGY (Revenue Agent)

## New Value Metric
**Primary**: Team size (# of developers)
**Secondary**: Integrations (# of connected tools)
**Usage-based**: Data retention (months of history)

**Rationale**: Aligns with value delivered, creates expansion revenue

---

## New Tier Structure

### Free (Community)
- **Price**: $0
- **Target**: Individual developers, open source
- **Features**:
  - 1 team, up to 5 developers
  - 3 integrations
  - 30 days data retention
  - Community support
- **Purpose**: Drive adoption, viral growth

---

### Starter (NEW)
- **Price**: $49/month (NEW - lower entry price)
- **Target**: Side projects, small startups
- **Features**:
  - 1 team, up to 10 developers
  - 5 integrations
  - 90 days data retention
  - Email support
- **Positioning**: Affordable entry point
- **Change**: New tier to capture indie hackers

---

### Team (REVISED)
- **Price**: $199/month (down from $299)
- **Target**: Small engineering teams (10-30 devs)
- **Features**:
  - 3 teams, up to 30 developers
  - 10 integrations
  - 6 months data retention
  - Priority support
- **Positioning**: Core product for small teams
- **Change**: Lower price, clearer positioning

---

### Growth (NEW)
- **Price**: $499/month
- **Target**: Growing companies (30-100 devs)
- **Features**:
  - Unlimited teams, up to 100 developers
  - 25 integrations
  - 12 months data retention
  - Dedicated support
  - SSO, audit logs
- **Positioning**: For scaling companies
- **Change**: New tier filling the gap to Enterprise

---

### Enterprise (REVISED)
- **Price**: Starting at $1,999/month (up from $999)
- **Target**: Large companies (100+ devs)
- **Features**:
  - Unlimited everything
  - Custom integrations
  - Unlimited data retention
  - White-glove support
  - SLA, custom contract
- **Positioning**: Premium offering
- **Change**: Higher price reflects value

---

## Add-Ons (Expansion Revenue)
1. **Additional Integrations**: $20/month per integration above plan limit
2. **Extended Data Retention**: $50/month for +6 months retention
3. **Advanced Analytics**: $100/month for predictive insights
4. **API Access**: $150/month for full API access

**Expected Add-On Revenue**: $5K-10K/month additional

---

## Competitive Positioning
- **vs Competitor A**: [Positioning]
- **vs Competitor B**: [Positioning]
- **Differentiation**: [What makes you worth more]

---

# EXPANSION REVENUE PLAYBOOK

## Strategy 1: Usage-Based Upsells
**Trigger**: Customer approaches 80% of limit
**Action**: Automated email suggesting upgrade
**Expected Impact**: Reduce churn by 30%, increase upgrades by 50%

## Strategy 2: Add-On Suggestions
**Trigger**: Customer uses feature X frequently
**Action**: Suggest relevant add-on
**Expected Impact**: $5K/month in add-on revenue

## Strategy 3: Annual Plans
**Offer**: 2 months free on annual payment
**Expected Impact**: Improve cash flow, reduce churn

## Strategy 4: Team Expansion
**Trigger**: Team adds more developers
**Action**: Automatic tier suggestion
**Expected Impact**: Capture growth in customer organizations

---

# MIGRATION PLAN (Workflow Agent)

## Phase 1: Grandfathering (Month 1)
- [ ] Announce new pricing to existing customers
- [ ] Grandfather existing customers at current price for 6 months
- [ ] Offer early upgrade incentives (20% off Growth plan)
- **Goal**: Maintain customer trust

## Phase 2: New Customer Rollout (Month 1)
- [ ] Launch new pricing for all new signups
- [ ] Update website, pricing page
- [ ] A/B test messaging
- **Goal**: Start capturing higher ARPU

## Phase 3: Existing Customer Migration (Months 2-6)
- [ ] Month 2: Email campaign explaining new value
- [ ] Month 3: Offer migration with bonus features
- [ ] Month 4-6: Gradual migration of willing customers
- [ ] Month 6: End grandfather period
- **Goal**: Migrate 80%+ of customers

## Phase 4: Expansion Revenue (Months 3-12)
- [ ] Month 3: Launch add-ons
- [ ] Month 4: Automated upsell emails
- [ ] Month 6: Annual plan push
- **Goal**: 20% of revenue from expansion

---

# EXPECTED REVENUE IMPACT

## Conservative Scenario

### Assumptions
- 20% of existing customers churn during migration
- 50% of customers upgrade tiers
- Add-ons adopted by 10% of customers
- New pricing attracts similar customer volume

### Projections
- **Month 6**: $35K MRR (133% growth)
- **Month 12**: $75K MRR (400% growth)
- **Churn**: 4% (down from 8%)
- **ARPU**: $500/month (up from $300)

---

## Base Scenario

### Assumptions
- 10% customer churn during migration
- 60% of customers upgrade tiers
- Add-ons adopted by 20% of customers
- New pricing attracts 20% more customers

### Projections
- **Month 6**: $50K MRR (233% growth)
- **Month 12**: $100K MRR (567% growth)
- **Churn**: 3% (down from 8%)
- **ARPU**: $600/month (up from $300)

---

## Aggressive Scenario

### Assumptions
- 5% customer churn during migration
- 70% of customers upgrade tiers
- Add-ons adopted by 30% of customers
- New pricing attracts 50% more customers (better positioning)

### Projections
- **Month 6**: $70K MRR (367% growth)
- **Month 12**: $150K MRR (900% growth)
- **Churn**: 2% (down from 8%)
- **ARPU**: $750/month (up from $300)

---

# IMPLEMENTATION CHECKLIST

## Week 1: Analysis & Planning
- [ ] Validate pricing with customer interviews
- [ ] Create detailed migration communications
- [ ] Build pricing page mockups

## Week 2: Technical Setup
- [ ] Update billing system (Stripe)
- [ ] Build usage-based metering
- [ ] Create add-on purchase flow

## Week 3: Communication
- [ ] Email existing customers about changes
- [ ] Publish new pricing page
- [ ] Update all marketing materials

## Week 4-8: Migration
- [ ] Monitor customer reactions
- [ ] Offer migration assistance
- [ ] Track key metrics daily

## Month 3+: Optimization
- [ ] A/B test pricing page
- [ ] Optimize upsell emails
- [ ] Launch annual plans
```

---

## Tips for Best Results

1. **Start with Data**: Know your actual metrics before optimizing
2. **Talk to Customers**: Validate pricing with real willingness-to-pay research
3. **Grandfather Existing**: Don't force existing customers to migrate immediately
4. **Test Incrementally**: Don't change everything at once
5. **Track Everything**: Monitor churn, upgrades, satisfaction closely

---

## Related Templates
- [04: Monetization Strategy](#) - For new product pricing
- [01: Deep Research](#) - For competitive pricing research
- [03: High-Converting Copy](#) - For pricing page copy
