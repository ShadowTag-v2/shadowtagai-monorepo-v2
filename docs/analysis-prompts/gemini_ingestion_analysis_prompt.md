# Gemini Ingestion Layer Analysis Prompt

**Target Model**: Gemini 2.0 Pro
**Confidence Target**: ≥60% (specs-only, pre-production)
**Version**: 1.0
**Last Updated**: 2025-11-15

---

## Purpose

Analyze the **Gemini Ingestion Layer** architecture, implementation, and operational readiness for the PNKLN Core Stack™ intelligence collection pipeline.

The Ingestion Layer is a **nightly CronJob-based intelligence collection system** running on GKE, responsible for gathering, classifying, and delivering intelligence from multiple sources to downstream services.

---

## System Context

### Role in PNKLN Core Stack

- **Position**: Upstream intelligence collection (foundational layer)
- **Architecture**: GKE CronJob Multi-Container
- **Runtime**: ~45 minutes/night (nightly at 2:00 AM UTC)
- **Cost**: ~$77/month operational
- **Integration**: **CALLED BY** services in 4 namespaces (judge6-system, analytics, briefing, archive)

### Key Differences from Judge 6

| Aspect              | Judge 6 (Enforcement)          | Gemini Ingestion (Collection)         |
| ------------------- | ------------------------------- | ------------------------------------- |
| **Architecture**    | Hybrid Gemini+PyTorch real-time | GKE CronJob multi-container batch     |
| **Primary Metric**  | p99 latency ≤90ms               | Runtime ≤45 min/night                 |
| **Throughput**      | 2.7M validations/day            | 100+ items/night                      |
| **Key Metrics**     | Latency, block rate, FP/FN      | Items/day, sources, cost/item         |
| **Integration**     | Calls services (downstream)     | Called by services (upstream)         |
| **Unique Features** | Compliance Framework, JR validation         | Ethical crawling, tier classification |
| **Cost Model**      | Per API call                    | Monthly operational (~$77)            |
| **Quality Focus**   | False positive/negative rates   | Relevance, timeliness, completeness   |

---

## Analysis Objectives

Provide a comprehensive architectural review covering:

### 1. **Architecture & Design**

- Multi-container CronJob architecture assessment
- Sidecar pattern for source collectors (YouTube, Twitter, News)
- Gemini 2.0 Flash integration for classification
- Shared volume communication between containers

### 2. **Performance & Efficiency**

Analyze runtime efficiency metrics:

- **Target**: ~45 minutes/night
- **Batch size optimization**: 10 items/classification call
- **Concurrency limits**: 10 parallel operations
- **Resource allocation**: CPU/memory per container

### 3. **Quality Gates**

Evaluate quality gate thresholds:

- **Items/Day**: ≥100 daily intelligence items
- **Source Diversity**: ≥5 sources (YouTube, Twitter, News, RSS, Reddit, HackerNews)
- **Cost/Item**: ≤$0.01 per item
- **Relevance Score**: ≥0.7 average
- **Runtime**: ≤45 minutes

### 4. **Ethical Compliance Model**

Assess ethical crawling implementation:

- **robots.txt compliance**: Automated respect for exclusion rules
- **Rate limiting**: 2 requests/second per source
- **Transparent user agent**: "PNKLN-Ingestion-Bot/1.0"
- **No aggressive scraping**: Backoff on 429/503 errors

### 5. **Multi-Source Coverage Analysis**

Evaluate source diversity and coverage:

- **YouTube**: Video intelligence via YouTube Data API
- **Twitter/X**: Social intelligence via Twitter API v2
- **News**: News intelligence via NewsAPI
- **RSS**: Custom RSS feed parsing
- **Reddit**: Trending discussions
- **HackerNews**: Tech news and discussions

Analyze:

- Source reliability and uptime
- Data quality per source
- Coverage gaps or over-reliance
- API cost per source

### 6. **Tier Classification Metrics**

Review the tier classification system:

- **Tier 1** (High-value): Composite score ≥0.9
- **Tier 2** (Medium-value): Composite score ≥0.7
- **Tier 3** (Low-value): Composite score <0.7

**Composite Score** = (Relevance + Timeliness + Completeness) / 3

Analyze:

- Tier distribution (target: 20% Tier 1, 50% Tier 2, 30% Tier 3)
- Gemini classification accuracy
- Tier rebalancing strategies

### 7. **AM Briefing Delivery Effectiveness**

Evaluate morning briefing generation:

- **Input**: Top 10 Tier 1 items
- **Format**: Executive summary (3-5 bullets), key takeaways, actions
- **Delivery**: 7:00 AM UTC to downstream services
- **Quality**: Relevance, actionability, conciseness

### 8. **Cost Optimization**

Analyze operational costs (~$77/month):

- **Gemini API costs**: ~$50/month (batch classification)
- **Source API costs**: ~$20/month (YouTube, Twitter, News)
- **GKE compute**: ~$7/month (CronJob resources)
- **Sensitivity analysis**: What if item volume 2x?

### 9. **Integration & Dependencies**

Review integration with PNKLN Core Stack:

- **Output to**:
  - GCS: `gs://pnkln-core-stack-intelligence/`
  - BigQuery: `pnkln_intelligence` dataset
  - AM Briefing service
- **Called by**:
  - judge6-system (for validation context)
  - analytics (for trends)
  - briefing service (for delivery)
  - archive service (for historical analysis)

### 10. **Operational Readiness**

Assess production deployment readiness:

- **Monitoring**: Prometheus metrics, Cloud Monitoring
- **Alerting**: Quality gate failures, runtime overruns
- **Error handling**: Source API failures, Gemini errors
- **Retry logic**: Exponential backoff on transient failures
- **Logging**: Structured logs for debugging

---

## Analysis Framework

### Primary Sources

Review the following artifacts (pre-production, specs-only):

1. **Kubernetes CronJob YAML**
   - File: `k8s/gemini_ingestion_cronjob.yaml`
   - Focus: Container specs, resource limits, scheduling, security context

2. **Orchestrator Implementation**
   - File: `src/ingestion-layer/ingestion_orchestrator.py`
   - Focus: Collection logic, Gemini integration, quality metrics

3. **Architecture Documentation**
   - File: `README.md` (Ingestion Layer section)
   - Focus: System design, data flow, integration points

4. **Deployment Scripts**
   - File: `scripts/master_deploy.sh`
   - Focus: Deployment sequence, validation steps

### Analysis Depth

For each component, provide:

1. **Assessment** (Current state, strengths, weaknesses)
2. **Risks** (Potential failure modes, bottlenecks)
3. **Recommendations** (Concrete improvements with priority)
4. **Confidence Level** (0-100%, based on available information)

**Minimum Acceptable Confidence**: 60% (specs-only)
**Target Confidence for Production**: 85% (with real telemetry)

---

## Output Format

Provide a structured report with the following sections:

### Executive Summary

- Overall readiness assessment (RED/YELLOW/GREEN)
- Top 3 strengths
- Top 3 risks
- Go/No-Go recommendation with conditions

### Architecture Review

- Design assessment
- Scalability analysis
- Failure mode analysis

### Performance & Efficiency

- Runtime analysis
- Batch size optimization
- Resource utilization

### Quality & Compliance

- Quality gate validation
- Ethical compliance assessment
- Tier classification effectiveness

### Source Coverage

- Source diversity analysis
- Coverage gap identification
- Reliability assessment

### Cost Analysis

- Monthly cost breakdown
- Sensitivity to scale
- Optimization opportunities

### Integration Review

- Upstream callers analysis
- Downstream handoffs
- Integration risks

### Operational Readiness

- Monitoring & alerting
- Error handling
- Runbook completeness

### Recommendations

Prioritized list of improvements:

- **P0** (Critical, blocker)
- **P1** (High, should fix before prod)
- **P2** (Medium, nice to have)

Each with:

- Issue description
- Impact assessment
- Proposed fix
- Estimated effort

---

## Success Criteria

The analysis should enable decision-makers to:

1. **Understand** the Ingestion Layer's role in PNKLN Core Stack
2. **Identify** risks and bottlenecks before production deployment
3. **Prioritize** improvements based on impact and effort
4. **Decide** go/no-go for production with clear conditions

---

## Notes for Gemini 2.0 Pro

- **Context length**: Utilize full 1M token context for comprehensive analysis
- **Structured output**: Use markdown tables, bullet lists, and code snippets
- **Confidence scoring**: Explicitly state confidence (0-100%) for each assessment
- **Actionable recommendations**: Provide concrete fixes, not vague suggestions
- **PNKLN awareness**: Consider integration with Judge 6, analytics, and briefing services

---

## Appendix: Quality Gate Thresholds

| Gate                 | Threshold | Current (Estimated)   | Pass/Fail     |
| -------------------- | --------- | --------------------- | ------------- |
| **Items/Day**        | ≥100      | ~150 (projected)      | ✓ PASS (est.) |
| **Source Diversity** | ≥5        | 6 sources             | ✓ PASS        |
| **Cost/Item**        | ≤$0.01    | ~$0.005 (projected)   | ✓ PASS (est.) |
| **Relevance Score**  | ≥0.7      | TBD (needs prod data) | ? UNKNOWN     |
| **Runtime**          | ≤45 min   | ~40 min (projected)   | ✓ PASS (est.) |

---

**End of Prompt**

Run this analysis and provide a comprehensive review of the Gemini Ingestion Layer for PNKLN Core Stack™.
