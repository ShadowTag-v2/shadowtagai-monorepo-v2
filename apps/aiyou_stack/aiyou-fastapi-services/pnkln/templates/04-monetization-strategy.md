# Template 04: Monetization & Revenue Strategy

## Purpose
Design revenue models, pricing strategies, and backend monetization systems.

## When to Use
- Launching new products
- Optimizing existing pricing
- Exploring revenue models
- Designing subscription tiers
- Fixing revenue leaks

---

## Copy-Paste Prompt

```
@revenue Design monetization strategy

Design a comprehensive monetization strategy:

**Business Context**:
- Business Model: [SaaS / Marketplace / API / etc.]
- Product/Service: [What you're selling]
- Target Customer: [Specific customer segment]
- Stage: [Pre-launch / Early-stage / Growth / Scaling]

**Current State** (if applicable):
- Current MRR/ARR: [$X]
- Number of Customers: [X]
- Churn Rate: [X%]
- Average Deal Size: [$X]
- LTV/CAC Ratio: [X:1]

**Competitive Landscape**:
- Competitor 1: [How they monetize]
- Competitor 2: [How they monetize]
- Competitor 3: [How they monetize]

**Goals**:
- Target MRR/ARR: [$X in Y months]
- Ideal Customer Profile (ICP): [Description]
- Unit Economics Target: [LTV/CAC ratio goal]

**Constraints**:
- [Technical constraints]
- [Market constraints]
- [Team constraints]

**Deliverables**:
1. Revenue model recommendation with rationale
2. Pricing strategy (tiers, price points, features)
3. Implementation roadmap (phases and timelines)
4. Technical requirements (payment systems, tracking)
5. Risk assessment and mitigation
6. Optimization playbook (how to grow revenue)
7. Financial projections (conservative/base/aggressive)
```

---

## Example Usage

```
@revenue Design monetization strategy

Design a comprehensive monetization strategy:

**Business Context**:
- Business Model: Developer-focused SaaS (API + Dashboard)
- Product/Service: AI agent orchestration platform
- Target Customer: Individual developers and small engineering teams (1-10 devs)
- Stage: Pre-launch (beta ready)

**Current State**:
- Current MRR/ARR: $0 (pre-launch)
- Beta Users: 50
- Target: $50K MRR in 6 months

**Competitive Landscape**:
- LangChain: Free OSS + LangSmith (usage-based SaaS)
- Vercel AI SDK: Free OSS + Vercel platform (usage-based)
- Anthropic Claude: API (usage-based, token pricing)

**Goals**:
- Target MRR: $50K in 6 months, $200K in 12 months
- Ideal Customer Profile: Solo developers and startups building AI agents
- Unit Economics Target: LTV/CAC > 3:1

**Constraints**:
- Need free tier for developer adoption
- Must support indie hackers (price-sensitive)
- Simple billing (avoid complex metering if possible)

**Deliverables**:
1. Revenue model recommendation with rationale
2. Pricing strategy (tiers, price points, features)
3. Implementation roadmap (phases and timelines)
4. Technical requirements (payment systems, tracking)
5. Risk assessment and mitigation
6. Optimization playbook (how to grow revenue)
7. Financial projections (conservative/base/aggressive)
```

---

## Expected Output Structure

```
## Revenue Model Recommendation

### Recommended Model: [Freemium + Usage-Based Hybrid]

**Rationale**:
- [Why this model fits your market]
- [Why this model fits your customer]
- [Expected unit economics]

**Model Components**:
1. [Component 1]: [Description]
2. [Component 2]: [Description]

---

## Pricing Strategy

### Value Metric
What to charge for: [API calls / Users / Projects / Compute time]

**Why This Metric**: [Aligns with value delivered]

### Tier Structure

**Free Tier** (Community)
- [Feature 1]
- [Feature 2]
- [Feature 3]
- Limitations: [X requests/month]
- Purpose: Drive adoption, build community

**Tier 1** - [$X/month]
- Everything in Free, plus:
- [Premium feature 1]
- [Premium feature 2]
- [X requests/month]
- Target: Solo developers, side projects

**Tier 2** - [$Y/month]
- Everything in Tier 1, plus:
- [Premium feature 3]
- [Premium feature 4]
- [Y requests/month]
- Target: Small teams, production apps

**Tier 3** - [Enterprise - Custom]
- Everything in Tier 2, plus:
- [Enterprise feature 1]
- [Enterprise feature 2]
- Unlimited usage
- Target: Large companies, mission-critical

### Pricing Rationale
- [Why these price points]
- [Price anchoring strategy]
- [Competitor positioning]

---

## Implementation Roadmap

### Phase 1: MVP Monetization (Month 1)
- [ ] Implement Free tier
- [ ] Set up Stripe
- [ ] Basic usage tracking
- [ ] Simple upgrade flow
- **Goal**: First paying customer

### Phase 2: Full System (Months 2-3)
- [ ] All tiers live
- [ ] Advanced metering
- [ ] Billing automation
- [ ] Revenue analytics
- **Goal**: $5K MRR

### Phase 3: Optimization (Months 4-6)
- [ ] A/B test pricing
- [ ] Expansion revenue features
- [ ] Churn reduction automation
- **Goal**: $50K MRR

---

## Technical Blueprint

### Payment Provider: [Stripe]
**Why**: [Developer-friendly, supports usage-based]

### Integration Requirements:
1. **Stripe Checkout**: For subscriptions
2. **Stripe Metering**: For usage tracking
3. **Stripe Billing**: For automated invoicing
4. **Webhooks**: For subscription events

### Data Tracking:
- Usage metrics: [What to track]
- Revenue metrics: [MRR, churn, expansion]
- Customer health: [Usage patterns, churn risk]

### Analytics Dashboard:
- Real-time MRR
- Churn rate
- Expansion revenue
- Cohort analysis

---

## Risk Assessment

### Risk 1: [Low willingness to pay]
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Start with generous free tier, prove value first

### Risk 2: [Complex metering issues]
- **Likelihood**: High
- **Impact**: Medium
- **Mitigation**: Start simple, add complexity later

### Risk 3: [Competitive pricing pressure]
- **Likelihood**: High
- **Impact**: Medium
- **Mitigation**: Differentiate on value, not price

---

## Optimization Playbook

### Months 1-3: Launch and Learn
- **Focus**: Get first 100 paying customers
- **Tactics**: Manual outreach, feedback loops
- **Experiments**: None (too early)

### Months 4-6: First Optimizations
- **Focus**: Reduce churn, increase ARPU
- **Tactics**: Usage-based emails, upgrade nudges
- **Experiments**: Pricing tests on Free → Paid

### Months 7-12: Scale Revenue
- **Focus**: Expansion revenue, enterprise
- **Tactics**: Feature gating, annual plans
- **Experiments**: Multi-variate pricing tests

### Ongoing: Experimentation Framework
- Test every month: [What to test]
- Track: [Key metrics]
- Iterate: [Decision framework]

---

## Financial Projections

### Conservative Scenario
- Month 6: $20K MRR
- Month 12: $80K MRR
- Assumptions: [List assumptions]

### Base Scenario
- Month 6: $50K MRR
- Month 12: $200K MRR
- Assumptions: [List assumptions]

### Aggressive Scenario
- Month 6: $100K MRR
- Month 12: $400K MRR
- Assumptions: [List assumptions]
```

---

## Tips for Best Results

1. **Be Honest About Stage**: Pre-launch vs scaling have different strategies
2. **Share Actual Numbers**: Real data = better recommendations
3. **Know Your Competitors**: How they monetize influences your strategy
4. **Define Success**: What does "good" revenue look like?
5. **Surface Constraints**: Free tier required? Budget limits?

---

## Related Templates
- [01: Deep Research](#) - Research competitive pricing first
- [03: High-Converting Copy](#) - Create pricing page copy
