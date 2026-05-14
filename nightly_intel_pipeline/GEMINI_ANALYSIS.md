# Gemini Ingestion Layer Analysis Prompt

**Comprehensive Analysis Framework for Intelligence Pipeline Evaluation**

This document outlines the Gemini 2.0 Pro analysis prompt architecture for evaluating the Nightly Intel Pipeline's ingestion layer, adapted from the Judge #6 validation system prompt.

## Overview

The Gemini Ingestion Layer Analysis Prompt is designed to perform comprehensive pre-production analysis of the intelligence collection pipeline, focusing on **proactive data acquisition** rather than reactive validation. This shift reflects the pipeline's role as a foundational layer in the PNKLN Core Stack™.

### Key Distinction: Collection vs. Enforcement

| Aspect | Judge #6 (Enforcement) | Gemini Ingestion Layer (Collection) |
|--------|------------------------|-------------------------------------|
| **Primary Role** | Reactive validator | Proactive collector |
| **Architecture** | Hybrid Gemini+PyTorch | GKE CronJob Multi-Container |
| **Performance Metrics** | p99 latency ≤90ms | ~45 min/night runtime efficiency |
| **Quality Gates** | 98% coverage threshold | Quality gates on items, sources, costs, scores |
| **Integration Pattern** | Calls services in 4 namespaces | Called by services in 4 namespaces |
| **Key Metrics** | Latency, throughput, block rate | Items/day, sources, cost/item, relevance |
| **Unique Features** | ATP 5-19, JR validation | Ethical crawling, tier classification |
| **Cost Model** | API calls per validation | Monthly operational ~$77 |
| **Quality Focus** | FP/FN rates | Relevance, timeliness, completeness |

## Direct Replacements: Domain Relevance

These replacements ensure the prompt stays focused on intelligence collection rather than enforcement:

### 1. **System Identity**
- **From**: "Judge #6" references throughout
- **To**: "Gemini Ingestion Layer" for all system references
- **Rationale**: Establishes clear domain context for Gemini 2.0 Pro's analysis

### 2. **File References**
- **From**: `judge_six.py` (single script)
- **To**: Pipeline documentation, architecture specs, flowcharts, config files
- **Rationale**: Ingestion layers are distributed systems requiring broader analysis scope. Enables evaluation of:
  - Multi-container orchestration diagrams
  - Kubernetes CronJob configurations
  - Data flow architecture
  - Integration dependencies

### 3. **Performance Metrics**
- **From**: p99 ≤90ms (real-time latency)
- **To**: ~45 min/night runtime efficiency (batch processing)
- **Rationale**: Nightly batch jobs optimize for total runtime, not per-request latency. This metric shift enables:
  - Parallelization opportunities in GKE
  - Resource allocation optimization
  - Cost efficiency analysis

### 4. **Quality Gates**
- **From**: 98% code coverage threshold
- **To**: Multi-faceted quality checks:
  - **Daily Items Ingested**: Volume metrics
  - **Source Diversity**: Coverage across YouTube, Twitter, arXiv, GitHub, News
  - **Cost per Item**: Budget sustainability (~$77/month target)
  - **Relevance Scores**: JR Engine quality assessment
- **Rationale**: Prevents over-optimization for quantity at expense of usability in downstream PNKLN components

## Context-Specific Adaptations

### Architecture Evolution

**Judge #6 (Hybrid Gemini+PyTorch)**
- Real-time inference for validation
- On-the-fly decision making
- Synchronous processing

**Gemini Ingestion Layer (GKE CronJob Multi-Container)**
- Scheduled batch processing (2 AM daily)
- Kubernetes orchestration for scalability
- Fault tolerance and retry mechanisms
- Resource optimization for variable data volumes

**Analysis Focus**:
- Container resource allocation (CPU/memory limits)
- Pod scheduling and node affinity
- Persistent volume claims for data storage
- Secret management for API keys

### Integration Pattern Flip

**Judge #6**: Caller (invokes 4 namespace services)
```
Judge #6 → Service A
         → Service B
         → Service C
         → Service D
```

**Ingestion Layer**: Callee (invoked by 4 namespace services)
```
Service A ┐
Service B ├→ Ingestion Layer → Data Store
Service C ┤
Service D ┘
```

**Analysis Implications**:
- Evaluate upstream trigger mechanisms
- Assess downstream handoff protocols
- Identify integration pain points
- Analyze backpressure handling

### Unique Features Comparison

#### Judge #6 Features
- **ATP 5-19 Compliance**: Risk level assessment (RA-1 through RA-4)
- **JR Validation**: Purpose → Reasons → Brakes framework
- **Real-time Blocking**: Immediate enforcement decisions

#### Ingestion Layer Features
- **Ethical Crawling**: RFC 9309 robots.txt compliance, rate limiting, circuit breakers
- **Tier Classification**: Strategic data prioritization
  - Tier 1: Executive review (score ≥85)
  - Tier 2: Auto-action approved (score ≥70)
  - Tier 3: Archive (score ≥50)
  - Tier 4: Low priority (<50)
- **Multi-Source Orchestration**: GitHub, arXiv, YouTube, Twitter, News APIs

**Analysis Emphasis**:
- Legal compliance verification (crawling standards)
- Resource allocation by tier priority
- Source coverage gaps and biases

## New Sections Added

These sections enhance depth and relevance for pre-production evaluation:

### 1. Ethical Compliance Model

**Analysis Areas**:
- **robots.txt Adherence**: RFC 9309 compliance verification
- **Rate Limiting**: Domain-specific delays (3-10 seconds)
- **Circuit Breaker**: Failure threshold handling
- **User-Agent Transparency**: Proper identification
- **Crawl-delay Respect**: Server load considerations

**Evaluation Criteria**:
```python
ETHICAL_COMPLIANCE_CHECKS = {
    "robots_txt_parsing": "24-hour cache, honor disallow rules",
    "rate_limiting": "Adaptive throttling with ±30% jitter",
    "circuit_breaker": "5 failures → 5-min timeout",
    "user_agent": "NightlyIntelBot/1.0 with contact URL",
    "legal_risk": "Assess ban/lawsuit probability"
}
```

### 2. Multi-Source Coverage Analysis

**Source Distribution Goals**:
- **GitHub**: 40% of daily items (repo discovery, code flattening)
- **arXiv**: 25% (recent papers in cs.AI, cs.LG, stat.ML)
- **YouTube**: 15% (video metadata, transcripts)
- **Twitter**: 10% (trending discussions, announcements)
- **News**: 10% (industry updates, regulatory changes)

**Analysis Metrics**:
- Source diversity (Gini coefficient)
- Bias detection (over-reliance on single source)
- Coverage gaps (missing critical sources)
- Expansion opportunities

### 3. Tier Classification Metrics

**Target Distribution**:
- Tier 1: 10-15% (high-value, executive review)
- Tier 2: 35-40% (actionable, auto-approved)
- Tier 3: 30-35% (archive, future reference)
- Tier 4: 15-20% (low priority, potential noise)

**Analysis Questions**:
- Is the distribution healthy or skewed toward low-value data?
- Are Tier 1 items truly executive-worthy?
- Should tier thresholds be adjusted?
- Are scoring criteria aligned with strategic goals?

### 4. AM Briefing Delivery Effectiveness

**Briefing Quality Metrics**:
- **Format**: Markdown with clear tier sections
- **Timeliness**: Delivered by 6 AM local time
- **Completeness**: Executive summary + tier breakdowns
- **Actionability**: Clear recommendations per tier
- **Readability**: Concise evaluations, no jargon overload

**Analysis Focus**:
- End-to-end pipeline success rate
- Briefing generation latency
- User feedback integration (if available)

## Confidence Adjustments

### Target Confidence Levels

**Judge #6 (Production System)**:
- **Target**: ≥70% confidence
- **Data Source**: Production telemetry, logs, real-world metrics
- **Rationale**: High confidence achievable with empirical data

**Gemini Ingestion Layer (Pre-Production)**:
- **Target**: ≥60% confidence
- **Data Source**: Specifications, architecture docs, design diagrams
- **Rationale**: Lower bar acknowledges lack of production telemetry, reduces frustration with uncertainty flags

**Post-Production Adjustment**:
Once deployed to GKE with operational metrics:
- Increase target to 70-75% confidence
- Incorporate actual runtime data, cost metrics, error rates
- Refine prompt with real-world edge cases

## Execution Recommendations

### Test Runs
Before full deployment, run Gemini 2.0 Pro on sample specifications:

1. **Ethical Compliance Test**: Verify robots.txt parsing logic analysis
2. **Architecture Evaluation**: Assess GKE resource allocation recommendations
3. **Cost Sensitivity**: Test reactions to cost spike scenarios
4. **Source Coverage**: Check multi-source gap detection

**Sample Prompt**:
```
Analyze the Gemini Ingestion Layer architecture specifications focusing on:
1. Ethical crawling compliance (RFC 9309, rate limiting)
2. GKE resource optimization (CPU/memory, pod scaling)
3. Monthly cost sustainability (~$77 target)
4. Multi-source coverage (GitHub, arXiv, YouTube, Twitter, News)
5. Tier classification distribution (target: 10-15% Tier 1)

Provide confidence scores (≥60%) for each analysis area.
```

### Visualization Enhancements

Request structured outputs from Gemini for better digestibility:

**Tables**:
- Tier distribution breakdown (actual vs. target)
- Source coverage matrix (items per source)
- Cost breakdown (API calls, storage, compute)

**Charts** (described in text):
- Runtime efficiency trends (45-min target)
- Quality score distribution (JR Engine outputs)
- Ethical compliance radar chart

### Edge Case Probes

Include failure mode analysis in prompts:

1. **Source Outages**: What if GitHub API is down for 2 hours?
2. **Cost Spikes**: How does system react to 3x item volume?
3. **Rate Limit Hits**: Circuit breaker activation scenarios
4. **Low-Quality Data**: All items score <50 (Tier 4)
5. **Kubernetes Failures**: Pod eviction, node downtime

### Integration with Judge #6

**Combined Analysis Opportunity**:
Since Ingestion Layer and Judge #6 are complementary (collection → validation), a unified prompt could analyze:

- **Handoff Protocols**: How does Tier 2 data flow to Judge #6?
- **Schema Compatibility**: Data format alignment
- **Performance Cascades**: Does ingestion latency affect validation?
- **End-to-End Quality**: Combined coverage and accuracy metrics

**Sample Integration Prompt**:
```
Analyze the end-to-end data flow from Gemini Ingestion Layer (collection)
to Judge #6 (validation):

1. Data handoff protocol (format, schema, timing)
2. Quality preservation (does scoring degrade?)
3. Latency budget (45-min ingestion + 90ms validation)
4. Error propagation (how do ingestion failures affect validation?)

Confidence target: ≥65% (pre-production, multi-system)
```

## GKE Deployment Considerations

### Runtime Target: ~45 Minutes/Night

**Optimization Strategies**:
1. **Parallelization**:
   - Concurrent GitHub repo flattening (3-5 repos simultaneously)
   - Multi-threaded arXiv downloads
   - Asynchronous API calls with rate limiting

2. **Resource Allocation**:
   ```yaml
   resources:
     requests:
       cpu: "1000m"
       memory: "2Gi"
     limits:
       cpu: "2000m"
       memory: "4Gi"
   ```

3. **Persistent Storage**:
   - SQLite database on persistent volume claim
   - Cached robots.txt entries (24-hour TTL)
   - Flattened repo storage for incremental updates

### Cost Model: ~$77/Month

**Breakdown**:
- **Claude API**: ~$0.50-2.00/run × 30 runs = $15-60/month
- **GKE Compute**: ~$10-15/month (small node, nightly runs)
- **Storage**: ~$2/month (100GB persistent disk)

**Sensitivity Analysis**:
- 2x item volume → ~$120/month (still economical)
- 3x volume → Consider cost caps or sampling strategies

### Quality Focus: Relevance, Timeliness, Completeness

**Evaluation Framework**:
```python
QUALITY_METRICS = {
    "relevance": {
        "metric": "JR Engine score distribution",
        "target": "≥40% Tier 1-2 items",
        "measurement": "Purpose alignment + technical merit"
    },
    "timeliness": {
        "metric": "Data freshness",
        "target": "≤7 days old (arXiv, GitHub)",
        "measurement": "Publication date vs. ingestion date"
    },
    "completeness": {
        "metric": "Source coverage",
        "target": "All 5 sources active",
        "measurement": "Items per source > 0"
    }
}
```

## Next Steps

### Iteration Roadmap

1. **Phase 1: Local Testing** (Current)
   - Validate ethical crawling on sample domains
   - Tune JR Engine scoring weights
   - Establish baseline tier distributions

2. **Phase 2: GKE Deployment** (Next)
   - Deploy CronJob to GKE cluster
   - Implement persistent storage
   - Configure secret management
   - Monitor 45-min runtime target

3. **Phase 3: Production Analysis** (Future)
   - Run Gemini 2.0 Pro analysis on production metrics
   - Increase confidence target to 70%+
   - Integrate with Judge #6 for end-to-end evaluation
   - Add visualization dashboards

4. **Phase 4: Optimization** (Ongoing)
   - Address edge cases discovered in production
   - Expand source coverage (Reddit, Stack Overflow)
   - Fine-tune tier thresholds based on user feedback
   - Explore cost reduction opportunities

### Deployment Checklist

Before running Gemini analysis prompt:

- [ ] Architecture diagrams available (GKE topology, data flow)
- [ ] Configuration files documented (config.py, Kubernetes manifests)
- [ ] Ethical compliance specs detailed (robots.txt, rate limits)
- [ ] Cost model validated (~$77/month sustainable)
- [ ] Tier classification logic documented
- [ ] Multi-source coverage targets defined
- [ ] Sample test data prepared (for dry runs)

### Success Criteria

**Analysis Quality**:
- ✓ Confidence ≥60% on all major analysis areas
- ✓ Actionable recommendations for optimization
- ✓ Edge case identification (≥5 failure scenarios)
- ✓ Cost sensitivity insights (2x/3x volume impacts)

**Deployment Readiness**:
- ✓ GKE resource specs optimized (based on Gemini recommendations)
- ✓ Ethical compliance verified (no legal risks flagged)
- ✓ Runtime target achievable (≤45 minutes projected)
- ✓ Integration points validated (4 namespace services)

## Conclusion

The Gemini Ingestion Layer Analysis Prompt represents a strategic adaptation of the Judge #6 framework, tailored for **proactive intelligence collection** rather than reactive validation. By emphasizing ethical crawling, multi-source diversity, and tier-based prioritization, this prompt enables comprehensive pre-production evaluation of the PNKLN Core Stack's foundational data layer.

**Key Takeaways**:
1. **Context matters**: Collection vs. enforcement requires different metrics
2. **Confidence calibration**: Pre-prod specs justify lower bars (60% vs. 70%)
3. **Holistic analysis**: Ethics + cost + quality > raw speed
4. **Iterative refinement**: Post-deployment data will improve future analyses

**Ready for execution** with Gemini 2.0 Pro. Awaiting production deployment data for Phase 3 iteration.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Status**: Ready for Gemini 2.0 Pro Execution
**Next Review**: Post-GKE deployment (Phase 3)
