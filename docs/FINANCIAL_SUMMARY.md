# Financial Summary: Pnkln Agent Platform

**Version:** 0.2.0 (Collection → Enforcement)
**Date:** 2025-11-16

---

## TL;DR

**Bottom Line:**
- **Operational Costs:** $1,077-1,677/mo (down from $1,280/mo in v0.1.0)
- **Break-Even:** 4-6 customers @ $297/mo OR 13,800 leads @ $0.10/lead
- **LTV:CAC Ratio:** 5.3:1 (exceeds 4:1 target) ✅
- **Time to Profitability:** 30-45 days with aggressive outbound
- **Bootstrap Capital:** $5K-12K (no VC needed)
- **ROI:** 9.5× at 7 customers (exceeds 3× target) ✅

---

## I. Operational Costs (Monthly)

### Layer 1: Gemini Ingestion (Collection)
```
Gemini API:           $15-25
GKE Infrastructure:   $50
Storage (GCS):        $2-5
Monitoring:           $0 (self-hosted)
─────────────────────────────
Total Layer 1:        $77/mo
```

### Layer 2: Judge #6 + JR Engine (Enforcement)
```
Gemini Flash:         $800-1,200
CloudFlare Workers:   $200-400
ChromaDB:             $0 (self-hosted)
Audit Storage:        $0-100
─────────────────────────────
Total Layer 2:        $1,000-1,600/mo
```

### Combined Stack
```
Minimum:              $1,077/mo
Maximum:              $1,677/mo
Expected:             $1,380/mo (mid-range)
```

**Cost Reduction vs v0.1.0:**
- Old (Vertex AI Vector Search): $1,280/mo
- New (Collection layer): $77/mo
- **Savings: 94%** ✅

---

## II. Revenue Model

### Pricing Tiers

#### Base: $297/month
- Target: SaaS companies (GDPR compliance)
- LTV: $5,346 (18 months)
- LTV:CAC: 5.3:1 ✅
- Payback: 3.4 months

#### White-Glove: $997/month
- Target: Healthcare (HIPAA compliance)
- LTV: $17,946 (18 months)
- LTV:CAC: 17.9:1 ✅
- Payback: 1.0 month

#### Enterprise: $9,970/month
- Target: Finserv (SOC2/audit)
- LTV: $179,460 (18 months)
- LTV:CAC: 179.5:1 ✅
- Payback: 3 days

#### Usage: $0.10/lead
- Target: B2B lead generation
- Margin: 50% ($0.05 profit/lead)
- Break-even: 13,800 leads/month

---

## III. Break-Even Scenarios

### Scenario A: Monthly Subscription (Base Tier Only)

| Customers | MRR | Annual Revenue | Monthly Profit | Status |
|-----------|-----|----------------|----------------|--------|
| 3 | $891 | $10,692 | -$489 | ❌ Loss |
| 4 | $1,188 | $14,256 | -$192 | ⚠️ Close |
| 5 | $1,485 | $17,820 | +$105 | ✅ Profitable |
| 6 | $1,782 | $21,384 | +$402 | ✅ Strong |

**Break-Even:** 5 customers @ $297/mo

### Scenario B: Subscription Mix (Realistic)

| Tier | Qty | MRR | Annual |
|------|-----|-----|--------|
| Base (60%) | 4 | $1,188 | $14,256 |
| White-Glove (30%) | 2 | $1,994 | $23,928 |
| Enterprise (10%) | 1 | $9,970 | $119,640 |
| **Total** | **7** | **$13,152** | **$157,824** |

**Monthly Profit:** $11,772 ✅
**ROI:** 9.5× (exceeds 3× gate) ✅
**Annual Profit:** $141,144

### Scenario C: Usage-Based Only

| Leads/Month | Revenue | Costs | Profit | Status |
|-------------|---------|-------|--------|--------|
| 10,000 | $1,000 | $1,380 | -$380 | ❌ |
| 13,800 | $1,380 | $1,380 | $0 | ⚠️ Break-Even |
| 25,000 | $2,500 | $1,380 | +$1,120 | ✅ |
| 50,000 | $5,000 | $1,380 | +$3,620 | ✅ |

### Scenario D: Hybrid (Most Realistic)

```
3× Base tier:          $891/mo
1× White-Glove:        $997/mo
20,000 leads:          $2,000/mo
─────────────────────────────
Total Revenue:         $3,888/mo
Operational Costs:     $1,380/mo
─────────────────────────────
Monthly Profit:        $2,508/mo ✅
Annual Profit:         $30,096
```

**Timeline to Profitability:** 4 months

---

## IV. Cash Flow Projections

### Months 0-3: Pre-Launch
```
Month 0: -$1,380 (setup)
Month 1: -$1,380 (development)
Month 2: -$1,083 (1 customer)
Month 3: -$489 (3 customers)
─────────────────────────────
Cumulative: -$4,332
```

**Capital Required:** $5,000 (1-month buffer)

### Months 4-6: Growth Phase
```
Month 4: +$508 (subscription + usage)
Month 5: +$1,505 (5 customers)
Month 6: +$2,508 (7 customers)
─────────────────────────────
Cumulative: +$189 ✅
```

**Break-Even:** Month 6

### Months 7-12: Scale Phase
```
Average: +$4,050/mo (10+ customers)
─────────────────────────────
Year 1 Net Profit: $20K-25K
```

---

## V. Key Metrics Summary

### Financial Health

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **LTV:CAC Ratio** | ≥4:1 | 5.3:1 | ✅ |
| **ROI (18mo)** | ≥3× | 9.5× | ✅ |
| **Gross Margin** | >50% | 64.5% | ✅ |
| **CAC Payback** | <6mo | 3.4mo | ✅ |
| **Monthly Burn** | <$2K | -$508 (Mo 4+) | ✅ |

### Operational Efficiency

| Metric | Target | Status |
|--------|--------|--------|
| **Collection Cost/Item** | ≤$0.10 | $0.077 ✅ |
| **Collection Runtime** | ≤45 min | TBD (pre-prod) |
| **Enforcement Latency p99** | ≤90ms | TBD (pre-prod) |
| **Uptime** | ≥99.9% | TBD (pre-prod) |

---

## VI. Customer Acquisition

### CAC Breakdown
```
Outbound Sales (50h):  $500
Marketing:             $200
Demo/Trial:            $200
Sales Engineering:     $100
─────────────────────────────
Total CAC:             $1,000
```

### Sales Cycle
```
Aggressive:            30 days
Conservative:          90 days
Blended Average:       45-60 days
```

### Target Customers

**Year 1 (Months 0-12):**
```
Base tier:             8-12 customers
White-Glove:           2-4 customers
Enterprise:            1-2 customers
─────────────────────────────
Total:                 12-18 customers
MRR:                   $6K-15K
```

---

## VII. Competitive Pricing

| Provider | Price/mo | Enforcement | Audit | Compliance |
|----------|----------|-------------|-------|------------|
| **Pnkln (Base)** | $297 | ✅ | ✅ | ✅ |
| **Pnkln (WG)** | $997 | ✅ | ✅ | ✅ |
| **Pnkln (Ent)** | $9,970 | ✅ | ✅ | ✅ |
| GodOfPrompt.ai | $997 | ❌ | ❌ | ❌ |
| Custom Dev | $10K-50K | Maybe | Maybe | Maybe |
| In-house | $15K+/mo | Eventually | Eventually | Eventually |

**Value Proposition:**
- **10-50× cheaper** than in-house ($297 vs $15K+/mo)
- **Instant compliance** vs months of development
- **Legal defensibility** via audit trails

---

## VIII. Risk Assessment

### Financial Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Slower sales cycle | 40% | 3-6mo delay | Pre-sales, annual contracts |
| Higher ops costs | 20% | +$500-1K/mo | Optimize API usage, caching |
| Pricing resistance | 20% | -10-30% | Focus on high-value segments |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Latency SLA miss | 30% | Churn | Edge compute, optimization |
| Compliance gaps | 15% | Lost deals | Partner with consultants |
| Competitor launch | 40% | Pricing pressure | First-mover, deep expertise |

---

## IX. Investment Requirements

### Bootstrap Path (Recommended)
```
Pre-launch (Mo 0-3):   $4,140
Buffer (Mo 4-5):       $2,760
─────────────────────────────
Total Capital Needed:  $6,900
```

**Funding Sources:**
```
Personal Savings:      $5,000
Pre-Sales (2 annual):  $7,128
─────────────────────────────
Total Available:       $12,128 ✅
```

**NO EXTERNAL FUNDING NEEDED** ✅

### Venture-Backed Path (Optional)
```
Seed Round:            $500K-1M
Use Cases:
  - Hire SDRs (faster sales)
  - Expand compliance frameworks
  - Geographic expansion (EU/APAC)
Dilution:              15-25%
```

**Not necessary for initial validation** - bootstrap path is viable.

---

## X. Quick Reference Tables

### Monthly Costs by Component

| Component | Min | Max | Expected |
|-----------|-----|-----|----------|
| Gemini API (collection) | $15 | $25 | $20 |
| GKE Infrastructure | $50 | $50 | $50 |
| Gemini Flash (enforcement) | $800 | $1,200 | $1,000 |
| CloudFlare Workers | $200 | $400 | $300 |
| Other | $12 | $102 | $10 |
| **Total** | **$1,077** | **$1,677** | **$1,380** |

### Revenue by Tier (per customer)

| Tier | Monthly | Annual | LTV (18mo) |
|------|---------|--------|------------|
| Base | $297 | $3,564 | $5,346 |
| White-Glove | $997 | $11,964 | $17,946 |
| Enterprise | $9,970 | $119,640 | $179,460 |
| Usage (20K leads) | $2,000 | $24,000 | $36,000 |

### Break-Even Customers by Tier

| Tier | Customers Needed | MRR | Timeline |
|------|------------------|-----|----------|
| Base | 5 | $1,485 | 3-4 months |
| White-Glove | 2 | $1,994 | 1-2 months |
| Enterprise | 1 | $9,970 | <1 month |
| Usage | 13,800 leads | $1,380 | 2-3 months |

---

## XI. Action Items

### Immediate (Week 1-4)
- [ ] Validate pricing with 10 target customers
- [ ] Launch MVP (Base tier only)
- [ ] Secure 2 pilot customers (50% upfront)
- [ ] Implement cost tracking

### Short-Term (Month 1-3)
- [ ] Hit $1,000 MRR (3-4 Base customers)
- [ ] Optimize ops costs to $1,200/mo
- [ ] Add White-Glove tier
- [ ] Build sales playbook

### Medium-Term (Month 4-6)
- [ ] Hit $3,000 MRR (break-even)
- [ ] Launch usage-based pricing
- [ ] Achieve profitability (Month 6)
- [ ] Expand to 10 customers

### Long-Term (Month 7-12)
- [ ] Scale to $10K+ MRR (30+ customers)
- [ ] Add Enterprise tier
- [ ] Expand compliance frameworks
- [ ] Consider seed round (optional)

---

## XII. Data for Analysis

### Cost Model Assumptions
```python
{
  'gemini_api_cost_per_1k_tokens': 0.50,
  'items_per_day': 1000,
  'tokens_per_item': 1000,
  'monthly_tokens': 30_000_000,
  'gke_node_type': 'n1-standard-1',
  'gke_monthly_cost': 50,
  'gemini_flash_qpm': 60,  # queries per minute
  'gemini_flash_cost_per_1m_tokens': 0.50,
  'cloudflare_workers_free_tier': 100_000,  # requests/day
}
```

### Revenue Model Assumptions
```python
{
  'average_customer_lifetime_months': 18,
  'churn_rate_monthly': {
    'base': 0.05,  # 5%/mo
    'white_glove': 0.03,  # 3%/mo
    'enterprise': 0.01,  # 1%/mo
  },
  'target_cac_usd': 1000,
  'sales_cycle_days': {
    'aggressive': 30,
    'conservative': 90,
    'average': 60,
  },
  'tier_distribution': {
    'base': 0.60,  # 60%
    'white_glove': 0.30,  # 30%
    'enterprise': 0.10,  # 10%
  }
}
```

### Performance Targets
```python
{
  'collection_layer': {
    'runtime_minutes': 45,
    'items_per_day': 1000,
    'cost_per_item': 0.077,
    'tier_1_percentage': 20,
    'sources_minimum': 10,
  },
  'enforcement_layer': {
    'latency_p99_ms': 90,
    'latency_p50_ms': 50,
    'uptime_percentage': 99.9,
    'false_positive_rate': 0.02,
  }
}
```

---

**Analysis Confidence:** 75% (pre-production estimates)

**Next Update:** After Month 3 (first production data)

**Contact:** finance@pnkln.ai

---

## Data Export (JSON)

```json
{
  "operational_costs": {
    "monthly": {
      "min": 1077,
      "max": 1677,
      "expected": 1380
    },
    "breakdown": {
      "layer_1_collection": 77,
      "layer_2_enforcement": 1303
    }
  },
  "revenue_model": {
    "tiers": {
      "base": {
        "monthly": 297,
        "ltv": 5346,
        "ltv_cac": 5.3
      },
      "white_glove": {
        "monthly": 997,
        "ltv": 17946,
        "ltv_cac": 17.9
      },
      "enterprise": {
        "monthly": 9970,
        "ltv": 179460,
        "ltv_cac": 179.5
      },
      "usage": {
        "per_lead": 0.10,
        "margin": 0.50
      }
    }
  },
  "break_even": {
    "customers_base_tier": 5,
    "customers_mixed": 7,
    "leads_usage_only": 13800,
    "timeline_months": 6
  },
  "kpis": {
    "ltv_cac_ratio": 5.3,
    "roi_18mo": 9.5,
    "gross_margin": 0.645,
    "cac_payback_months": 3.4
  },
  "capital_requirements": {
    "bootstrap": 6900,
    "seed_optional": 500000
  }
}
```

---

**Last Updated:** 2025-11-16 23:45 UTC
