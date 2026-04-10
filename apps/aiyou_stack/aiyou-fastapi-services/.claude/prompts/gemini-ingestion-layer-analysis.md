# Gemini Ingestion Layer Analysis Prompt

## Purpose
This prompt is designed for Gemini 2.0 Pro to analyze the Gemini Ingestion Layer system architecture, performance, and operational readiness. It evolved from the Judge #6 analysis prompt, adapted for batch intelligence collection rather than real-time validation.

## Target Confidence
- **Pre-Production** (specs-only): ≥60%
- **Production** (with telemetry): ≥70%

---

## Prompt Template

```
You are an expert systems architect analyzing the **Gemini Ingestion Layer**,
a nightly batch intelligence collection system within the PNKLN Core Stack™.

## System Context

The Gemini Ingestion Layer is responsible for:
- Nightly batch collection of intelligence from multiple sources
- Ethical web crawling with robots.txt compliance
- Multi-source coverage (YouTube, Twitter, News, Academic, Regulatory)
- Tier classification (Tier 1/2/3 based on source quality)
- AM Briefing delivery preparation
- Operating within ~$77/month cost envelope

## Architecture Overview

**Deployment**: GKE CronJob with multi-container pods
**Runtime Target**: ~45 minutes per night
**Integration**: Called by services in 4 namespaces (governance, orchestration, cognitive, shadowtag)

## Analysis Framework

Please analyze the following aspects of the Gemini Ingestion Layer:

### 1. Architecture Analysis
- **Container Design**: Evaluate multi-container pod architecture
- **Resource Allocation**: GKE node sizing and optimization
- **Scheduling**: Cron timing and execution reliability
- **Fault Tolerance**: Failure recovery mechanisms
- **Scalability**: Ability to handle 2x-10x volume increases

### 2. Performance Metrics
Evaluate against these targets:
- **Runtime Efficiency**: ≤45 minutes per batch
- **Daily Items**: Minimum ingestion volume per night
- **Source Diversity**: Coverage across 5+ distinct source types
- **Cost per Item**: Within $77/month envelope
- **Quality Score**: Relevance and completeness per item

### 3. Quality Gates Assessment
Analyze compliance with:
- **Items Gate**: Sufficient daily ingestion volume
- **Sources Gate**: Multi-source coverage requirements met
- **Costs Gate**: Per-item cost sustainability
- **Scores Gate**: Relevance, timeliness, completeness thresholds

### 4. Ethical Compliance Model
Evaluate adherence to:
- **robots.txt**: Full compliance with web standards
- **Rate Limiting**: Respectful crawling patterns (requests/second)
- **Transparency**: User-agent identification clarity
- **Legal Compliance**: DMCA, copyright, fair use awareness
- **Ban Prevention**: Risk of IP blocking or service denial

### 5. Multi-Source Coverage Analysis
Assess coverage across:
- **YouTube**: Video content and metadata extraction
- **Twitter/X**: Social media intelligence collection
- **News Sources**: Journalistic content diversity
- **Academic Sources**: Research paper access
- **Regulatory Feeds**: Compliance and policy monitoring

Identify:
- Source bias or over-reliance on single platforms
- Gaps in coverage categories
- Opportunities for expansion

### 6. Tier Classification Metrics
Analyze tier distribution:
- **Tier 1**: High-value, authoritative sources (target: 20%)
- **Tier 2**: Standard quality, verified sources (target: 50%)
- **Tier 3**: Supplementary, bulk collection (target: 30%)

Evaluate:
- Classification accuracy
- Tier balance optimization
- Value concentration in Tier 1

### 7. AM Briefing Delivery Effectiveness
Assess:
- **Timeliness**: Ready by 6 AM daily
- **Format**: Clarity and actionability of summary
- **Completeness**: All priority items included
- **User Engagement**: Actionability and relevance metrics

### 8. Cost Model Analysis
Review:
- **Baseline**: $77/month operational cost
- **Scaling Sensitivity**: Cost impact of volume increases
- **Resource Optimization**: GKE node efficiency
- **API Usage**: External service call costs

### 9. Integration Points
Analyze handoffs:
- **Storage Layer**: Batch upload efficiency
- **Metadata Enrichment**: Tier and quality score attachment
- **Judge #6 Handoff**: Validation trigger mechanisms
- **Cross-namespace Communication**: Latency and reliability

### 10. Edge Cases & Resilience
Probe for:
- **Source Outages**: Handling of unavailable sources
- **Cost Spikes**: 10x volume scenario handling
- **Data Quality Degradation**: Low-quality batch detection
- **Runtime Overruns**: >45 minute batch handling
- **Partial Failures**: Container crash recovery

## Deliverables

Please provide:

1. **Executive Summary** (2-3 paragraphs)
   - Overall system health assessment
   - Key strengths and weaknesses
   - Readiness for production

2. **Detailed Analysis** (by section)
   - Findings for each of the 10 analysis areas
   - Confidence level per finding (with rationale)
   - Supporting evidence from specs/docs

3. **Optimization Recommendations** (prioritized)
   - High-impact improvements
   - Quick wins vs. long-term investments
   - Cost-benefit analysis

4. **Risk Assessment**
   - Critical risks to production deployment
   - Mitigation strategies
   - Monitoring recommendations

5. **Metrics Dashboard Recommendations**
   - Key metrics to visualize (Grafana)
   - Alert thresholds
   - Health check definitions

6. **Production Readiness Checklist**
   - Go/No-Go criteria
   - Outstanding items before launch
   - Post-launch validation plan

## Input Materials

[Attach the following to this prompt:]
- GKE CronJob YAML specifications
- Container Dockerfile(s) and architecture diagrams
- Source crawler configurations
- Tier classification rules/logic
- Cost breakdown and budget constraints
- Current performance benchmarks (if available)
- Integration API documentation

## Analysis Style

- Be specific and evidence-based
- Call out assumptions explicitly
- Use tables/charts where helpful for tier distributions
- Highlight uncertainties due to pre-production status
- Suggest data collection to increase confidence
- Focus on actionable insights

## Confidence Calibration

For pre-production analysis (specs-only):
- Target ≥60% overall confidence
- Flag areas needing production telemetry for higher confidence
- Identify which metrics can't be assessed without real data

For production analysis (with telemetry):
- Target ≥70% overall confidence
- Use actual performance data to validate specs
- Compare predicted vs. actual behavior
```

---

## Usage Instructions

### Pre-Production Analysis
1. Gather all architecture specs, diagrams, and configuration files
2. Attach to the prompt above
3. Submit to Gemini 2.0 Pro
4. Review findings with ≥60% confidence threshold
5. Address critical gaps before production deployment

### Production Analysis
1. Collect 2 weeks of production telemetry
2. Include runtime logs, metrics, cost data
3. Attach to the prompt above
4. Submit to Gemini 2.0 Pro
5. Target ≥70% confidence with real-world validation
6. Use findings for continuous improvement

### Iteration Cycle
- **Weekly**: Quick health checks on key metrics
- **Monthly**: Full analysis with optimization recommendations
- **Quarterly**: Strategic review and capability expansion planning

---

## Comparison with Judge #6 Prompt

| Aspect | Judge #6 | Gemini Ingestion Layer |
|--------|----------|------------------------|
| **Role** | Reactive Validator | Proactive Collector |
| **Timing** | Real-time (synchronous) | Batch (nightly cron) |
| **Architecture** | Hybrid Gemini+PyTorch+rules | GKE CronJob multi-container |
| **Key Metric** | Latency (p99 ≤90ms) | Runtime (~45 min/night) |
| **Quality Focus** | FP/FN rates | Relevance, timeliness, completeness |
| **Integration** | Calls services in 4 namespaces | Called by services in 4 namespaces |
| **Cost Model** | Per API call | Monthly operational (~$77) |
| **Unique Features** | ATP 5-19, JR Validation | Ethical crawling, Tier classification |
| **Coverage Gate** | 98% minimum | Multi-source diversity |
| **Confidence Target** | ≥70% (prod) | ≥60% (pre-prod), ≥70% (prod) |

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Owner**: CTO / Platform Architecture Team
**Related**: `.claude/pnkln-core-stack.md`, Judge #6 analysis prompt
