# Judge #6 Validation System

**Real-Time Compliance & Intelligence Validation Layer**

---

## Overview

**Judge #6** is AiYou's downstream validation and enforcement system within the PNKLN Core Stack™, operating as a **hybrid Gemini+PyTorch real-time validator** that applies ATP 5-19 compliance rules, JR (Joint Requirements) validation, and quality gates to intelligence items before they reach ShadowTag attestation.

**Key Function:** Transform classified intelligence (from Gemini Ingestion Layer) into compliance-validated, actionable data ready for cryptographic attestation.

**Position in Stack:** Sits between Knowledge Graph (entity extraction) and ShadowTag Notarization (attestation)

---

## Architecture

### System Design

```

┌──────────────────────────────────────────────────────────┐
│                   Judge #6 Validation                     │
│                                                           │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │  ATP 5-19      │  │   JR Rules     │  │  Quality   │ │
│  │  Compliance    │  │   Validator    │  │   Gates    │ │
│  │                │  │                │  │            │ │
│  │ • DO-178C      │  │ • NIST RMF     │  │ • FP/FN    │ │
│  │ • ISO 26262    │  │ • ITAR         │  │ • Coverage │ │
│  │ • FCC Rules    │  │ • EAR          │  │ • Latency  │ │
│  └────────────────┘  └────────────────┘  └────────────┘ │
│          │                   │                   │       │
│          └───────────────────┴───────────────────┘       │
│                              ▼                            │
│                   ┌────────────────────┐                 │
│                   │  Validation Result │                 │
│                   │  (Pass/Fail/Flag)  │                 │
│                   └────────────────────┘                 │
└──────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  ShadowTag Attestation (L0-L4)│
              │  • Pass → L4 Attestation      │
              │  • Fail → Reject              │
              │  • Flag → L2 Attestation      │
              └───────────────────────────────┘

```

### Hybrid AI Architecture

**Gemini 2.0 Pro** (Natural Language Understanding):

- Parse complex regulatory text (DO-178C, NIST RMF)

- Interpret JR requirements in context

- Generate human-readable validation reports

**PyTorch** (Fast Rule Matching):

- Binary classification for known patterns (ITAR keywords, export control lists)

- Low-latency decision trees for ATP 5-19 rules

- Batch scoring for coverage metrics

| Component | Technology | Latency Contribution | Accuracy Target |
|-----------|-----------|---------------------|-----------------|
| **Rule Engine** | PyTorch (ONNX Runtime) | 15-25ms (p99) | ≥98% coverage |
| **NLU Parser** | Gemini 2.0 Pro | 40-60ms (p99) | ≥95% intent classification |
| **Decision Logic** | Python 3.11 + FastAPI | 10-15ms (p99) | 100% deterministic |
| **Total p99 Latency** | — | **≤90ms** | — |

---

## Key Metrics & Performance Targets

### Operational Metrics (vs. Gemini Ingestion Layer)

| Metric | Judge #6 (Validation) | Gemini Ingestion Layer |
|--------|----------------------|------------------------|
| **Architecture** | Hybrid Gemini+PyTorch | GKE CronJob Multi-Container |
| **Execution Model** | Real-time on-demand | Nightly batch (23:00 UTC) |
| **Performance Target** | p99 ≤90ms | ≤45 min/night |
| **Primary Metrics** | Latency, Throughput, Block Rate | Items/day, Sources, Cost/Item |
| **Quality Gates** | FP/FN rates, Coverage (≥98%) | Relevance, Timeliness, Completeness |
| **Integration** | **Calls** services in 4 namespaces | **Called by** services in 4 namespaces |
| **Cost Model** | Per-API-call variable ($0.02-0.05/validation) | Fixed monthly (~$77) |
| **Unique Features** | ATP 5-19 compliance, JR validation | Ethical crawling, Tier classification |

### Performance Benchmarks (Production)

```yaml
latency_sla:
  p50: ≤35ms
  p95: ≤70ms
  p99: ≤90ms
  p99.9: ≤150ms

throughput:
  max_qps: 5000 requests/second
  sustained_qps: 2000 requests/second (24h average)
  burst_capacity: 10000 requests/second (5 min)

accuracy_metrics:
  false_positive_rate: ≤1.5%  # Items incorrectly blocked
  false_negative_rate: ≤0.5%  # Non-compliant items passed
  coverage: ≥98%               # % of ATP 5-19 rules evaluated

block_rate:
  tier_1_items: 2-5%    # High-value intelligence rarely blocked
  tier_2_items: 8-12%   # Medium-value items, stricter filters
  tier_3_items: 25-35%  # Low-value items, aggressive filtering
  overall: 12-18%       # Average across all tiers

```

---

## ATP 5-19 Compliance Rules

### What is ATP 5-19?

**Allied Tactical Publication (ATP) 5-19** is a NATO standardized framework for **joint intelligence preparation of the operational environment (JIPOE)**. Judge #6 implements a subset of ATP 5-19 rules relevant to intelligence validation, ensuring items meet military intelligence standards before attestation.

**Key ATP 5-19 Domains Implemented:**

| Domain | ATP 5-19 Requirement | Judge #6 Implementation | Pass Criteria |
|--------|---------------------|------------------------|---------------|
| **Source Reliability** | 6-level classification (A-F) | Rate sources A (Reliable) to F (Unreliable) | Source rating ≥C |
| **Information Credibility** | 6-level classification (1-6) | Rate content 1 (Confirmed) to 6 (Improbable) | Credibility ≤3 |
| **Timeliness** | Intelligence must be "current" | Timestamp validation, staleness check | <48h for tactical, <7d for strategic |
| **Completeness** | SALUTE report format (Size, Activity, Location, Unit, Time, Equipment) | Check for required fields in structured data | ≥80% field completeness |
| **Relevance** | Geographic/temporal/thematic fit | Keyword matching, geo-fence validation | Match ≥2 of 3 criteria |
| **Security Classification** | Proper marking (U, C, S, TS) | Auto-classify based on keywords, sources | Consistent marking |

### Example Validation Flow

```python

# Simplified ATP 5-19 validation logic

def validate_atp_5_19(item):
    results = {
        "source_reliability": rate_source(item.source),  # A-F scale
        "credibility": rate_credibility(item.content),   # 1-6 scale
        "timeliness": check_staleness(item.timestamp),
        "completeness": check_salute_format(item),
        "relevance": match_requirements(item.tags),
        "classification": auto_classify(item.content)
    }

    # Pass criteria
    if (results["source_reliability"] <= "C" and
        results["credibility"] <= 3 and
        results["timeliness"] == "current" and
        results["completeness"] >= 0.80 and
        results["relevance"] >= 2):
        return "PASS", results
    else:
        return "FAIL", results

```

**Example Results:**

```json
{
  "item_id": "ing_2025-11-15_a7b3c9",
  "validation_result": "PASS",
  "atp_5_19_scores": {
    "source_reliability": "B (Usually Reliable)",
    "credibility": 2 ("Probably True"),
    "timeliness": "current (<24h)",
    "completeness": 0.95,
    "relevance": 3,
    "classification": "UNCLASSIFIED//FOUO"
  },
  "pass_reason": "All ATP 5-19 criteria met",
  "next_action": "shadowtag_l4_attestation"
}

```

---

## JR (Joint Requirements) Validation

### Joint Requirements Framework

**JR Validation** ensures intelligence items comply with **U.S. military joint doctrine** and **export control regulations** (ITAR, EAR, NIST RMF). This is critical for Defense & ISR vertical customers.

**Core JR Checks:**

| Requirement | Description | Validation Method | Failure Impact |
|-------------|-------------|-------------------|----------------|
| **ITAR Compliance** | No controlled technical data to foreign nationals | Keyword matching (munitions list, spacecraft specs) | Block + flag for manual review |
| **EAR Dual-Use** | Commercial items with military applications | Entity List matching, ECCN classification | Flag for export license check |
| **NIST RMF Controls** | Cybersecurity controls for defense systems | Policy validation (800-53 controls) | Require L5 attestation upgrade |
| **Clearance Level** | Appropriate classification marking | Auto-classify + human override | Reclassify or reject |
| **OPSEC Violations** | Operational security leaks (troop movements, call signs) | NER (Named Entity Recognition) + blocklist | Block + alert OPSEC team |

### ITAR Keyword Detection Example

```yaml
itar_controlled_items:
  category_iv_spacecraft:

    - "satellite bus design"

    - "propulsion system schematics"

    - "radiation-hardened electronics"
  category_viii_aircraft:

    - "flight control source code"

    - "avionics architecture"

    - "ejection seat mechanism"
  category_xi_military_electronics:

    - "GPS receiver design (military)"

    - "encrypted communications protocols"

    - "radar cross-section data"

validation_action:
  if_match:

    - block_item: true

    - flag_for_review: "ITAR Compliance Team"

    - classification: "SECRET//NOFORN"

    - notify: "compliance@aiyou.ai"

```

**Real-World Scenario:**

An ingested item contains: *"Lockheed Martin's new F-35 avionics architecture integrates..."*


- **ITAR Check:** Keyword "avionics architecture" matches Category VIII

- **Result:** Item **BLOCKED**, flagged for manual review

- **Notification:** ITAR Compliance Team alerted within 5 minutes

- **Downstream:** Item **NOT** sent to ShadowTag attestation

---

## Quality Gates & Coverage Metrics

### Coverage Target: ≥98%

**Coverage** measures the percentage of ATP 5-19 rules evaluated against each intelligence item. Judge #6 targets ≥98% coverage, meaning nearly all regulatory checks are applied.

**Coverage Calculation:**

```

Coverage = (Rules Evaluated / Total ATP 5-19 Rules) × 100%

Example:

- Total ATP 5-19 rules implemented: 127

- Rules evaluated for item "ing_2025-11-15_a7b3c9": 125

- Coverage: 125/127 = 98.4% ✅

```

**Why Not 100%?**

- Some rules require external data (e.g., source reliability ratings from human analysts)

- Real-time constraints prevent deep NLP analysis on every item

- Certain rules apply only to specific domains (e.g., maritime-specific checks)

### False Positive/False Negative Rates

**Target:**

- **FP Rate:** ≤1.5% (items incorrectly blocked)

- **FN Rate:** ≤0.5% (non-compliant items passed)

**Measurement Method:**

1. **Weekly Human Review:** 500 random items (100 from each tier) manually validated

2. **Error Categorization:**

   - **FP:** Item blocked but should have passed (e.g., legitimate news article blocked for ITAR keyword false alarm)

   - **FN:** Item passed but should have been blocked (e.g., export-controlled data slipped through)

3. **Model Retraining:** FP/FN examples fed back into PyTorch classifier monthly

**Historical Performance (Q4 2025):**

| Month | FP Rate | FN Rate | Coverage | Notes |
|-------|---------|---------|----------|-------|
| **Oct 2025** | 2.1% | 0.8% | 96.3% | Initial launch, high error rates |
| **Nov 2025** | 1.7% | 0.6% | 97.8% | Tuned ITAR keywords, reduced false alarms |
| **Dec 2025** | 1.4% | 0.5% | 98.2% | ✅ Met SLA targets |

---

## Integration with 4 Kubernetes Namespaces

Judge #6 **calls** services across **4 Kubernetes namespaces** to complete validation:

### Namespace Architecture

```

┌──────────────────────────────────────────────────────────────┐
│                    AiYou GKE Cluster                         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ namespace: intelligence-ingestion                   │   │
│  │  - Gemini Ingestion Layer (upstream)                │   │
│  │  - Data normalization ETL                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ namespace: intelligence-validation  ← JUDGE #6 HERE │   │
│  │  - Judge #6 validation API                          │   │
│  │  - ATP 5-19 rule engine                             │   │
│  │  - JR compliance checker                            │   │
│  └─────────────────────────────────────────────────────┘   │
│          │                    │                     │       │
│          ▼                    ▼                     ▼       │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ namespace:   │  │ namespace:       │  │ namespace:   │ │
│  │ knowledge-   │  │ attestation      │  │ experience-  │ │
│  │ graph        │  │                  │  │ layer        │ │
│  │              │  │ - ShadowTag      │  │              │ │
│  │ - Entity     │  │ - Merkle tree    │  │ - AM Briefing│ │
│  │   extraction │  │ - TPM signing    │  │ - Dashboard  │ │
│  └──────────────┘  └──────────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────┘

```

### Service Call Dependencies

| Namespace | Service Called | Purpose | Latency Budget |
|-----------|----------------|---------|----------------|
| **intelligence-ingestion** | `ingestion-api.svc.cluster.local` | Fetch raw items for validation | 5-10ms |
| **knowledge-graph** | `entity-extractor.svc.cluster.local` | Extract entities (orgs, locations, dates) for relevance scoring | 20-30ms |
| **attestation** | `shadowtag-api.svc.cluster.local` | Check if item already attested (deduplication) | 5-10ms |
| **experience-layer** | `am-briefing-api.svc.cluster.local` | Notify AM Briefing of high-priority items | 5-10ms (async) |

**Total Cross-Namespace Latency:** 35-60ms (fits within p99 ≤90ms SLA)

---

## Cost Model: Per-API-Call Economics

### Variable Cost Structure

Unlike Gemini Ingestion Layer's **fixed monthly cost ($1,376)**, Judge #6 operates on a **per-validation cost model** to scale with usage.

```yaml
per_validation_costs:
  gemini_2_0_pro:
    input_tokens_avg: 1500 tokens (item content + ATP 5-19 rules)
    cost_per_1m_input: $1.25
    cost_per_validation: $0.001875

  pytorch_inference:
    gpu_instance: "NVIDIA T4 (shared)"
    cost_per_1000_inferences: $0.05
    cost_per_validation: $0.00005

  api_overhead:
    kubernetes_ingress: $0.0001/request
    cloud_nat_egress: $0.0002/request
    total: $0.0003/request

total_per_validation: $0.002225 (~$0.0022)

```

### Monthly Cost Projection

| Daily Validations | Monthly Validations | Total Monthly Cost | Cost per Item |
|-------------------|---------------------|--------------------|---------------|
| **10,000** | 300,000 | $667 | $0.0022 |
| **50,000** (current) | 1,500,000 | $3,338 | $0.0022 |
| **100,000** | 3,000,000 | $6,675 | $0.0022 |
| **500,000** (2× scale) | 15,000,000 | $33,375 | $0.0022 |

**Key Insight:** Cost scales **linearly** with volume (no infrastructure fixed costs to amortize), making Judge #6 more expensive at high scale compared to batch systems.

**Optimization Strategy:**

- **Cache Validation Results:** 30-day TTL for identical content hashes (reduces duplicate validations by ~15%)

- **Tier-Based Routing:** Skip ATP 5-19 checks for Tier 3 items (low-value), saving ~30% on API calls

- **Batch Mode (Optional):** For non-critical items, batch 100 validations per Gemini call (reduces cost by 40%)

---

## Real-Time vs. Batch Processing Trade-Offs

### Why Real-Time for Judge #6?

| Use Case | Latency Requirement | Example |
|----------|-----------------------|---------|
| **Live Defense Intel** | <100ms | Aircraft detects GPS spoofing → validate threat intelligence → alert pilot |
| **FAANG Content Moderation** | <200ms | Meta user uploads deepfake → validate provenance → block/flag |
| **Aviation NOTAM Updates** | <500ms | FAA issues airspace closure → validate compliance → update rebroadcast nodes |

**Batch Processing (Gemini Ingestion)** works for:

- Overnight data collection where 45-minute runtime is acceptable

- Historical analysis, trend detection, archival

**Real-Time Processing (Judge #6)** required for:

- Safety-critical decisions (aviation, defense, autonomous vehicles)

- User-facing interactions (content moderation, fraud detection)

- Compliance enforcement with SLA requirements

---

## Comparison Table: Acquisitive vs. Defensive Philosophy

| Dimension | Gemini Ingestion Layer (Acquisitive) | Judge #6 (Defensive) |
|-----------|-------------------------------------|----------------------|
| **Goal** | Maximize **recall** (catch everything) | Maximize **precision** (block bad items) |
| **Error Tolerance** | High (15-25% misclassification OK pre-prod) | Low (<2% FP/FN) |
| **Speed** | Slow (45 min batch) | Fast (<90ms real-time) |
| **Cost** | Fixed ($1.4K/month) | Variable ($0.0022/item) |
| **Integration** | Upstream (called by downstream) | Midstream (calls services before/after) |
| **Metrics** | Volume, diversity, cost/item | Latency, accuracy, block rate |

**Analogy:**

- **Ingestion Layer = Fishing Trawler:** Cast a wide net, accept bycatch, sort later

- **Judge #6 = Quality Inspector:** Examine each fish, reject defects, pass only premium

---

## Monitoring & Observability

### Grafana Dashboard Metrics

```yaml
key_metrics:

  - name: "Validation Latency (p50, p95, p99)"
    alert_threshold: "p99 > 100ms for 5 min"


  - name: "Throughput (QPS)"
    alert_threshold: "QPS < 500 (under capacity) OR QPS > 5000 (overload)"


  - name: "Block Rate (%)"
    alert_threshold: "Block rate < 5% (under-filtering) OR > 30% (over-blocking)"


  - name: "False Positive Rate (%)"
    alert_threshold: "FP > 2% for 24h rolling window"


  - name: "ATP 5-19 Coverage (%)"
    alert_threshold: "Coverage < 98% for 1 hour"


  - name: "Gemini API Errors"
    alert_threshold: "Error rate > 1% for 15 min"

```

**Grafana URL:** https://grafana.aiyou.ai/d/judge-six-validation

### Incident Response Runbook

| Alert | Severity | Response Time | Mitigation |
|-------|----------|---------------|------------|
| **p99 Latency > 150ms** | P2 (Medium) | 30 min | Scale up PyTorch inference nodes |
| **FP Rate > 3%** | P1 (High) | 15 min | Roll back rule changes, notify SRE |
| **Gemini API Quota Exceeded** | P0 (Critical) | 5 min | Failover to BERT fallback model |
| **ITAR Violation Detected** | P0 (Critical) | Immediate | Block item, notify compliance team, freeze pipeline |

---

## Roadmap & Future Enhancements

### Q1 2026: Accuracy Improvements


- [ ] Reduce FP rate to ≤1.0% through fine-tuned PyTorch models

- [ ] Increase ATP 5-19 coverage to 99.5%

- [ ] Implement human-in-the-loop review for borderline cases (0.45-0.55 confidence)

### Q2 2026: Multi-Language Support


- [ ] Extend JR validation to non-English content (Mandarin, Russian, Arabic)

- [ ] Translate ATP 5-19 rules for NATO allies (French, German, Polish)

### Q3 2026: Explainability & Auditing


- [ ] Generate human-readable validation reports (e.g., "Blocked due to ITAR Category VIII match: 'avionics architecture'")

- [ ] Integrate with ShadowTag audit trails for end-to-end provenance

### Q4 2026: Cost Optimization


- [ ] Implement validation result caching (30-day TTL) → reduce costs by 15-20%

- [ ] Tier-based routing (skip ATP 5-19 for Tier 3 items) → save 30% on API calls

---

## Integration with Cor.8 Ecosystem

| Cor.8 Component | Judge #6 Input | Judge #6 Output |
|-----------------|----------------|-----------------|
| **Gemini Ingestion Layer** | Classified items (Tier 1/2/3) | Validation pass/fail/flag |
| **ShadowTag Attestation** | Validation results | Attestation level (L2/L4) or rejection |
| **PNT System** | Geo-tagged intelligence | Threat alerts for anti-spoofing |
| **Aviation Vertical** | FAA filings, NOTAM updates | Compliance-validated updates |
| **Defense & ISR** | FOIA docs, DoD contracts | ATP 5-19 validated intel |

---

## References & Related Documentation


- **[Gemini Ingestion Layer](./gemini-ingestion-layer.md)** — Upstream data collection

- **[ShadowTag Verification Layer](./shadowtag-verification.md)** — Downstream attestation

- **[Defense & ISR Vertical](../05-verticals/defense-isr.md)** — DoD use cases

- **[Regulatory Compliance Checklists](../10-regulatory/compliance-checklists.md)** — NIST RMF, ITAR, EAR

---

## Status & Ownership

**Current Phase:** Production (deployed Q4 2025)
**Expected Uptime:** 99.9% (3-nines SLA)
**Team:** Validation Systems (4 engineers, 2 ML specialists, 1 SRE)
**On-Call Rotation:** 24/7 PagerDuty for P0/P1 incidents

**Monitoring:**

- **Grafana Dashboard:** https://grafana.aiyou.ai/d/judge-six-validation

- **Logs:** Cloud Logging (project: `aiyou-validation-prod`)

- **Alerts:** Slack #validation-alerts, PagerDuty for critical

**Contact:** validation-team@aiyou.ai

---

*"Validation is trust. Trust is value."*
