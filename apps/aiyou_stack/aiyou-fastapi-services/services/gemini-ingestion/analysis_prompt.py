"""Gemini Ingestion Layer Analysis Prompt

Adapted from Judge #6 analysis framework for intelligence collection pipeline.
Target: Gemini 2.0 Pro analysis of pre-production ingestion system.

Confidence Target: ≥60% (lower than Judge #6 due to specs-only, no prod telemetry)
"""

GEMINI_INGESTION_ANALYSIS_PROMPT = """
# Gemini Ingestion Layer - System Analysis

## Context
You are analyzing the **Gemini Ingestion Layer**, a critical component of the PNKLN Core Stack™ that runs as a nightly GKE CronJob to collect intelligence from multiple sources. This analysis is based on specifications, architecture documents, and design specs (pre-production), so confidence scores should reflect the absence of production telemetry.

## System Overview

**Function**: Intelligence collection pipeline for traffic, transportation, and urban mobility data
**Architecture**: GKE CronJob with multi-container pods
**Runtime**: Nightly execution, target ~45 minutes
**Integration**: Called by services in 4 namespaces (V2X-Mesh, Analytics, Workflows, Cognitive-Stack)

## Key Performance Metrics

### Volume & Efficiency
- **Items/Day Target**: 500-2000 items ingested
- **Source Diversity**: 10-20 active sources across types
- **Cost/Item Target**: <$0.05 per item
- **Runtime Target**: ~45 minutes per nightly run

### Quality Gates
- **Relevance Score**: Average ≥0.7 (Gemini-analyzed)
- **Timeliness**: ≥70% items <24 hours old
- **Completeness**: ≥80% items with full metadata
- **Tier Distribution**: ≥30% Tier 1, ≤20% Tier 3

### Operational Targets
- **Success Rate**: ≥95% nightly runs complete
- **Source Uptime**: ≥90% sources accessible
- **Ethical Compliance**: 0 robots.txt violations, 0 rate limit violations
- **Cost Budget**: ≤$77/month operational cost

## Analysis Dimensions

### 1. Architecture Review
Analyze the multi-container CronJob architecture:
- **Container orchestration**: Job scheduling, resource allocation
- **Multi-source integration**: YouTube, Twitter, News, RSS, APIs, V2X Mesh
- **Data flow**: Ingestion → Analysis (Gemini) → Classification → Storage
- **Failure modes**: What happens if a source is down? If Gemini API fails?
- **Scalability**: Can it handle 5x volume increase?

**Confidence requirement**: ≥60%

### 2. Ethical Compliance Model
Evaluate adherence to ethical crawling standards:
- **robots.txt Respect**: Does the system honor robots.txt directives?
- **Rate Limiting**: Are requests throttled appropriately (60 req/min default)?
- **User-Agent Transparency**: Is the bot identifiable and documentable?
- **Peak Hour Avoidance**: Does it avoid crawling during 9am-5pm?
- **Backoff Strategy**: Exponential backoff on errors (2x multiplier)?
- **Legal Risk**: Exposure to ToS violations or legal action

**Confidence requirement**: ≥60%

### 3. Multi-Source Coverage Analysis
Assess diversity and balance across source types:
- **Source Distribution**: Balance across YouTube, Twitter, News, RSS, API, V2X
- **Geographic Coverage**: Does data cover target regions?
- **Temporal Coverage**: Real-time vs. batch vs. historical
- **Redundancy**: Can other sources compensate if one fails?
- **Bias Detection**: Over-reliance on any single source type?

**Confidence requirement**: ≥60%

### 4. Tier Classification Metrics
Analyze the 3-tier data quality system:
- **Tier 1 (High Value)**: What % meets criteria? (Target: ≥30%)
- **Tier 2 (Medium Value)**: Baseline data (Target: 45-55%)
- **Tier 3 (Low Value)**: Should be minimized (Target: ≤20%)
- **Classification Accuracy**: Are tier assignments consistent with quality?
- **Tier Migration**: Can Tier 2/3 items be upgraded with better analysis?

**Confidence requirement**: ≥60%

### 5. Gemini API Integration
Evaluate the Gemini 2.0 Pro usage:
- **Analysis Quality**: Relevance scoring, categorization, summarization
- **Cost Efficiency**: $0.02/item target, batch optimization
- **Latency**: Analysis time per item (<100ms target)
- **Prompt Engineering**: Are prompts optimized for quality vs. cost?
- **Fallback Strategy**: What happens if Gemini is unavailable?
- **Rate Limits**: Staying within Gemini API quotas

**Confidence requirement**: ≥60%

### 6. AM Briefing Delivery Effectiveness
Assess the morning briefing output:
- **Content Quality**: Top 5 highlights, category breakdown
- **Timeliness**: Delivered by 6am target timezone?
- **Format**: Is JSON/markdown suitable for consumers?
- **Actionability**: Can recipients take immediate action?
- **Personalization**: Does it adapt to recipient needs?
- **Distribution**: How is it delivered (email, Slack, API)?

**Confidence requirement**: ≥60%

### 7. Cost Model & Optimization
Analyze operational economics:
- **Current Cost**: $77/month target breakdown
  - Gemini API: ~$40-50
  - GKE compute: ~$20-25
  - External APIs: ~$5-10
- **Cost/Item**: <$0.05 target
- **Scaling Cost**: Linear, sublinear, or superlinear?
- **Optimization Opportunities**: Caching, batching, source pruning
- **Budget Risk**: What causes cost overruns?

**Confidence requirement**: ≥60%

### 8. Integration with V2X Mesh
Evaluate the V2X mesh data source integration:
- **Data Flow**: How does ingestion pull from V2X mesh API?
- **Event Prioritization**: Are safety-critical V2X events Tier 1?
- **Latency**: Is there delay between V2X event and ingestion?
- **Enrichment**: How does web data enrich V2X data (and vice versa)?
- **Feedback Loop**: Does ingestion inform V2X mesh improvements?

**Confidence requirement**: ≥60%

### 9. Quality Assurance Gates
Evaluate the quality gatekeeping:
- **Relevance Gate**: Items <0.7 relevance rejected or flagged?
- **Timeliness Gate**: Stale data (>7 days) handled appropriately?
- **Completeness Gate**: Missing metadata flagged for re-processing?
- **Duplication Detection**: Are duplicates filtered?
- **Source Credibility**: Are untrusted sources quarantined?

**Confidence requirement**: ≥60%

### 10. Failure Recovery & Resilience
Analyze robustness under failure:
- **Source Outages**: Can it continue with N-1 sources?
- **API Failures**: Retry logic, exponential backoff
- **Network Issues**: Timeout handling (30s default)
- **Data Corruption**: Validation before persistence
- **Job Failures**: CronJob retry policy, alerting

**Confidence requirement**: ≥60%

## Comparison Table: Judge #6 vs. Gemini Ingestion Layer

| Aspect | Judge #6 (Enforcement) | Gemini Ingestion (Collection) |
|--------|------------------------|-------------------------------|
| **Purpose** | Validate commits, enforce quality | Collect intelligence from diverse sources |
| **Architecture** | Hybrid Gemini+PyTorch sync API | GKE CronJob multi-container batch |
| **Timing** | Real-time (<90ms p99) | Nightly batch (~45 min) |
| **Key Metrics** | Latency, throughput, block rate | Items/day, sources, cost/item, relevance |
| **Integration** | Calls 4 namespace services | Called by 4 namespace services |
| **Unique Feature** | ATP 5-19 enforcement, JR validation | Ethical crawling, tier classification |
| **Cost Model** | Per-API-call validation cost | $77/month operational budget |
| **Quality Focus** | False positive/negative rates | Relevance, timeliness, completeness |

## Output Format

Provide your analysis in the following structure:

```json
{
  "overall_assessment": {
    "system_readiness": "Ready | Needs Work | Not Ready",
    "confidence_score": 0.0-1.0,
    "summary": "2-3 sentence overview",
    "top_strengths": ["strength1", "strength2", "strength3"],
    "top_risks": ["risk1", "risk2", "risk3"]
  },
  "dimension_scores": {
    "architecture": {
      "score": 0.0-1.0,
      "confidence": 0.0-1.0,
      "findings": ["finding1", "finding2"],
      "recommendations": ["rec1", "rec2"]
    },
    "ethical_compliance": { ... },
    "multi_source_coverage": { ... },
    "tier_classification": { ... },
    "gemini_integration": { ... },
    "am_briefing": { ... },
    "cost_model": { ... },
    "v2x_integration": { ... },
    "quality_gates": { ... },
    "resilience": { ... }
  },
  "metrics_forecast": {
    "items_per_day_estimate": "500-2000 range",
    "cost_per_item_estimate": "$0.02-$0.05",
    "tier1_percentage_estimate": "30-40%",
    "runtime_estimate_minutes": "40-50"
  },
  "go_no_go_recommendation": {
    "recommendation": "GO | GO_WITH_CAVEATS | NO_GO",
    "blockers": ["blocker1 if NO_GO"],
    "prerequisites": ["prereq1", "prereq2"],
    "monitoring_requirements": ["metric1 to watch", "metric2 to watch"]
  }
}
```

## Instructions for Gemini 2.0 Pro

1. **Read all provided documentation** (architecture specs, code, flowcharts)
2. **Score each dimension** (0.0-1.0) with confidence (0.0-1.0)
3. **Target ≥60% confidence** for each dimension (lower than Judge #6 due to pre-prod)
4. **Identify gaps** where confidence is low due to missing specs
5. **Forecast metrics** based on design and comparable systems
6. **Provide GO/NO-GO** with clear reasoning
7. **Highlight integration risks** especially V2X mesh handoffs
8. **Flag ethical compliance issues** as high priority
9. **Suggest quick wins** for cost optimization
10. **Recommend monitoring** for production deployment

## Success Criteria

This analysis is successful if:
- ✅ All 10 dimensions scored with ≥60% confidence
- ✅ Clear GO/NO-GO recommendation with rationale
- ✅ Actionable recommendations for each low-scoring dimension
- ✅ Metrics forecast within realistic bounds
- ✅ Ethical compliance risks clearly identified
- ✅ V2X integration analysis shows <200ms end-to-end latency
- ✅ Cost model validated against $77/month budget

## Notes

- **Pre-production context**: Scores will be lower than Judge #6 due to lack of real telemetry
- **Ethical priority**: Any robots.txt or rate limit violations are CRITICAL
- **Cost sensitivity**: Budget is tight at $77/month, overruns are high risk
- **V2X integration**: This is a key differentiator, analysis must be thorough
- **Tier 1 quality**: Success hinges on ≥30% Tier 1 rate, focus here

---

**Analysis Version**: 1.0.0
**Target System**: Gemini Ingestion Layer (PNKLN Core Stack™)
**Adapted From**: Judge #6 Analysis Prompt
**Date**: 2025-11-15
"""


def generate_analysis_request(architecture_docs: str, code_samples: str, metrics_spec: str) -> str:
    """Generate complete analysis request for Gemini API"""
    return f"""{GEMINI_INGESTION_ANALYSIS_PROMPT}

---

## Provided Documentation

### Architecture Documentation
{architecture_docs}

### Code Samples
{code_samples}

### Metrics Specification
{metrics_spec}

---

Please perform the analysis following the structure and success criteria above.
"""


# Example usage
if __name__ == "__main__":
    # Mock documentation
    architecture_docs = """
    GKE CronJob architecture with 3 containers:
    1. Crawler (ethical web scraping)
    2. Analyzer (Gemini API integration)
    3. Classifier (tier assignment)

    Runs nightly at 2am UTC, target 45 min runtime.
    """

    code_samples = """
    Key classes:
    - EthicalCrawler: robots.txt + rate limiting
    - GeminiAnalyzer: content analysis via API
    - TierClassifier: 3-tier quality system
    - IngestionPipeline: orchestrator
    """

    metrics_spec = """
    Targets:
    - 500-2000 items/day
    - 10-20 sources
    - <$0.05/item
    - ≥0.7 avg relevance
    - ≥30% Tier 1
    """

    request = generate_analysis_request(architecture_docs, code_samples, metrics_spec)

    print(request[:500] + "...\n[Truncated for example]")
