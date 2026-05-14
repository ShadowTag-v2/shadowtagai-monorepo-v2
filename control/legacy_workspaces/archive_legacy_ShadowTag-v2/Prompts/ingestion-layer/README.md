# Gemini Ingestion Layer Analysis Prompt

This directory contains analysis prompts for the **PNKLN Gemini Ingestion Layer**, a nightly batch intelligence collection pipeline running on Google Kubernetes Engine (GKE).

## Overview

### What is the Gemini Ingestion Layer?

The Gemini Ingestion Layer is PNKLN's **foundational intelligence collection component** that:
- Runs as a **GKE CronJob** overnight (~45 min runtime)
- Collects intelligence from **multiple sources** (YouTube, Twitter, News, Web)
- Classifies items into **Tier 1/2/3** based on value
- Generates **AM Briefing** summaries for stakeholders
- Operates within **$77/month** budget constraint

**Stack Position**: Upstream foundation → Feeds Judge #6 validation → Enables downstream analytics

---

## Directory Structure

```
ingestion-layer/
├── README.md                                      # This file
├── metadata/
│   └── ingestion-versions.json                    # Version registry
├── examples/
│   └── [Sample GKE specs, pipeline configs]       # Test artifacts
└── v1/
    └── gemini-ingestion-layer-analysis.md         # Main analysis prompt
```

---

## What Does This Prompt Do?

The Gemini Ingestion Layer Analysis Prompt enables **Gemini 2.0 Pro** to conduct comprehensive architectural and operational analysis of the intelligence collection pipeline.

### Analysis Capabilities

**1. Architecture Analysis**
- GKE CronJob multi-container orchestration
- Pod specs, resource allocation, scheduling
- Fault tolerance, scalability, data flow

**2. Key Metrics Analysis**
- Items/day, source diversity, cost/item
- Runtime efficiency (~45 min target)
- Tier distribution (Tier 1/2/3 balance)

**3. Integration Analysis**
- Upstream triggers (services in 4 namespaces)
- Downstream consumers (Judge #6, analytics)
- Cross-namespace communication patterns

**4. Ethical Compliance Model** ⭐ *Unique to Ingestion*
- robots.txt adherence
- Rate limiting and polite crawling
- ToS compliance (YouTube, Twitter APIs)
- Legal risk assessment (GDPR, CCPA)

**5. Multi-Source Coverage Analysis** ⭐ *Unique to Ingestion*
- Source diversity (YouTube, Twitter, News, Web)
- Bias detection (geographic, political, topic)
- Expansion opportunities

**6. Tier Classification Metrics** ⭐ *Unique to Ingestion*
- Tier 1: High-value intelligence (20-30% target)
- Tier 2: Medium-value context (50-60% target)
- Tier 3: Low-value archival (10-20% target)

**7. Cost Model Analysis**
- Monthly budget ($77) breakdown
- Cost/item efficiency
- Scalability sensitivity (2x volume impact)

**8. Quality Focus**
- Relevance (≥80% aligned with objectives)
- Timeliness (≤2h Tier 1, ≤12h Tier 2/3)
- Completeness (≥95% metadata)
- Deduplication (≥90% accuracy)

**9. AM Briefing Delivery Effectiveness** ⭐ *Unique to Ingestion*
- Content quality (Tier 1 focus, summarization)
- Timeliness (ready by 6 AM target)
- Format usability (email, Slack, dashboard)

**10. Runtime Efficiency Analysis**
- 45-minute execution target
- Bottleneck identification
- Parallelization opportunities

---

## Version History

### v1.0 (Current - Active)
**Status**: Pre-Production Analysis
**Created**: 2025-11-14
**Target Model**: Gemini 2.0 Pro
**Confidence Target**: ≥60% (realistic for specs-only analysis)

**Features**:
- 10-section comprehensive analysis framework
- Adapted from Judge #6 v2 analytical structure
- 4 new sections unique to collection pipelines
- Ethical compliance deep-dive
- Multi-source coverage evaluation
- Tier classification metrics
- AM Briefing delivery assessment

**Deployment Stage**: Pre-production (specs and docs only)

---

## Key Differences from Judge #6

This prompt is adapted from the **Judge #6 v2 framework** but tailored for intelligence collection:

| Aspect | Judge #6 | Gemini Ingestion Layer |
|--------|----------|------------------------|
| **Purpose** | Enforcement validation | Intelligence collection |
| **Operational Mode** | Real-time (ms) | Batch overnight (min) |
| **Key Metric** | p99 ≤ 90ms latency | ~45 min runtime |
| **Integration** | Calls services | Called by services |
| **Quality Focus** | False positive/negative rates | Relevance, timeliness, completeness |
| **Unique Features** | ATP 5-19 enforcement | Ethical crawling, tier classification |
| **Cost Model** | Per-operation API calls | Monthly $77 budget |
| **Confidence Target** | ≥70% (prod telemetry) | ≥60% (pre-prod specs) |

**See**: `/docs/JUDGE-6-TO-INGESTION-LAYER-COMPARISON.md` for detailed transformation analysis

---

## Usage

### Loading the Prompt

```python
from prompt_loader import load_prompt

# Load Gemini Ingestion Layer analysis prompt
prompt = load_prompt(
    component="ingestion-layer",
    version="v1"
)
```

### Running Analysis with Gemini 2.0 Pro

```python
from google.generativeai import GenerativeModel

# Initialize Gemini 2.0 Pro
model = GenerativeModel("gemini-3.1-pro")

# Load analysis prompt
with open("prompts/ingestion-layer/v1/gemini-ingestion-layer-analysis.md") as f:
    system_prompt = f.read()

# Provide GKE specs and pipeline docs as context
context = """
[GKE CronJob configuration YAML]
[Pipeline architecture diagram]
[Source integration documentation]
[Cost model spreadsheet]
"""

# Execute analysis
response = model.generate_content(
    f"{system_prompt}\n\n---\n\nANALYZE THE FOLLOWING:\n\n{context}"
)

print(response.text)
```

### Expected Output Format

```markdown
# Gemini Ingestion Layer Analysis Report

**Analysis Date**: 2025-11-14
**Analyzed Artifacts**: GKE CronJob specs, pipeline docs, cost model
**Confidence Level**: 65% (Target: ≥60%)

---

## Executive Summary
[2-3 paragraph overview]

---

## Section-by-Section Analysis

### 1. Architecture Analysis
[Strengths, Concerns, Optimization Opportunities]

### 2. Key Metrics Analysis
[Metric evaluation, missing metrics, target alignment]

[... Sections 3-10 ...]

---

## Risk Register
| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Source API quota exhaustion | HIGH | MEDIUM | Implement quota monitoring, fallback sources |

---

## Recommendations (Prioritized)
1. **CRITICAL**: Add robots.txt validation before web crawling
2. **HIGH**: Implement source diversity monitoring dashboard
3. **MEDIUM**: Optimize container resource allocation for 30-min runtime
4. **LOW**: Explore Reddit as additional Tier 1 source

---

## Open Questions
- What is the exact daily item target for production?
- Which namespace service acts as primary trigger?

---

## Appendix
[Supporting data, diagrams]
```

---

## SLA Constraints

The prompt evaluates against these pre-production targets:

| Constraint | Target | Purpose |
|------------|--------|---------|
| **Runtime** | ~45 min/night | Nightly batch window |
| **Delivery** | Ready by 6 AM | Morning briefing availability |
| **Cost** | $77/month | Operational budget |
| **Relevance** | ≥80% | Intelligence quality |
| **Completeness** | ≥95% | Metadata coverage |
| **Timeliness (T1)** | ≤2 hours | High-value freshness |
| **Timeliness (T2/3)** | ≤12 hours | Medium/low-value lag |
| **Source Diversity** | ≥4 active | Coverage breadth |

---

## Ethical Compliance Requirements

**Critical Evaluation Areas**:

✅ **robots.txt Adherence**: Respect webmaster directives, no banned paths
✅ **Rate Limiting**: Polite crawling (max 1 req/sec per domain), backoff on errors
✅ **Transparency**: Clear user-agent (`PNKLN-Crawler/1.0; +https://pnkln.ai/crawler-info`)
✅ **Legal/ToS**: YouTube API Terms, Twitter Developer Agreement compliance
✅ **Privacy**: No personal data beyond public posts, GDPR/CCPA adherence

**Risk Mitigation**: Analysis flags non-compliance risks for legal review

---

## Multi-Source Coverage

**Configured Sources**:

| Source | Type | Status | API/Crawl | Compliance |
|--------|------|--------|-----------|------------|
| **YouTube** | Video platform | Active | API | YouTube API ToS |
| **Twitter/X** | Social media | Active | API | Twitter Developer Agreement |
| **News** | RSS aggregators | Active | RSS/API | Feed terms |
| **Web** | Direct crawling | Active | HTTP | robots.txt, polite crawling |

**Analysis Focus**:
- Is coverage balanced (avoid 80% one source)?
- Are there geographic/political/topic biases?
- What sources should be added (Reddit, LinkedIn, Blogs)?

---

## Tier Classification System

**Intelligence Value Hierarchy**:

### Tier 1: High-Value (20-30% target)
- Primary sources, verified accounts
- Breaking news, strategic intelligence
- High engagement, mission-critical
- **Use**: AM Briefing headlines, strategic decisions

### Tier 2: Medium-Value (50-60% target)
- Secondary sources, credible outlets
- Analysis pieces, contextual information
- **Use**: Background research, trend analysis

### Tier 3: Low-Value (10-20% target)
- Aggregators, low-engagement posts
- Opinion blogs, archival content
- **Use**: Long-tail queries, historical context

**Analysis Task**: Evaluate tier distribution health, prevent tier drift to junk

---

## Quality Dimensions

**Replacing FP/FN Rates** (Judge #6 binary errors) with:

| Dimension | Definition | Target | Measurement |
|-----------|------------|--------|-------------|
| **Relevance** | % items aligned with objectives | ≥80% | Downstream consumer feedback |
| **Timeliness** | Lag: publication → ingestion | ≤2h (T1), ≤12h (T2/3) | Timestamp delta |
| **Completeness** | % items with required metadata | ≥95% | Field presence check |
| **Deduplication** | % duplicates identified | ≥90% | Hash matching accuracy |

---

## AM Briefing Delivery

**Output**: Morning intelligence summary from overnight collection

**Evaluation Criteria**:
- ✅ **Content Quality**: Tier 1 focus, summarization (not raw dumps)
- ✅ **Timeliness**: Ready by 6 AM PST target
- ✅ **Format**: Email/Slack/Dashboard with structured sections
- ✅ **Reliability**: Delivery success rate, partial fallback if sources fail

**Effectiveness Grade**: A/B/C/D/F based on criteria above

---

## PNKLN Stack Integration

### Position in Stack

```
PNKLN Core Stack™

┌─────────────────────────────────────┐
│   Downstream: Analytics, Dashboards │
│   (Consumers of validated intel)    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Midstream: Judge #6 Validation    │  ← Judge #6 prompt analyzes
│   (Enforces ATP 5-19, blocks/allows)│
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   UPSTREAM: Gemini Ingestion Layer  │  ← THIS PROMPT ANALYZES
│   (Collects, classifies, tiers)     │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│   Sources: YouTube, Twitter, News   │
└─────────────────────────────────────┘
```

**Upstream Dependencies**: Orchestration services in 4 namespaces (triggers)
**Downstream Consumers**: Judge #6, analytics, AM Briefing delivery

---

## Complementary Analysis

For **end-to-end PNKLN pipeline evaluation**, run both prompts:

1. **Gemini Ingestion Layer Prompt** (this) → Analyze collection
2. **Judge #6 Prompt** → Analyze validation
3. **Combined Analysis** → Evaluate handoffs, data contracts, failure propagation

**Integration Questions**:
- Does Ingestion output format match Judge #6 input?
- Are tier classifications respected by Judge #6?
- If Ingestion fails, does Judge #6 have fallback data?

---

## Next Steps

### Pre-Production (Current)
1. ✅ Prompt created and documented
2. ⏳ Test run on sample GKE CronJob specs
3. ⏳ Validate Gemini 2.0 Pro handling of ethical sections
4. ⏳ Add visualization requests (tier charts, cost breakdowns)
5. ⏳ Probe edge cases (source outages, cost spikes)

### Post-Deployment (Production)
6. Re-run analysis with real metrics (logs, dashboards, BigQuery)
7. Raise confidence target to ≥70%
8. Compare spec-based predictions to actual performance
9. Iterate on low-accuracy sections
10. Document lessons learned

### Combined Analysis
11. Run Ingestion + Judge #6 prompts together
12. Analyze handoff quality
13. Validate tier classification propagation
14. Stress-test failure scenarios

---

## References

- **Main Prompt**: `v1/gemini-ingestion-layer-analysis.md`
- **Version Registry**: `metadata/ingestion-versions.json`
- **Comparison to Judge #6**: `/docs/JUDGE-6-TO-INGESTION-LAYER-COMPARISON.md`
- **Judge #6 Prompts**: `/prompts/judge/`

---

## Contributing

When modifying Ingestion Layer prompts:

1. Create new version directory (v2/, v3/, etc.)
2. Update `metadata/ingestion-versions.json`
3. Document changes in version-specific CHANGELOG
4. Test with sample GKE specs before production
5. Validate against SLA constraints
6. Update comparison docs if framework changes

---

**Maintained by**: PNKLN Engineering / Intelligence Pipeline Team
**Target Model**: Gemini 2.0 Pro
**Last Updated**: 2025-11-14
**Status**: Active (Pre-Production)
