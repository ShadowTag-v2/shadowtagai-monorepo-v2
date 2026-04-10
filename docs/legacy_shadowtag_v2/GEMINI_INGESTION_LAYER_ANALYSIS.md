# Gemini Ingestion Layer Analysis Prompt

## Overview

This document specifies the Gemini Ingestion Layer Analysis Prompt, adapted from the Judge #6 validation framework for intelligence collection pipeline analysis. The ingestion layer operates as a proactive collector feeding the SHADOWTAGAI Core Stack™, contrasting with Judge #6's reactive enforcement role.

**System Role**: Pre-production intelligence collection pipeline
**Runtime Model**: GKE CronJob (nightly batch processing)
**Target Runtime**: ~45 minutes/night
**Monthly Operational Cost**: ~$77
**Analysis Confidence Target**: ≥60% (specs-only, pre-production)

---

## Architecture Comparison: Judge #6 vs Gemini Ingestion Layer

| Aspect               | Judge #6 (Validation)                       | Gemini Ingestion Layer (Collection)     |
| -------------------- | ------------------------------------------- | --------------------------------------- |
| **Primary Function** | Reactive enforcement/validation             | Proactive data collection               |
| **Architecture**     | Hybrid Gemini+PyTorch+Rules (3-layer)       | GKE CronJob Multi-Container             |
| **Deployment**       | Sidecar pattern, synchronous                | Batch cron, nightly execution           |
| **Key Metrics**      | p99 latency ≤90ms, throughput, block rate   | Items/day, sources, cost/item, scores   |
| **Performance SLA**  | p99 ≤90ms total, <500µs Judge path          | ~45 min/night runtime efficiency        |
| **Quality Gates**    | 98% PRB coverage (Purpose/Reasons/Brakes)   | Items, sources, costs, relevance scores |
| **Integration**      | Calls services in 4 namespaces              | Called by services in 4 namespaces      |
| **Position**         | Enforcement layer (reactive)                | Foundation layer (acquisitive)          |
| **Unique Features**  | ATP 5-19 risk stratification, JR validation | Ethical crawling, tier classification   |
| **Cost Model**       | API calls per validation                    | Monthly operational ~$77                |
| **Quality Focus**    | FP/FN rates, coverage %                     | Relevance, timeliness, completeness     |

---

## Direct Replacements

### 1. Component Identity

- **From**: "Judge #6"

- **To**: "Gemini Ingestion Layer"

- **Rationale**: Domain-specific focus on intelligence collection vs enforcement

### 2. File References

- **From**: `judge_six.py` (single script)

- **To**: Pipeline documentation, architecture specs, flowcharts, config files

- **Rationale**: Distributed ingestion system requires broader artifact analysis

### 3. Performance Metrics

- **From**: p99 ≤90ms (real-time latency)

- **To**: ~45 min/night runtime efficiency

- **Rationale**: Batch processing optimizes for bulk throughput over per-operation speed

### 4. Quality Gates

- **From**: 98% PRB coverage (binary threshold)

- **To**: Multi-dimensional quality gates:
  - Daily items ingested (volume)

  - Source diversity (breadth)

  - Per-item costs (efficiency)

  - Relevance scores (quality)

- **Rationale**: Prevents over-optimization for quantity at expense of downstream usability

---

## New Sections Added

### 1. Ethical Compliance Model

**Purpose**: Ensure crawler-based ingestion adheres to web standards and legal requirements

**Key Metrics**:

- `robots.txt` compliance rate: ≥99.9%

- Rate limiting adherence: No source exceeds 1 req/sec sustained

- Transparency: User-Agent identification in all requests

- Attribution tracking: Immutable source lineage in GCS logs

**Risk Mitigation**:

- RA-1: Legal violation → Multi-layer validation (pre-crawl checks + runtime monitoring)

- RA-2: Source bans → Exponential backoff + allowlist management

- ATP 5-19 Integration: Ethical gates enforce deterministic blocks for non-compliant sources

**SHADOWTAGAI Stack Impact**: Trust-building for entire platform, reduces litigation risk

### 2. Multi-Source Coverage Analysis

**Target Sources**:

- YouTube (video intelligence)

- Twitter/X (real-time signals)

- News feeds (structured content)

- Academic papers (domain expertise)

- Government data (regulatory intelligence)

- Dark web monitors (threat intelligence)

**Coverage Metrics**:

- Source diversity index: Shannon entropy across categories

- Bias detection: Over-reliance thresholds (no source >40% of daily volume)

- Gap analysis: Weekly review of underrepresented verticals

**Optimization Triggers**:

- If Twitter >60% of volume → Expand news/academic crawlers

- If Tier 1 sources <30% → Retune classification algorithms

### 3. Tier Classification Metrics

**Tier Definitions**:

- **Tier 1**: High-value, verified sources (e.g., .gov, peer-reviewed)

- **Tier 2**: Medium-value, curated sources (e.g., major news outlets)

- **Tier 3**: Low-value, unverified sources (e.g., social media aggregates)

**Target Distribution** (daily ingestion):

- Tier 1: ≥30%

- Tier 2: 40-50%

- Tier 3: ≤30%

**Quality Indicators**:

- Tier 1 relevance score: ≥0.85

- Tier 2 relevance score: ≥0.70

- Tier 3 relevance score: ≥0.50

**Classification Pipeline**:

```yaml
step1_source_reputation:
  method: "Domain allowlist + historical scoring"
  latency: "<100ms"

step2_content_analysis:
  method: "Gemini 2.0 Pro semantic evaluation"
  latency: "<2s per item"

step3_attribution_verification:
  method: "Cross-reference with trusted databases"
  latency: "<500ms"

aggregation:
  voting: "Majority 2/3 to assign tier"
  disputes: "Human review queue (asynch)"
```

### 4. AM Briefing Delivery Effectiveness

**Purpose**: Ensure ingested intelligence translates to actionable morning summaries

**Format Requirements**:

- Length: 500-1000 words (5-minute read)

- Structure: Executive summary + tiered findings + action items

- Delivery: 06:00 Pacific, ±5 minutes

- Channels: Secure email + encrypted Slack webhook

**Quality Gates**:

- Relevance: ≥4/5 user rating (weekly survey)

- Timeliness: 100% on-time delivery (43min/month budget)

- Completeness: All Tier 1 items from prior 24h included

- Actionability: ≥2 concrete next steps per briefing

**Feedback Loop**:

- Daily: Automated click-through tracking on action items

- Weekly: User survey on utility and clarity

- Monthly: Gemini re-tuning based on low-rated briefings

---

## Context-Specific Adaptations

### Architecture: GKE CronJob Multi-Container

**Deployment Model**:

```yaml
namespace: intelligence-pipeline/
schedule: "0 2 * * *" # 02:00 Pacific daily
containers:
  - name: crawler-orchestrator
    image: shadowtagai/crawler-orchestrator:v2.1
    resources:
      requests: { cpu: "500m", memory: "1Gi" }
      limits: { cpu: "2", memory: "4Gi" }

  - name: gemini-classifier
    image: shadowtagai/gemini-classifier:v1.3
    resources:
      requests: { cpu: "1", memory: "2Gi" }
      limits: { cpu: "4", memory: "8Gi" }

  - name: storage-writer
    image: shadowtagai/storage-writer:v1.0
    resources:
      requests: { cpu: "250m", memory: "512Mi" }
      limits: { cpu: "1", memory: "2Gi" }

volumes:
  - name: ingestion-cache
    persistentVolumeClaim:
      claimName: ingestion-pvc-500gb
```

**Analysis Focus**:

- Fault tolerance: Pod restart policies, failure retry logic

- Resource allocation: CPU/memory tuning for 45-min target

- Scalability: Horizontal pod autoscaling for variable volumes

### Key Metrics: Items/Day, Sources, Cost/Item

**Operational Dashboard** (Grafana):

- **Items/Day**: Target 10,000-15,000 (scales with coverage expansion)

- **Active Sources**: Target 50-100 (diverse, tier-balanced)

- **Cost/Item**: Target $0.0051 ($77/mo ÷ 15k items)

- **Relevance Score**: Weighted average ≥0.72

**Cost Breakdown** (~$77/mo):

```yaml
gke_compute: "$35/mo (CronJob node pool, 4 vCPU)"
gemini_api: "$25/mo (Gemini 2.0 Pro classification, ~450k tokens/night)"
storage: "$10/mo (GCS + Firestore writes)"
networking: "$7/mo (egress to crawled sources)"
```

**Sensitivity Analysis**:

- If items/day doubles → Cost scales to ~$140/mo (linear Gemini API usage)

- If runtime exceeds 60 min → Add 2 vCPU (+$17.50/mo)

### Integration: Called by Services in 4 Namespaces

**Upstream Triggers** (services that invoke ingestion):

```yaml
namespace: gke-gateway-system/
  service: inference-gateway
  trigger: "User requests for fresh intelligence"
  method: "Async queue (Pub/Sub)"

namespace: gke-monitoring-system/
  service: prometheus-alerts
  trigger: "Source outage detection"
  method: "Webhook callback"

namespace: gke-training-system/
  service: fine-tuning-orchestrator
  trigger: "New training corpus requests"
  method: "Direct API call"

namespace: intelligence-pipeline/
  service: cor-64-nightly
  trigger: "Scheduled intelligence synthesis"
  method: "Cron dependency chain"

```

**Downstream Handoffs** (ingestion outputs to):

```yaml
firestore_collections:
  - ingested_items/ # Raw classified data

  - tier_classifications/ # Tier assignments + scores

  - source_health/ # Crawl success rates

gcs_buckets:
  - ${PROJECT_ID}-shadowtagai-raw-intel/ # Unprocessed artifacts

  - ${PROJECT_ID}-shadowtagai-classified-intel/ # Tier-sorted outputs

pubsub_topics:
  - ingestion-complete # Triggers downstream processors

  - ingestion-failures # Alerts for manual review
```

**Analysis Focus**:

- Handoff latency: Time from ingestion-complete to downstream consumption

- Failure propagation: How ingestion failures affect dependent services

- Backpressure handling: Queue depth monitoring during high-volume periods

---

## Confidence Adjustments

### Pre-Production Constraints

**Target**: ≥60% confidence (vs ≥70% for Judge #6 production)

**Rationale**:

- Specs-only analysis lacks real-world telemetry (logs, metrics, traces)

- More assumptions required for cost/performance projections

- Tier classification untested at scale

**Confidence Boosters** (post-production):

- +10% with 30 days of operational logs

- +15% with user feedback on AM briefings

- +5% with A/B testing on classification algorithms

**Current Limitations**:

- No empirical data on source ban rates

- Gemini API cost estimates based on synthetic workloads

- Tier distribution assumptions from manual sampling

**Mitigation**:

- Flag all <60% confidence findings for human review

- Quarterly recalibration with production metrics

- Gemini 2.0 Pro self-reports uncertainty in outputs

---

## Quality Focus: Relevance, Timeliness, Completeness

### Relevance

**Definition**: Semantic alignment between ingested content and SHADOWTAGAI vertical priorities

**Measurement**:

- Gemini 2.0 Pro scoring: 0.0 (irrelevant) to 1.0 (critical)

- Baseline: DoD/FAA/FDA content ≥0.85, general tech ≥0.60

- User feedback: Weekly "Was this useful?" surveys

**Optimization**:

- Retune crawler keywords based on low-relevance clusters

- Expand allowlists for high-scoring domains

- Prune sources with sustained <0.50 scores

### Timeliness

**Definition**: Freshness of ingested data relative to publication time

**Measurement**:

- Crawl lag: Time from source publish to ingestion

- Target: ≤6 hours for Tier 1, ≤24 hours for Tier 2/3

- AM briefing: 100% include prior 24h Tier 1 items

**Optimization**:

- Increase cron frequency for breaking news sources (hourly)

- Implement webhook subscriptions where supported (RSS, APIs)

- Alerting for >12h lag on critical sources

### Completeness

**Definition**: Coverage of all relevant sources within defined scope

**Measurement**:

- Source uptime: % of planned sources successfully crawled

- Target: ≥95% daily (allows 5% transient failures)

- Gap detection: Weekly audit against master source list

**Optimization**:

- Exponential backoff for failed sources (3 retries, 5/15/45 min delays)

- Manual review queue for persistent failures (>3 days)

- Quarterly source list refresh (add emerging platforms, prune dead links)

---

## Cost Model: Monthly Operational ~$77

### Breakdown by Component

```yaml
infrastructure:
  gke_cronJob_node_pool:
    vcpu: 4
    memory: "16Gi"
    monthly_cost: "$35"
    utilization: "~15% (45 min/night = 3.1% of 24h)"
    optimization: "Consider spot VMs for -60% cost"

ai_services:
  gemini_2_0_pro_classification:
    tokens_per_night: "~450k (30 tokens/item × 15k items)"
    cost_per_1m_tokens: "$1.85"
    monthly_cost: "$25"
    optimization: "Batch requests for 10% volume discount"

storage:
  gcs_raw_intel:
    size: "~200GB/month (compressed JSON)"
    cost_per_gb: "$0.020"
    monthly_cost: "$4"

  gcs_classified_intel:
    size: "~100GB/month (filtered + tier-sorted)"
    cost_per_gb: "$0.020"
    monthly_cost: "$2"

  firestore_writes:
    writes_per_night: "~15k"
    cost_per_100k: "$0.90"
    monthly_cost: "$4"

networking:
  egress_to_sources:
    data_transfer: "~50GB/month"
    cost_per_gb: "$0.12"
    monthly_cost: "$6"

  pubsub_messages:
    messages_per_night: "~15k"
    cost_per_1m: "$0.40"
    monthly_cost: "$1"

total_monthly_cost: "$77"
```

### Scaling Scenarios

**2× Volume (30k items/night)**:

- Gemini API: $25 → $50 (+100%)

- GKE: $35 → $52 (add 2 vCPU, +49%)

- Storage: $10 → $17 (+70%, compresses better at scale)

- Networking: $7 → $11 (+57%)

- **Total**: $77 → $130 (+69%, sublinear scaling)

**10× Volume (150k items/night)**:

- Gemini API: $25 → $250 (+900%)

- GKE: $35 → $140 (16 vCPU, +300%)

- Storage: $10 → $50 (+400%)

- Networking: $7 → $40 (+471%)

- **Total**: $77 → $480 (+523%, requires architectural changes)

**Cost Kill-Switch**:

- If monthly cost >$150 → Alert + manual approval for next run

- If cost/item >$0.010 → Investigate classification inefficiencies

---

## File References and Analysis Artifacts

### Pipeline Documentation

- `docs/ingestion_architecture.md` - System design and data flow

- `docs/ethical_crawling_policy.md` - robots.txt compliance, rate limits

- `docs/tier_classification_rubric.md` - Tier 1/2/3 criteria and scoring

### Architecture Specs

- `k8s/intelligence-pipeline/cronJob-ingestion.yaml` - Kubernetes manifest

- `terraform/ingestion_foundation/main.tf` - GCP resource definitions

- `diagrams/ingestion_flowchart.svg` - Visual pipeline representation

### Configuration Files

- `config/source_allowlist.yaml` - Approved crawl targets by tier

- `config/gemini_classification_prompts.yaml` - Tier scoring templates

- `config/am_briefing_template.md` - Morning summary format

### Monitoring and Telemetry

- Prometheus metrics: `ingestion_items_total`, `ingestion_cost_per_item`, `source_success_rate`

- Grafana dashboard: `SHADOWTAGAI Ingestion Health` (15-panel overview)

- Jaeger traces: End-to-end latency breakdown per source

---

## Next Steps and Iteration

### Test Runs

1. **Dummy Specs Analysis**: Run Gemini 2.0 Pro on synthetic pipeline docs to calibrate outputs

2. **Ethical Section Validation**: Verify robots.txt compliance logic with known edge cases

3. **Cost Projection Accuracy**: Compare estimates against 7-day pilot run

### Visualization

- Add report generation: Tier distribution pie charts, source health heatmaps

- Grafana integration: Auto-populate dashboards from analysis JSON outputs

- AM briefing preview: Sample rendered summaries in analysis reports

### Edge Cases

- **Source Outages**: Simulate 50% source failure, validate retry/fallback logic

- **Cost Spikes**: Inject 5× volume surge, test auto-scaling and kill-switches

- **Tier Misclassification**: Analyze false Tier 1 assignments (low relevance but high source reputation)

### Integration with Judge #6

- **End-to-End Flow**: Analyze handoff from ingestion → Judge #6 validation

- **Combined Prompt**: Unified analysis covering collection → enforcement pipeline

- **Latency Budget**: Partition 90ms total SLA across ingestion (asynch) + Judge (≤10ms)

---

## Deployment Readiness

**Status**: ✅ Ready for pilot deployment (30-day validation)

**Pre-Production Checklist**:

- [ ] GKE CronJob deployed to `intelligence-pipeline/` namespace

- [ ] Gemini 2.0 Pro API keys configured with $100/mo quota

- [ ] Source allowlist populated with initial 25 Tier 1 sources

- [ ] Ethical compliance monitoring enabled (robots.txt validator)

- [ ] AM briefing delivery tested to secure channels

- [ ] Cost alerting configured (>$150/mo threshold)

**Pilot Success Criteria** (30 days):

- Items/day: ≥10k sustained

- Cost/item: ≤$0.0077

- Runtime: ≤60 min/night (90th percentile)

- Tier 1 %: ≥25%

- AM briefing delivery: ≥95% on-time

- User satisfaction: ≥3.5/5 average rating

**Production Promotion Gates**:

- All pilot criteria met for 21/30 days

- Zero RA-1 ethical violations

- <3 manual interventions/week

- Formal approval from SHADOWTAGAI Core Stack™ governance board

---

## Appendix: Gemini 2.0 Pro Prompt Template

```markdown
You are analyzing the SHADOWTAGAI Gemini Ingestion Layer, a pre-production intelligence
collection pipeline deployed as a GKE CronJob. Your task is to evaluate architecture,
performance, ethical compliance, and integration readiness based on provided
specifications and documentation.

## Context

- **System**: Gemini Ingestion Layer (nightly batch intelligence collection)

- **Runtime**: ~45 min/night target

- **Cost**: ~$77/mo operational budget

- **Quality Gates**: Items/day, source diversity, cost/item, relevance scores

- **Confidence**: Aim for ≥60% (specs-only, no production telemetry)

## Analysis Dimensions

1. **Ethical Compliance**: robots.txt adherence, rate limiting, transparency

2. **Multi-Source Coverage**: Diversity across YouTube, Twitter, news, academic, gov, dark web

3. **Tier Classification**: Distribution and accuracy of Tier 1/2/3 assignments

4. **AM Briefing Effectiveness**: Delivery timeliness, format quality, actionability

5. **Cost Efficiency**: $/item, scaling sensitivity, kill-switch thresholds

6. **Integration Readiness**: Upstream triggers, downstream handoffs, failure propagation

## Artifacts to Review

- Pipeline documentation (architecture, flowcharts)

- GKE CronJob manifests (k8s YAML)

- Terraform infrastructure specs

- Source allowlists and classification rubrics

- Monitoring configurations (Prometheus, Grafana)

## Output Format

Provide a structured report with:

- Executive summary (3-5 sentences)

- Per-dimension analysis (findings + confidence scores)

- Risk assessment (ATP 5-19 stratification: RA-1 to RA-4)

- Recommendations (prioritized by impact)

- Confidence caveats (what's missing for ≥70% confidence)

Flag any <60% confidence findings for human review. Be direct and results-oriented.
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Maintainer**: SHADOWTAGAI Core Stack™ Architecture Team
**Related Docs**: `SHADOWTAGAI_THREAD_ROLLUP_COMPREHENSIVE.md`, `judge_six_analysis_prompt.md`
