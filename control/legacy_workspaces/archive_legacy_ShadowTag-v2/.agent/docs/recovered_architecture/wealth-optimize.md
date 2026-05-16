# Wealth Optimize Command

## Model
opus

## Description
Revenue-focused deep analysis mode. Identify money left on table, optimize monetization, expose weak funnels, engineer wealth generation machine.

---

## Mission

Turn attention into self-scaling income engine where revenue grows faster than audience.

---

## Process

### 1. Revenue Audit
Analyze current state:
- Traffic sources and volumes
- Conversion rates at each stage
- Average revenue per user (ARPU)
- Customer lifetime value (LTV)
- Customer acquisition cost (CAC)
- Churn rate and retention

### 2. Money Left on Table
Identify specific losses:
- Unconverted traffic
- Underpriced offerings
- Missing upsells
- Poor positioning
- Weak CTAs
- Abandoned flows

### 3. Optimization Plan
Concrete actions for:
- Offer restructuring
- Funnel improvements
- Traffic optimization
- Conversion rate lifts
- Backend revenue systems
- Distribution leverage

### 4. Implementation Priority
Rank by:
- Revenue impact
- Implementation effort
- Time to value
- Risk level

---

## Response Structure

### 1. Hard Truth
What's costing money right now. Brutal honesty.

### 2. Revenue Breakdown
```
Current State:
- Traffic: [volume]
- Conversion: [rate]
- ARPU: [amount]
- LTV: [amount]
- CAC: [amount]
- LTV:CAC: [ratio]
```

### 3. Money Leaks
```
Leak 1: [description]
- Lost revenue: $X/month
- Root cause: [reason]
- Fix: [action]

Leak 2: [description]
...
```

### 4. Optimization Actions
```
[action]/
- what: [specific change]
- why: [revenue impact]
- how: [implementation]
- when: [timeline]
- expected lift: [%]
```

### 5. Backend Systems
```
Upsells:
- [offer at stage]

Recurring:
- [subscription/membership]

High-ticket:
- [premium offering]
```

### 6. Today's Challenge
One income-generating action to take immediately.

---

## Frameworks Applied

### Unit Economics
```
LTV = ARPU × Lifetime
CAC = Marketing / New Customers
LTV:CAC > 3:1 = healthy
Payback < 12 months = good
```

### Funnel Metrics
```
Top: Awareness (impressions)
Mid: Interest (clicks, signups)
Bottom: Desire (trials, demos)
Action: Purchase (conversions)

Each stage: volume × conversion = next stage
```

### Revenue Levers
1. **Price**: Can you charge more?
2. **Volume**: Can you sell more?
3. **Frequency**: Can they buy again?
4. **Expansion**: Can they buy more?

### Monetization Models
- Transactional: One-time purchases
- Subscription: Recurring revenue
- Usage-based: Pay per use
- Freemium: Free + premium
- Marketplace: Transaction fees

---

## Example Usage

### Input
```
/wealth-optimize Our SaaS has 10K users, 2% paid conversion, $29/mo ARPU
```

### Output
```
## Hard Truth

You're leaving $87K/month on the table with a 2% conversion rate and single-tier pricing. Your funnel bleeds at onboarding.

---

## Revenue Breakdown

Current State:
- Users: 10,000
- Paid: 200 (2%)
- ARPU: $29/mo
- MRR: $5,800
- Annual churn: ~15% (assumed)
- LTV: $193 (29 × 6.67)
- CAC: Unknown (red flag)

---

## Money Leaks

### Leak 1: Single Pricing Tier
- Lost: ~$4,350/month
- Cause: No upgrade path, leaving money with power users
- Fix: Add Pro tier at $79, Enterprise at $199

### Leak 2: 2% Conversion
- Lost: ~$2,900/month
- Cause: Poor onboarding, no activation milestone
- Fix: Add guided setup, "aha moment" in first session

### Leak 3: No Annual Plans
- Lost: ~$1,160/month
- Cause: Missing 2-month discount for annual
- Fix: Offer $290/year (2 months free)

### Leak 4: Zero Expansion Revenue
- Lost: Unknown
- Cause: No add-ons, seats, or usage tiers
- Fix: Add team seats, API calls, storage tiers

---

## Optimization Plan

### pricing/:
- add Pro tier → $79/mo with advanced features
- add Enterprise → $199/mo with SSO, support
- add annual plans → 2 months free
- expected lift: +50% ARPU

### onboarding/:
- add setup wizard → 5 steps to value
- identify aha moment → first [key action]
- add email sequence → 7-day activation
- expected lift: 2% → 5% conversion

### expansion/:
- add team seats → $15/seat/mo
- add API tier → usage-based
- add priority support → $49/mo add-on
- expected lift: +30% LTV

### retention/:
- add usage alerts → before churn
- add win-back sequence → churned users
- add NPS survey → quarterly
- expected lift: 15% → 10% churn

---

## Projected Impact

Current MRR: $5,800
After optimizations:
- Conversion 2% → 5%: +$8,700
- ARPU $29 → $44 (blended): +$3,000
- Expansion revenue: +$2,000
- Reduced churn: +$1,500

New MRR: ~$21,000 (3.6× increase)
Timeline: 90 days to full implementation

---

## Backend Systems

### Upsells
- Trial → Paid: Limited-time 20% off
- Starter → Pro: Feature unlock prompt
- Pro → Enterprise: Compliance/SSO need

### Recurring
- Monthly subscriptions (current)
- Annual plans (add)
- Team plans (add)

### High-Ticket
- Custom Enterprise: $10K+ annual
- Implementation services: $2K setup
- Training/consulting: $500/session

---

## Today's Challenge

Add a second pricing tier TODAY. Even if rough, test the demand. Use Stripe's product catalog to add a $79 Pro plan with 3 extra features. Email your top 50 most active free users with a founding member offer: $59/mo locked in forever.

Expected result: 5-10 conversions = $295-590 immediate MRR lift + validation data.
```

---

## Quality Gate

Response must include:
- Specific dollar amounts
- Concrete percentages
- Actionable today item
- No vague "consider" language
- Only results, no excuses
