# GPU Infrastructure: TCO & ROI Analysis

> **Detailed Financial Model for Cloud vs. On-Premise GPU Compute**
> **Date**: 2025-11-17
> **Version**: 1.0

---

## Executive Summary

This document provides transparent, digit-by-digit TCO (Total Cost of Ownership) and ROI calculations for GPU infrastructure decisions. All assumptions are clearly stated and adjustable.

### Key Findings


- **At $10/hr cloud pricing**: Own hardware pays off at ≥ 24.65% utilization

- **At $3/hr cloud pricing**: Own hardware pays off at ≥ 82.1% utilization

- **At $7/hr cloud pricing** (realistic blended rate): Own hardware pays off at ≥ 35.2% utilization

- **Payback period** (100% util, $10/hr cloud): ~9.2 months

- **Recommended approach**: Cloud-first until proven utilization exceeds thresholds

---

## Table of Contents


1. [Assumptions](#assumptions)

2. [On-Premise TCO Calculation](#on-premise-tco-calculation)

3. [Cloud Cost Calculation](#cloud-cost-calculation)

4. [Break-Even Analysis](#break-even-analysis)

5. [ROI Scenarios](#roi-scenarios)

6. [Sensitivity Analysis](#sensitivity-analysis)

7. [ETF-Style Investment Views](#etf-style-investment-views)

8. [Financial Models](#financial-models)

---

## Assumptions

### Target Configuration

**GPU Cluster Specification**:

- **Total GPUs**: 64× H100-class (80GB each)

- **Physical Layout**: 8× DGX H100 nodes (8 GPUs per node)

- **Interconnect**: NVLink 4.0 + 400 Gbps InfiniBand

- **System RAM**: 2TB per node (16TB total)

- **Storage**: NVMe scratch + object storage tier

### Cloud Pricing Scenarios

| Scenario | Price per GPU-Hour | Provider Type | Notes |
|----------|-------------------|---------------|-------|
| **High** | $10.00 | Hyperscaler on-demand | AWS, GCP, Azure p5.48xlarge equivalent |
| **Medium** | $7.00 | Blended (reserved + spot) | Realistic mixed workload pricing |
| **Low** | $3.00 | Specialist committed | CoreWeave, Lambda with 1-year commit |

### On-Premise Cost Components

#### Capital Expenditure (CapEx)

| Component | Cost | Notes |
|-----------|------|-------|
| 8× DGX H100 8-GPU nodes | $2,400,000 | ~$300K per node |
| High-speed fabric (IB switches) | $480,000 | 400 Gbps per node |
| NVMe storage tier | $320,000 | Fast scratch space |
| Object storage tier | $160,000 | Checkpoint/model storage |
| Facility upgrades (power, cooling) | $320,000 | Redundant power, HVAC |
| Installation & integration | $120,000 | Professional services |
| **Total CapEx** | **$3,200,000** | **One-time investment** |

#### Operational Expenditure (OpEx)

**Depreciation**:

- **Period**: 36 months (straight-line)

- **Monthly**: $3,200,000 ÷ 36 = **$88,888.89**

**Power & Cooling**:

- **Power per DGX**: ~10 kW

- **Total power**: 80 kW continuous

- **PUE (Power Usage Effectiveness)**: 1.4 (40% cooling overhead)

- **Effective draw**: 80 kW × 1.4 = 112 kW

- **Electricity rate**: $0.12/kWh (blended commercial)

- **Monthly hours**: 720 (30 days × 24 hours)

*Calculation*:

```

Power cost = 80 kW × 720 h × $0.12 = 5,760 kWh × $0.12 = $6,912.00
Cooling cost = $6,912.00 × 0.40 = $2,764.80
Total energy = $6,912.00 + $2,764.80 = $9,676.80

```

**Facilities & Support**:

- **Network connectivity**: $3,000/month (10 Gbps enterprise)

- **Facilities management**: $5,000/month (monitoring, physical security)

- **Support & maintenance**: $7,000/month (NVIDIA warranties, break-fix)

- **Total**: $15,000/month

**Optional Software Licensing**:

- **NVIDIA AI Enterprise**: ~$10,000-15,000/month (not included in baseline)

- **MLOps platforms**: Variable (Kubeflow free, others paid)

---

## On-Premise TCO Calculation

### Monthly TCO (Baseline)

```

Component                     Amount
────────────────────────────────────
Depreciation                  $88,888.89
Power (80 kW × 720h × $0.12)   $6,912.00
Cooling (40% of power)         $2,764.80
Facilities & support          $15,000.00
────────────────────────────────────
Monthly TCO (baseline)       $113,565.69

```

### Annual TCO

```

Monthly TCO × 12 = $113,565.69 × 12 = $1,362,788.28

```

### Per-GPU Monthly Cost

```

$113,565.69 ÷ 64 GPUs = $1,774.46 per GPU per month

```

### Per-GPU-Hour Cost (at 100% utilization)

```

$1,774.46 ÷ 720 hours = $2.46/GPU-hour

```

**Key Insight**: At full utilization, on-prem costs $2.46/GPU-hour. Any cloud price above this loses money at high utilization.

---

## Cloud Cost Calculation

### Formula

```

Monthly Cloud Cost = Number of GPUs × Price per GPU-Hour × Hours per Month × Utilization
Monthly Cloud Cost = 64 × P × 720 × U

```

Where:

- `P` = Price per GPU-hour

- `U` = Utilization percentage (0.0 to 1.0)

### Pricing Scenarios

#### High Cloud Pricing ($10/hr)

```

Base monthly cost (100% util) = 64 × $10 × 720 = $460,800
Cost at utilization U = $460,800 × U

```

| Utilization | Monthly Cost |
|-------------|--------------|
| 100% | $460,800 |
| 80% | $368,640 |
| 60% | $276,480 |
| 40% | $184,320 |
| 25% | $115,200 |
| 20% | $92,160 |

#### Medium Cloud Pricing ($7/hr)

```

Base monthly cost (100% util) = 64 × $7 × 720 = $322,560
Cost at utilization U = $322,560 × U

```

| Utilization | Monthly Cost |
|-------------|--------------|
| 100% | $322,560 |
| 80% | $258,048 |
| 60% | $193,536 |
| 40% | $129,024 |
| 35% | $112,896 |
| 20% | $64,512 |

#### Low Cloud Pricing ($3/hr)

```

Base monthly cost (100% util) = 64 × $3 × 720 = $138,240
Cost at utilization U = $138,240 × U

```

| Utilization | Monthly Cost |
|-------------|--------------|
| 100% | $138,240 |
| 82% | $113,357 |
| 60% | $82,944 |
| 40% | $55,296 |
| 20% | $27,648 |

---

## Break-Even Analysis

### Break-Even Formula

At break-even, cloud cost equals on-prem TCO:

```

Cloud Cost = On-Prem TCO
64 × P × 720 × U = $113,565.69
U = $113,565.69 ÷ (64 × P × 720)
U = $113,565.69 ÷ (46,080 × P)

```

### Break-Even Utilization by Price

| Cloud Price (P) | Break-Even Utilization (U) | Interpretation |
|-----------------|---------------------------|----------------|
| $10/hr | **24.65%** | Own if util > ~25% |
| $9/hr | 27.39% | Own if util > ~27% |
| $8/hr | 30.81% | Own if util > ~31% |
| **$7/hr** | **35.21%** | **Sweet spot trigger** |
| $6/hr | 41.08% | Own if util > ~41% |
| $5/hr | 49.30% | Own if util > ~49% |
| $4/hr | 61.62% | Own if util > ~62% |
| $3/hr | **82.16%** | Own if util > ~82% |

### Visual Break-Even Chart

```

Utilization Threshold for Owning Hardware
(Below line: Cloud wins | Above line: Own wins)

100% ┼───────────────────────────────────────
     │                               ╱
 90% ┤                           ╱
     │                       ╱  $3/hr
 80% ┤                   ╱───────────(82%)
     │               ╱
 70% ┤           ╱
     │       ╱
 60% ┤   ╱
     │╱          $5/hr (49%)
 50% ┤───────────────────────
     │       ╱
 40% ┤   ╱           $7/hr (35%)
     │╱──────────────────────
 30% ┤
     │╱      $10/hr (25%)
 20% ┤───────────────
     │
 10% ┤
     │
  0% ┼───────────────────────────────────────
     $3      $5      $7      $9      $11
           Cloud Price per GPU-Hour

```

### Decision Recommendations

#### Scenario 1: Hyperscaler On-Demand ($9-11/hr)

**Break-even**: ~25-27% utilization
**Recommendation**:

- ✅ Own if you can sustain ≥30% utilization

- ✅ Cloud only for burst/experimental workloads

- 💰 High ROI for owned hardware

#### Scenario 2: Blended/Reserved ($6-8/hr)

**Break-even**: ~30-40% utilization
**Recommendation**:

- ✅ Own if you can sustain ≥40% utilization

- ⚠️ Monitor carefully; close to break-even

- 📊 Use 90-day rolling average to decide

#### Scenario 3: Specialist/Committed ($2-4/hr)

**Break-even**: ~60-80% utilization
**Recommendation**:

- ❌ Stay cloud unless utilization is consistently ≥80%

- ✅ Excellent for variable workloads

- 💡 Best option for Phase 1

---

## ROI Scenarios

### Scenario 1: High Cloud Pricing ($10/hr, 100% Utilization)

**Annual cloud cost**:

```

$460,800/month × 12 = $5,529,600

```

**Annual on-prem TCO**:

```

$113,565.69/month × 12 = $1,362,788.28

```

**Annual net benefit**:

```

$5,529,600 - $1,362,788.28 = $4,166,811.72

```

**ROI**:

```

($4,166,811.72 ÷ $3,200,000) × 100 = 130.2% per year

```

**Payback period**:

```

$3,200,000 ÷ $347,234/month = 9.2 months

```

### Scenario 2: High Cloud Pricing ($10/hr, 40% Utilization)

**Annual cloud cost**:

```

$184,320/month × 12 = $2,211,840

```

**Annual on-prem TCO**: $1,362,788.28 (unchanged)

**Annual net benefit**:

```

$2,211,840 - $1,362,788.28 = $849,051.72

```

**ROI**:

```

($849,051.72 ÷ $3,200,000) × 100 = 26.5% per year

```

**Payback period**:

```

$3,200,000 ÷ $70,754/month = 45.2 months

```

### Scenario 3: Low Cloud Pricing ($3/hr, 100% Utilization)

**Annual cloud cost**:

```

$138,240/month × 12 = $1,658,880

```

**Annual on-prem TCO**: $1,362,788.28

**Annual net benefit**:

```

$1,658,880 - $1,362,788.28 = $296,091.72

```

**ROI**:

```

($296,091.72 ÷ $3,200,000) × 100 = 9.25% per year

```

**Payback period**:

```

$3,200,000 ÷ $24,674/month = 129.7 months (10.8 years)

```

**Conclusion**: Not attractive within 3-year depreciation window.

### Scenario 4: Medium Cloud Pricing ($7/hr, 60% Utilization)

**Annual cloud cost**:

```

$193,536/month × 12 = $2,322,432

```

**Annual on-prem TCO**: $1,362,788.28

**Annual net benefit**:

```

$2,322,432 - $1,362,788.28 = $959,643.72

```

**ROI**:

```

($959,643.72 ÷ $3,200,000) × 100 = 30.0% per year

```

**Payback period**:

```

$3,200,000 ÷ $79,970/month = 40.0 months

```

---

## Sensitivity Analysis

### Full Sensitivity Matrix

Monthly net benefit (Cloud cost - On-prem TCO):

| Utilization | $10/hr | $9/hr | $8/hr | $7/hr | $6/hr | $5/hr | $4/hr | $3/hr |
|-------------|--------|-------|-------|-------|-------|-------|-------|-------|
| **100%** | +$347K | +$298K | +$250K | +$209K | +$161K | +$112K | +$64K | +$25K |
| **80%** | +$255K | +$216K | +$176K | +$145K | +$105K | +$66K | +$27K | −$12K |
| **60%** | +$163K | +$133K | +$102K | +$80K | +$50K | +$21K | −$9K | −$31K |
| **40%** | +$71K | +$50K | +$28K | +$15K | −$6K | −$25K | −$46K | −$58K |
| **35%** | +$48K | +$31K | +$13K | **−$1K** | −$21K | −$36K | −$54K | −$64K |
| **25%** | **+$2K** | −$10K | −$21K | −$29K | −$40K | −$51K | −$65K | −$73K |
| **20%** | −$21K | −$30K | −$39K | −$45K | −$54K | −$62K | −$71K | −$79K |

**Legend**:

- **Positive (+)**: Cloud costs more → Owning wins

- **Negative (−)**: Cloud costs less → Cloud wins

- **Bold**: Break-even point

### Key Insights from Matrix


1. **At $10/hr**: Own hardware wins at any utilization ≥25%

2. **At $7/hr**: Break-even is exactly 35% utilization

3. **At $3/hr**: Cloud wins until you hit 82% utilization

4. **Sweet spot**: If blended cloud rate ≥$7/hr and util ≥40%, owning is clearly better

### Impact of Power Cost Variations

| Electricity Rate | Monthly Power+Cooling | Impact on TCO | New Break-Even ($7/hr) |
|------------------|----------------------|---------------|------------------------|
| $0.08/kWh | $6,451.20 | −$3,226 | 32.4% |
| $0.10/kWh | $8,064.00 | −$1,613 | 33.8% |
| **$0.12/kWh** | **$9,676.80** | **Baseline** | **35.2%** |
| $0.15/kWh | $12,096.00 | +$2,419 | 37.7% |
| $0.20/kWh | $16,128.00 | +$6,451 | 42.2% |

**Conclusion**: Power costs significantly impact break-even in high-electricity regions.

---

## ETF-Style Investment Views

### Cloud Compute Access ETF (C-ETF)

**Objective**: Diversified GPU provider basket to minimize cost and maximize availability.

#### Portfolio Composition

| Ticker | Provider Type | Weight | Target $/GPU-hr | Volatility | Rationale |
|--------|---------------|--------|-----------------|------------|-----------|
| **HYP-A** | Hyperscaler A (GCP) | 30% | $9.00 | Low | Enterprise SLAs, compliance |
| **SPEC-1** | Specialist 1 (CoreWeave) | 25% | $3.50 | Medium | Low cost, committed |
| **HYP-B** | Hyperscaler B (AWS) | 20% | $10.00 | Low | Regional coverage |
| **SPEC-2** | Specialist 2 (Lambda) | 15% | $4.00 | Medium | Burst capacity |
| **HYP-C** | Hyperscaler C (Azure) | 10% | $9.50 | Low | Edge PoPs, low latency |

#### Blended Metrics

**Blended $/GPU-hr**:

```

(0.30 × $9.00) + (0.25 × $3.50) + (0.20 × $10.00) + (0.15 × $4.00) + (0.10 × $9.50)
= $2.70 + $0.875 + $2.00 + $0.60 + $0.95
= $7.125/GPU-hr

```

**Expected annual cost** (60% utilization):

```

64 GPUs × $7.125/hr × 720 h/month × 0.60 × 12 months
= $1,971,648 per year

```

**Break-even utilization**: 35.5% (very close to trigger point)

#### Risk Profile

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Preemption (SPEC providers) | Medium | Low | Checkpointing every 15 min |
| Capacity constraints | Low | Medium | Multi-provider redundancy |
| Price increases | Medium | Medium | 1-year commitments where possible |
| Egress fees | Low | Low | Regional data locality |

#### Rebalancing Strategy


- **Monthly**: Review actual costs vs. targets; adjust weights

- **Quarterly**: Renegotiate commitments based on utilization

- **Annually**: Major review; consider reserved instances or on-prem

---

### On-Premise Infrastructure ETF (O-ETF)

**Objective**: Diversified component basket to spread TCO risk.

#### Portfolio Composition

| Ticker | Component | Weight | Investment | Expected Life | Annual Amortization |
|--------|-----------|--------|------------|---------------|---------------------|
| **NVDA-SYS** | NVIDIA DGX nodes | 55% | $1,760,000 | 3 years | $586,667 |
| **NET-FAB** | InfiniBand fabric | 15% | $480,000 | 5 years | $96,000 |
| **STOR-NVM** | NVMe + object storage | 15% | $480,000 | 5 years | $96,000 |
| **FAC-PWR** | Power & cooling | 10% | $320,000 | 10 years | $32,000 |
| **OPS-TOOL** | Ops toolchain | 5% | $160,000 | 3 years | $53,333 |
| **Total** | | **100%** | **$3,200,000** | | **$864,000/yr** |

#### Performance Metrics

**Theoretical peak**: 64× H100 @ 989 TFLOPS (FP16) each = 63,296 TFLOPS

**Effective throughput** (75% efficiency): 47,472 TFLOPS

**Cost per TFLOPS-hour** (100% util):

```

$113,566/month ÷ 720 hours ÷ 47,472 TFLOPS = $0.00332 per TFLOPS-hour

```

#### Risk Profile

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Underutilization | Medium | High | Cloud-first proof of demand |
| Component failure | Low | Medium | Redundancy, hot spares |
| Technology obsolescence | Low | Medium | 36-month depreciation |
| Power outage | Low | High | UPS, redundant feeds |
| Staffing gaps | Medium | Medium | Training, vendor support |

#### Dividend Yield (Utilization-Based Returns)

| Utilization | Effective $/GPU-hr | "Yield" vs. $10/hr Cloud |
|-------------|-------------------|--------------------------|
| 100% | $2.46 | 75.4% savings |
| 80% | $3.08 | 69.2% savings |
| 60% | $4.10 | 59.0% savings |
| 40% | $6.15 | 38.5% savings |
| 25% | $9.84 | 1.6% savings |

**Sweet spot**: 60-100% utilization yields "dividends" of 59-75% savings vs. cloud.

---

## Financial Models

### Net Present Value (NPV) Analysis

**Assumptions**:

- Discount rate: 10% (WACC)

- Time horizon: 3 years (depreciation period)

- Utilization: 60% average

- Cloud pricing: $7/hr blended

#### Cloud Option (Status Quo)

```

Year 0: $0 (no CapEx)
Year 1: −$1,971,648 (OpEx)
Year 2: −$1,971,648
Year 3: −$1,971,648

NPV = −$1,971,648/(1.10) − $1,971,648/(1.10)² − $1,971,648/(1.10)³
    = −$1,792,407.27 − $1,629,461.15 − $1,481,328.32
    = −$4,903,196.74

```

#### On-Prem Option

```

Year 0: −$3,200,000 (CapEx)
Year 1: −$296,816 (OpEx only: power + facilities)
Year 2: −$296,816
Year 3: −$296,816

NPV = −$3,200,000 − $296,816/(1.10) − $296,816/(1.10)² − $296,816/(1.10)³
    = −$3,200,000 − $269,832.73 − $245,302.48 − $223,002.25
    = −$3,938,137.46

```

**NPV Advantage (On-Prem)**:

```

−$3,938,137.46 − (−$4,903,196.74) = +$965,059.28

```

**Conclusion**: At 60% utilization and $7/hr cloud, on-prem has NPV advantage of ~$965K over 3 years.

### Internal Rate of Return (IRR)

For on-prem investment, IRR is the discount rate where NPV = 0.

**Cash flows** (vs. cloud baseline):

```

Year 0: −$3,200,000 (initial investment)
Year 1: +$1,674,832 (cloud savings minus on-prem OpEx)
Year 2: +$1,674,832
Year 3: +$1,674,832

IRR calculation:
0 = −$3,200,000 + $1,674,832/(1+IRR) + $1,674,832/(1+IRR)² + $1,674,832/(1+IRR)³

```

Solving: **IRR ≈ 31.2%**

**Interpretation**: On-prem investment yields 31.2% annualized return vs. cloud baseline at these assumptions.

---

## Conclusion & Recommendations

### Summary Table

| Metric | Cloud ($7/hr, 60% util) | On-Prem (60% util) | Advantage |
|--------|-------------------------|-------------------|-----------|
| **Monthly cost** | $193,536 | $113,566 | On-prem: $79,970/mo |
| **Annual cost** | $2,322,432 | $1,362,788 | On-prem: $959,644/yr |
| **3-year TCO** | $6,967,296 | $4,088,365 | On-prem: $2,878,931 |
| **3-year NPV** | −$4,903,197 | −$3,938,137 | On-prem: +$965,060 |
| **IRR** | N/A (baseline) | 31.2% | On-prem wins |
| **$/GPU-hr** | $7.00 | $4.10 | On-prem: 41% cheaper |

### Decision Framework

```

IF (90-day avg utilization ≥ 35%) AND (blended cloud rate ≥ $7/hr)
THEN initiate DGX procurement
ELSE continue cloud-first strategy

```

### Phase-Based Recommendations


1. **Phase 1 (Months 0-3)**: Cloud multi-provider, measure utilization

2. **Phase 2 (Months 3-6)**: If triggers hit, begin DGX procurement (6-month lead time)

3. **Phase 3 (Months 9-12)**: Deploy on-prem, migrate workloads, maintain cloud for burst

### Risk-Adjusted Recommendation

Given uncertainties in utilization and workload growth:


1. **Start cloud**: Prove demand, optimize costs

2. **Set trigger**: Auto-alert when 90-day util ≥35% at ≥$7/hr

3. **Pilot hybrid**: 1× DGX to build ops muscle

4. **Scale to own**: When math clearly favors it

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-17
**Next Review**: Upon hitting 30% sustained utilization
