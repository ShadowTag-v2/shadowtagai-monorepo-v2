# ADR 002: Collection → Enforcement Dual-Layer Architecture

**Status:** ✅ ACCEPTED

**Date:** 2025-11-15

**Supersedes:** ADR-001 (extends enforcement-first architecture with upstream collection layer)

**Decision Makers:** ShadowTagAi Engineering Team

---

## Context and Problem Statement

ADR-001 established enforcement-first architecture (Judge #6 + JR Engine) for compliance validation. However, this addressed only the **downstream** enforcement problem. The **upstream** intelligence collection problem remained unsolved:

- No standardized data collection pipeline

- No ethical compliance validation for web crawling

- No quality scoring for collected intelligence

- No tier classification for data sources

- No integration between collection and enforcement layers

**Key Insight:** Collection and enforcement are complementary—enforcement without quality input data produces garbage audits.

---

## Decision

Implement **dual-layer architecture** combining intelligence collection (upstream) with compliance enforcement (downstream):

```

┌─────────────────────────────────────────────────────────┐
│              SHADOWTAGAI Core Stack Architecture               │
│                                                          │
│  LAYER 1: Gemini Ingestion (Collection - Upstream)      │
│  ├─ Multi-source data collection                        │
│  ├─ Ethical compliance validation                       │
│  ├─ Tier classification (1/2/3)                         │
│  ├─ Quality scoring (relevance/timeliness/completeness) │
│  └─ AM briefing delivery                                │
│                                                          │
│  LAYER 2: Judge #6 + JR Engine (Enforcement - Downstream)│
│  ├─ Purpose/Reasons/Brakes validation                   │
│  ├─ GDPR/CAN-SPAM/HIPAA compliance                      │
│  ├─ Content policy enforcement                          │
│  └─ Audit trail generation                              │
│                                                          │
│  INTEGRATION: Intelligence Agent                         │
│  └─ Collection → Validation → Enforcement → Briefing    │
└─────────────────────────────────────────────────────────┘

```

---

## Architecture: Gemini Ingestion Layer

### Purpose

Proactive intelligence collector (upstream of enforcement)

### Key Characteristics

| Aspect              | Judge #6 (Downstream)           | Gemini Ingestion (Upstream)           |
| ------------------- | ------------------------------- | ------------------------------------- |
| **Function**        | Reactive validator              | Proactive collector                   |
| **Architecture**    | Hybrid Gemini+PyTorch           | GKE CronJob Multi-Container           |
| **Performance**     | p99 ≤90ms (real-time)           | ~45 min/night (batch)                 |
| **Key Metrics**     | Latency, Throughput, Block Rate | Items/Day, Sources, Cost/Item, Scores |
| **Integration**     | Calls Services in 4 Namespaces  | Called by Services in 4 Namespaces    |
| **Unique Features** | ATP 5-19, JR Validation         | Ethical Crawling, Tier Classification |
| **Cost Model**      | API Calls per Validation        | Monthly Operational ~$77              |
| **Quality Focus**   | FP/FN Rates (accuracy)          | Relevance, Timeliness, Completeness   |

### Quality Gates

```python
quality_gates = {
    'items_per_day': ≥1000,  # High-quality items collected
    'unique_sources': ≥10,    # Diverse source coverage
    'cost_per_item': ≤$0.10,  # Economic efficiency
    'relevance_score': ≥0.7,  # Quality threshold
    'runtime': ≤45 min,       # Batch efficiency
    'ethical_compliance': 100%, # Zero critical violations
}

```

### Tier Classification

**Tier 1 (High-Value Authoritative):** 20% target

- .gov, .edu, .mil domains

- Major news: NYT, Reuters, Bloomberg

- Academic: arXiv, Nature, Science

**Tier 2 (Moderate-Value Verified):** 50% target

- Established tech blogs: TechCrunch

- Verified social: Twitter Blue, YouTube channels

- Industry publications

**Tier 3 (Low-Value General):** 30% acceptable

- User-generated content

- Forums, Reddit

- Aggregators

### Ethical Compliance Model

```python
ethical_validations = [
    'robots.txt_compliance',      # Respect site crawling rules
    'rate_limiting',              # <60 req/hour default
    'attribution',                # Source URL preservation
    'transparency',               # SHADOWTAGAIBot user agent
    'privacy_respect',            # No personal data scraping
]

```

---

## Multi-Source Coverage

### Required Source Types

| Source Type    | Priority    | Example Sources  | Rate Limit |
| -------------- | ----------- | ---------------- | ---------- |
| **News**       | Required    | NYT, Reuters     | 30/hour    |
| **Academic**   | Required    | arXiv, JSTOR     | 60/hour    |
| **YouTube**    | Recommended | YouTube Data API | 100/hour   |
| **Twitter**    | Recommended | Twitter API v2   | 180/hour   |
| **Government** | Recommended | Federal Register | 60/hour    |
| **RSS**        | Optional    | Various feeds    | Varies     |

### Source Type Requirements

- **Minimum:** 3 different source types

- **Required types:** News + Academic

- **Recommended:** News + Academic + (YouTube OR Twitter OR Government)

---

## Intelligence Agent: Complete Pipeline

### Architecture

```python
class IntelligenceAgent(ShadowTagAiAgent):
    """
    Complete collection → enforcement pipeline


    1. Gemini Ingestion Layer (Collection)
       ├─ Multi-source data collection
       ├─ Ethical compliance validation
       ├─ Tier classification
       └─ Quality scoring


    2. JR Engine Validation (Intent)
       └─ Validate collection purpose


    3. Judge #6 Enforcement (Compliance)
       ├─ GDPR/CAN-SPAM checks
       └─ Content policy verification


    4. AM Briefing Delivery (Output)
       └─ Formatted intelligence summary
    """

```

### Use Cases

1. **Daily Intelligence Briefing**
   - Nightly cron job (~45 min runtime)

   - Collect from 10+ sources

   - Filter to 1000+ quality items

   - Deliver morning summary

2. **On-Demand Intelligence Collection**
   - User query: "AI agent frameworks and LLM developments"

   - Target: 100 items

   - Sources: News + Academic + YouTube

   - Enforcement: GDPR/attribution compliance

3. **Compliance-Verified Data Gathering**
   - Collect data for analysis

   - Ensure ethical crawling

   - Verify tier distribution

   - Export audit trail

---

## Operational Costs

### Gemini Ingestion Layer

| Component              | Cost/Month                          |
| ---------------------- | ----------------------------------- |
| **Gemini API**         | ~$15-25 (1000 items/day × $0.50/1k) |
| **GKE Infrastructure** | ~$50 (cron job + storage)           |
| **Bandwidth**          | ~$2-5                               |
| **Total**              | **~$77/month**                      |

### Combined Stack (Collection + Enforcement)

| Layer                    | Cost/Month             |
| ------------------------ | ---------------------- |
| **Gemini Ingestion**     | $77                    |
| **Judge #6 + JR Engine** | $1,000-1,600           |
| **Total**                | **$1,077-1,677/month** |

**Break-Even (with collection):**

- Need: 4-6 customers @ $297/mo OR

- 10,777-16,770 validated leads @ $0.10/lead

---

## Integration Patterns

### Pattern 1: Intelligence Agent (Full Pipeline)

```python
from shadowtagai_agents import IntelligenceAgent, IntelligenceTask

agent = IntelligenceAgent()

result = agent.collect_intelligence(
    IntelligenceTask(
        query="AI agent frameworks",
        target_items=100,
        customer_id="customer_123",
        require_enforcement=True,
        require_briefing=True,
    )
)

# Output: IntelligenceResult with:

# - ingestion_result (collection metrics)

# - verification_result (compliance status)

# - briefing (formatted summary)

# - audit_trail (complete pipeline audit)

```

### Pattern 2: Standalone Ingestion

```python
from shadowtagai_agents import GeminiIngestionLayer, DEFAULT_SOURCES

ingestion = GeminiIngestionLayer()
for source in DEFAULT_SOURCES:
    ingestion.register_source(source)

result = ingestion.ingest(target_items=1000)

# Output: IngestionResult with:

# - items (collected data)

# - metrics (quality gates, tier distribution)

# - violations (ethical compliance issues)

```

### Pattern 3: Enforcement-Only (ADR-001)

```python
from shadowtagai_agents import ComplianceSDRAgent

agent = ComplianceSDRAgent()

result = agent.generate_leads(
    query="German fintech CTOs",
    target_count=100,
    customer_id="customer_123"
)

# Output: LeadGenerationResult with enforcement

```

---

## Comparison: Judge #6 vs Gemini Ingestion

### Adapted from Judge #6 Analysis Prompt

| Dimension               | Judge #6 (Enforcement)    | Gemini Ingestion (Collection)     |
| ----------------------- | ------------------------- | --------------------------------- |
| **File References**     | judge_six.py              | Pipeline docs, architecture specs |
| **Performance Metrics** | p99 ≤90ms (real-time)     | ~45 min/night (batch)             |
| **Quality Gates**       | 98% Coverage (validation) | Items/Day, Sources, Cost, Scores  |
| **Architecture**        | Hybrid Gemini+PyTorch     | GKE CronJob Multi-Container       |
| **Cost Model**          | Per validation API call   | Monthly operational ~$77          |
| **Confidence Target**   | ≥70% (production data)    | ≥60% (specs-only, pre-prod)       |

### New Sections (Gemini Ingestion Only)

1. **Ethical Compliance Model**
   - robots.txt adherence

   - Rate limiting enforcement

   - Attribution requirements

   - Transparency (user agent)

2. **Multi-Source Coverage Analysis**
   - YouTube, Twitter, News, RSS, Academic, Government

   - Diversity metrics (≥10 sources, ≥3 types)

3. **Tier Classification Metrics**
   - Tier 1: 20% target (high-value)

   - Tier 2: 50% target (moderate-value)

   - Tier 3: 30% acceptable (low-value)

4. **AM Briefing Delivery Effectiveness**
   - Morning summary generation

   - Markdown/JSON/HTML formats

   - Relevance-sorted output

---

## Consequences

### Positive

- **Complete Pipeline:** Collection → Enforcement → Delivery

- **Ethical Intelligence:** robots.txt compliance, rate limiting, attribution

- **Quality Scoring:** Relevance/timeliness/completeness metrics

- **Tier Classification:** Prioritize high-value sources

- **Cost Efficiency:** $77/month for 30,000+ items/month

- **Reusable Components:** Ingestion layer usable in other contexts

### Negative

- **Increased Complexity:** Two layers to maintain (collection + enforcement)

- **Higher Total Cost:** $1,077-1,677/month (vs $1,000-1,600 enforcement-only)

- **Longer Development:** Collection layer adds scope to 7-day MVP

- **Integration Challenges:** Ensuring seamless handoff between layers

### Neutral

- **Confidence Adjustment:** 60% vs 70% (pre-prod vs prod)

- **Runtime Trade-off:** Batch processing (45 min) vs real-time (<90ms)

- **Use Case Separation:** Intelligence collection vs compliance enforcement

---

## Implementation Status

### Completed (v0.2.0)

- [x] Gemini Ingestion Layer module

- [x] Ethical compliance validator

- [x] Multi-source coverage analyzer

- [x] Tier classification system

- [x] Intelligence Agent (full pipeline)

- [x] Ingestion configuration

- [x] Default source registry

### Pending (Next Sprint)

- [ ] Actual source integrations (YouTube API, Twitter API, NewsAPI)

- [ ] robots.txt parser implementation

- [ ] Rate limiting persistence (Redis)

- [ ] PDF audit export for ingestion layer

- [ ] GKE cron job deployment

- [ ] AM briefing delivery system

---

## Testing Strategy

### Collection Layer Tests

```bash

# Unit tests

pytest tests/unit/test_gemini_ingestion.py
pytest tests/unit/test_ethical_compliance.py
pytest tests/unit/test_tier_classifier.py

# Integration tests

pytest tests/integration/test_intelligence_agent.py
pytest tests/integration/test_collection_enforcement_flow.py

```

### Quality Gate Validation

```python
def test_quality_gates():
    agent = IntelligenceAgent()
    result = agent.collect_intelligence(task)

    assert result.metrics['ingestion']['items_collected'] >= 1000
    assert result.metrics['ingestion']['unique_sources'] >= 10
    assert result.metrics['ingestion']['average_cost_per_item'] <= 0.10
    assert result.metrics['ingestion']['average_relevance'] >= 0.7
    assert result.metrics['ingestion']['runtime_minutes'] <= 45

```

---

## Deployment

### GKE Cron Job (Nightly Batch)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: shadowtagai-intelligence-collection
spec:
  schedule: "0 2 * * *" # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: intelligence-agent
              image: gcr.io/shadowtagai/intelligence-agent:latest
              env:
                - name: TARGET_ITEMS
                  value: "1000"

                - name: RUNTIME_LIMIT_MINUTES
                  value: "45"
          restartPolicy: OnFailure
```

---

## Monitoring

### Key Metrics

| Metric                            | Target  | Alert Threshold    |
| --------------------------------- | ------- | ------------------ |
| **Items/Day**                     | ≥1000   | <500 (warning)     |
| **Runtime**                       | ≤45 min | >60 min (critical) |
| **Cost/Item**                     | ≤$0.10  | >$0.15 (warning)   |
| **Relevance**                     | ≥0.7    | <0.5 (warning)     |
| **Ethical Violations (Critical)** | 0       | >0 (critical)      |
| **Tier 1 %**                      | ≥20%    | <10% (warning)     |

---

## Future Enhancements

1. **ML-Based Quality Scoring**
   - Train model to predict relevance

   - Replace rule-based scoring

2. **Dynamic Source Discovery**
   - Automatically discover new sources

   - Evaluate source quality

3. **Multi-Language Support**
   - Non-English source collection

   - Language detection

4. **Real-Time Streaming**
   - Supplement batch with real-time feeds

   - WebSocket/SSE delivery

---

## References

- ADR-001: Enforcement-First Agent Architecture

- Gemini Ingestion Layer Analysis Prompt (adapted from Judge #6 version)

- ATP 5-19: US Army risk assessment methodology

- robots.txt Standard: https://www.robotstxt.org/

- GDPR: EU General Data Protection Regulation

- CAN-SPAM: US email marketing law

---

**Status:** ✅ IMPLEMENTED (v0.2.0)

**Last Updated:** 2025-11-15

**Next Review:** After first production deployment (7-day sprint completion)
