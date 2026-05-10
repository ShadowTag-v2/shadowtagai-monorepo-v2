# Monte Carlo Scenario Analysis Templates

**Purpose:** Generate probability-weighted financial projections for ShadowTag-v2JR Reasons Gate
**Tool:** Google Sheets formulas (no special software required)
**Output:** Base/Best/Worst scenarios + probability-weighted NPV

---

## Overview

Monte Carlo simulation models uncertainty by running thousands of scenarios with varying inputs. For ShadowTagAi, we use a simplified 3-scenario approach that's fast enough for decision-making but rigorous enough for Army RM Stage IV compliance.

**Three Scenarios:**
1. **Base Case** (50% probability) - Realistic assumptions
2. **Best Case** (25% probability) - Optimistic but achievable
3. **Worst Case** (25% probability) - Pessimistic assumptions

---

## Google Sheets Template

### Setup

```
Column A: Variable Name
Column B: Base Case
Column C: Best Case
Column D: Worst Case
Column E: Probability
Column F: Weighted Value
```

### Example: New Feature ROI Analysis

| Variable | Base | Best | Worst | Formula |
|----------|------|------|-------|---------|
| **INPUTS** |
| Dev Hours | 200 | 160 | 300 | |
| Hourly Rate | $150 | $150 | $150 | |
| Infra Cost/mo | $500 | $450 | $650 | |
| Months to Launch | 3 | 2 | 5 | |
| Customers Y1 | 100 | 150 | 50 | |
| Avg Revenue/Customer | $2,000 | $2,500 | $1,500 | |
| Churn Rate | 10% | 5% | 20% | |
| | | | | |
| **CALCULATED** |
| Dev Cost | $30,000 | $24,000 | $45,000 | =B2*B3 |
| Infra Cost (18mo) | $9,000 | $8,100 | $11,700 | =B4*18 |
| Total Investment | $39,000 | $32,100 | $56,700 | =B8+B9 |
| Y1 Revenue | $200,000 | $375,000 | $75,000 | =B6*B7 |
| Y2 Revenue (net churn) | $180,000 | $356,250 | $60,000 | =B11*(1-B8) |
| 18mo Revenue | $300,000 | $562,500 | $112,500 | =(B11+B12)*0.75 |
| ROI | 6.69× | 16.52× | 0.98× | =(B13-B10)/B10 |
| | | | | |
| **WEIGHTED** |
| Probability | 50% | 25% | 25% | |
| Weighted ROI | 3.35× | 4.13× | 0.25× | =B14*B16 |
| **Expected ROI** | **7.73×** | | | =SUM(B17:D17) |

### Formulas Explained

```
Dev Cost = Dev Hours × Hourly Rate
Infra Cost = Monthly Cost × 18 months
Total Investment = Dev Cost + Infra Cost (18mo)

Y1 Revenue = Customers × Avg Revenue
Y2 Revenue = Y1 Revenue × (1 - Churn Rate)
18mo Revenue = (Y1 + Y2) × 0.75 (pro-rated)

ROI = (Revenue - Investment) / Investment

Expected ROI = Σ (ROI_scenario × Probability_scenario)
```

---

## NPV Calculation Template

### Setup

```
Time Period (months): 0, 1, 2, ..., 18
Cash Flows: Investment (negative), Revenue (positive)
Discount Rate: 15% annually = 1.17% monthly
```

### Example NPV Calculation

| Month | Base Cash Flow | Discounted CF | Best Cash Flow | Discounted CF | Worst Cash Flow | Discounted CF |
|-------|----------------|---------------|----------------|---------------|-----------------|---------------|
| 0 | -$39,000 | -$39,000 | -$32,100 | -$32,100 | -$56,700 | -$56,700 |
| 1 | -$500 | -$494 | -$450 | -$445 | -$650 | -$642 |
| 2 | -$500 | -$489 | -$450 | -$440 | -$650 | -$635 |
| 3 | $5,000 | $4,828 | $10,000 | $9,656 | $2,000 | $1,931 |
| 4 | $15,000 | $14,328 | $25,000 | $23,880 | $5,000 | $4,776 |
| ... | ... | ... | ... | ... | ... | ... |
| 18 | $25,000 | $20,127 | $40,000 | $32,203 | $10,000 | $8,051 |
| **NPV** | | **$156,234** | | **$312,456** | | **$12,345** |

### NPV Formula (Google Sheets)

```
=NPV(discount_rate/12, B2:B19) + B1

Where:
- discount_rate = 15% annually (0.15)
- /12 converts to monthly rate
- B2:B19 = Monthly cash flows (excluding initial investment)
- B1 = Initial investment (negative)
```

### Weighted NPV

```
Expected NPV = (Base NPV × 0.5) + (Best NPV × 0.25) + (Worst NPV × 0.25)
             = ($156k × 0.5) + ($312k × 0.25) + ($12k × 0.25)
             = $78k + $78k + $3k
             = $159k ✅ POSITIVE

Probability of Positive NPV = 75% (Base + Best scenarios)
```

---

## LTV:CAC Template

### Customer Lifetime Value (LTV)

| Variable | Base | Best | Worst |
|----------|------|------|-------|
| Avg Revenue/Customer/Year | $2,000 | $2,500 | $1,500 |
| Gross Margin | 80% | 85% | 75% |
| Churn Rate (annual) | 10% | 5% | 20% |
| **LTV** | **$16,000** | **$42,500** | **$5,625** |

**Formula:**
```
LTV = (Avg Revenue × Gross Margin) / Churn Rate

Base: ($2,000 × 0.8) / 0.1 = $16,000
Best: ($2,500 × 0.85) / 0.05 = $42,500
Worst: ($1,500 × 0.75) / 0.2 = $5,625
```

### Customer Acquisition Cost (CAC)

| Variable | Base | Best | Worst |
|----------|------|------|-------|
| Marketing Spend/mo | $10,000 | $8,000 | $15,000 |
| Sales Costs/mo | $5,000 | $4,000 | $7,000 |
| New Customers/mo | 5 | 8 | 3 |
| **CAC** | **$3,000** | **$1,500** | **$7,333** |

**Formula:**
```
CAC = (Marketing + Sales) / New Customers

Base: ($10k + $5k) / 5 = $3,000
Best: ($8k + $4k) / 8 = $1,500
Worst: ($15k + $7k) / 3 = $7,333
```

### LTV:CAC Ratio

| Scenario | LTV | CAC | Ratio | Gate |
|----------|-----|-----|-------|------|
| Base | $16,000 | $3,000 | 5.33:1 | ✅ PASS |
| Best | $42,500 | $1,500 | 28.33:1 | ✅ PASS |
| Worst | $5,625 | $7,333 | 0.77:1 | ❌ FAIL |

**Weighted LTV:CAC:**
```
= (5.33 × 0.5) + (28.33 × 0.25) + (0.77 × 0.25)
= 2.67 + 7.08 + 0.19
= 9.94:1 ✅ PASS (≥4:1 threshold)
```

---

## Sensitivity Analysis

Identify which variables have the biggest impact on ROI.

### Setup

| Variable | -20% Impact | Base | +20% Impact | Sensitivity |
|----------|-------------|------|-------------|-------------|
| Dev Hours | ROI: 8.4× | ROI: 6.7× | ROI: 5.6× | HIGH |
| Customers Y1 | ROI: 4.0× | ROI: 6.7× | ROI: 9.4× | HIGH |
| Churn Rate | ROI: 7.2× | ROI: 6.7× | ROI: 6.3× | LOW |
| Avg Revenue | ROI: 4.0× | ROI: 6.7× | ROI: 9.4× | HIGH |
| Infra Cost | ROI: 6.9× | ROI: 6.7× | ROI: 6.5× | LOW |

**High-Leverage Factors:** Dev Hours, Customers Y1, Avg Revenue
**Mitigation:** Focus on reducing dev time and increasing customer acquisition

---

## Full Scenario Template (Copy-Paste Ready)

```markdown
# [Feature Name] - Monte Carlo Analysis

Generated: [Date]
Analyst: [Name]

## Input Assumptions

### Development Costs
| Variable | Base | Best | Worst |
|----------|------|------|-------|
| Backend Dev Hours | 120 | 96 | 180 |
| Frontend Dev Hours | 80 | 64 | 120 |
| QA/Testing Hours | 40 | 32 | 60 |
| Hourly Rate | $150 | $150 | $150 |
| **Total Dev Cost** | $36,000 | $28,800 | $54,000 |

### Infrastructure Costs (18 months)
| Variable | Base | Best | Worst |
|----------|------|------|-------|
| Cloud Hosting/mo | $500 | $400 | $700 |
| AI Compute/mo | $300 | $200 | $500 |
| Database/mo | $200 | $150 | $300 |
| **Total Infra (18mo)** | $18,000 | $13,500 | $27,000 |

### Timeline
| Variable | Base | Best | Worst |
|----------|------|------|-------|
| Dev Timeline (months) | 3 | 2 | 5 |
| Ramp-up Period (months) | 3 | 2 | 6 |
| Time to Full Adoption (months) | 12 | 9 | 18 |

### Revenue Assumptions
| Variable | Base | Best | Worst |
|----------|------|------|-------|
| New Customers Y1 | 100 | 150 | 50 |
| Avg Revenue/Customer | $2,000 | $2,500 | $1,500 |
| Conversion Rate | 5% | 7% | 3% |
| Churn Rate | 10% | 5% | 20% |

## Scenario Results

### Base Case (50% Probability)
- Total Investment: $54,000
- 18-month Revenue: $300,000
- ROI: 4.56×
- NPV (15% discount): $182,340
- LTV:CAC: 5.33:1
- Payback Period: 6 months
- **Decision:** ✅ PASS all gates

### Best Case (25% Probability)
- Total Investment: $42,300
- 18-month Revenue: $562,500
- ROI: 12.30×
- NPV (15% discount): $398,765
- LTV:CAC: 28.33:1
- Payback Period: 3 months
- **Decision:** ✅ PASS all gates

### Worst Case (25% Probability)
- Total Investment: $81,000
- 18-month Revenue: $112,500
- ROI: 0.39× ❌
- NPV (15% discount): -$15,234
- LTV:CAC: 0.77:1 ❌
- Payback Period: 24+ months
- **Decision:** ❌ FAIL Reasons gate

## Probability-Weighted Results

- **Expected ROI:** 5.81× ✅ PASS (≥3×)
- **Expected NPV:** $191,618 ✅ POSITIVE
- **Expected LTV:CAC:** 11.48:1 ✅ PASS (≥4:1)
- **Probability of Positive NPV:** 75% ✅ PASS (≥70%)

## Sensitivity Analysis

High-impact variables (±20% change):
1. **New Customers Y1:** ±60% ROI change
2. **Avg Revenue/Customer:** ±45% ROI change
3. **Dev Timeline:** ±35% ROI change

Low-impact variables:
- Churn Rate: ±10% ROI change
- Infra Costs: ±8% ROI change

## Risk Mitigation

To de-risk high-impact variables:
- [ ] **New Customers:** Pre-sell to 20 customers before dev (validate demand)
- [ ] **Avg Revenue:** Survey existing customers for pricing sensitivity
- [ ] **Dev Timeline:** Use experienced contractor (reduce uncertainty)

## ShadowTag-v2JR Decision

### Reasons Gate: ✅ PASS

- ROI ≥3×: Yes (5.81× expected)
- LTV:CAC ≥4:1: Yes (11.48:1 expected)
- NPV ≥70% positive: Yes (75% probability)

**Recommendation:** GO - Proceed with implementation

**Conditions:**
- Validate pricing with customer interviews before launch
- Monitor churn closely (kill-switch if >15% in first 6 months)
- Reassess after Phase 1 (before scaling to all customers)

## Next Steps

1. Create dev docs: `/dev-docs [Feature Name]`
2. Start Phase 1: Backend implementation
3. Schedule gate review after 4 weeks
4. Track actuals vs. projections monthly
```

---

## Tools & Resources

### Google Sheets Templates

Create a copy of this template:
```
File > Make a copy
Rename: "[Feature Name] - Monte Carlo Analysis"
Share with: Strategy team only
```

**Template includes:**
- Input assumptions (editable)
- Automatic calculations
- Charts (ROI distribution, NPV over time)
- Sensitivity analysis (tornado chart)

### Python Script (Advanced)

For running 1000+ simulations:

```python
import numpy as np
import pandas as pd

# Input ranges
dev_hours = np.random.normal(200, 40, 1000)  # Mean 200, StdDev 40
customers_y1 = np.random.normal(100, 20, 1000)
avg_revenue = np.random.normal(2000, 300, 1000)
churn_rate = np.random.uniform(0.05, 0.20, 1000)

# Calculate ROI for each simulation
investment = dev_hours * 150 + 18000  # Dev + Infra
revenue_18mo = customers_y1 * avg_revenue * (1 + (1 - churn_rate)) * 0.75
roi = (revenue_18mo - investment) / investment

# Results
roi_mean = np.mean(roi)
roi_median = np.median(roi)
prob_positive_npv = np.sum(roi > 0) / len(roi) * 100

print(f"Expected ROI: {roi_mean:.2f}×")
print(f"Median ROI: {roi_median:.2f}×")
print(f"Probability of Positive NPV: {prob_positive_npv:.1f}%")

# Percentiles
print(f"10th percentile: {np.percentile(roi, 10):.2f}×")
print(f"90th percentile: {np.percentile(roi, 90):.2f}×")
```

---

## Best Practices

1. **Conservative Base Case:** Use historical data, not aspirational targets
2. **Realistic Best/Worst:** Within 2 standard deviations of base
3. **Document Assumptions:** Every number needs a source or rationale
4. **Update Monthly:** Compare actuals vs. projections, refine model
5. **Sensitivity First:** Focus on high-impact variables, ignore noise
6. **Validate with Customers:** Don't guess pricing/demand - ask users

---

## Common Mistakes

❌ **Overly optimistic base case**
```
Base Case: 500 customers Y1 (when you have 50 today)
```

❌ **Ignoring time value of money**
```
ROI = Total Revenue / Investment (no discounting)
```

❌ **Forgetting maintenance costs**
```
Investment = Dev Cost only (missing ongoing infra/support)
```

❌ **Equal probability scenarios**
```
Base/Best/Worst all at 33.3% (unrealistic)
```

✅ **Correct: Conservative + Validated**
```
Base Case: 100 customers Y1 (2× current growth rate)
Source: Historical data from past 12 months
Validated: Pre-sold to 20 beta customers
```

---

**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi Finance Team (Erik)
**Framework:** ShadowTag-v2JR Reasons Gate
**Discount Rate:** 15% (standard for bootstrapped startups)
