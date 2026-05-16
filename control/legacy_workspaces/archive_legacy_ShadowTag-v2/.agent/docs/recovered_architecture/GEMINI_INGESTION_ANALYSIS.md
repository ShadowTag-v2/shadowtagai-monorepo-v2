# Gemini Ingestion Layer Analysis Prompt

**Adapted from Master Agent Framework for SHADOWTAGAI Intelligence Pipeline**

## Executive Summary

This prompt analyzes the **Gemini-powered Nightly Intelligence Ingestion Layer** - a GKE CronJob-based system that collects, classifies, and delivers AI/ML intelligence from multiple sources to power the SHADOWTAGAI Core Stack™.

**Key Metrics**:


- **Runtime**: ~45 minutes/night (target efficiency)


- **Quality Gates**: Items/day, source diversity, cost/item, relevance scores


- **Cost Model**: ~$77/month operational


- **Ethical Compliance**: robots.txt, rate limiting, transparency

**Confidence Target**: ≥60% (pre-production, spec-based analysis)

---

## 🎯 System Overview

### Architecture

**GKE CronJob Multi-Container Orchestration**


- **Scheduler**: Cloud Scheduler triggers nightly at 02:00 UTC


- **Coordinator**: Main container orchestrates data collection


- **Collectors**: Parallel containers for each source type


  - arXiv Research Papers (cs.AI, cs.LG, cs.CL, cs.DC, cs.SE)


  - Hacker News (Algolia API)


  - Reddit (PRAW API across 6 ML subreddits)


  - Papers with Code


  - GitHub Trending


- **Processors**: Embedding generation, tier classification


- **Delivery**: BigQuery insertion, GCS storage, AM briefing generation

### Integration Points

**Called BY** (Upstream Triggers):


- Cloud Scheduler (nightly cron)


- Manual triggers via Cloud Run Jobs API


- CI/CD post-deployment validation


- On-demand intelligence refresh requests

**Calls TO** (Downstream Services):


- BigQuery (metadata + search indexes)


- GCS (raw data + embeddings)


- Vertex AI (embedding generation)


- Cloud Logging (telemetry + errors)

---

## 📊 Key Performance Indicators

### Ingestion Metrics (vs. Judge #6's Latency/Throughput)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Items/Day** | 500-1,000 | Total papers + news + discussions ingested |
| **Source Coverage** | ≥5 active sources | arXiv, HN, Reddit, PwC, GitHub |
| **Cost/Item** | <$0.15 | Total monthly cost / items ingested |
| **Runtime Efficiency** | ≤45 min | p95 end-to-end execution time |
| **Error Rate** | <2% | Failed items / total attempted |
| **Relevance Score** | ≥70% | ML model confidence on Tier 1/2 items |

### Quality Gates (vs. Judge #6's 98% Coverage)



1. **Daily Items**: ≥200 items/day minimum (prevents data gaps)


2. **Source Diversity**: No single source >60% of daily volume


3. **Cost Ceiling**: <$100/month total operational cost


4. **Timeliness**: Items published within last 48 hours


5. **Completeness**: ≥95% of items have all required metadata fields


6. **Relevance**: ≥60% classified as Tier 1 or Tier 2

---

## 🔒 Ethical Compliance Model

### Crawling Standards (NEW - not in Judge #6)

**robots.txt Compliance**:


- All HTTP crawlers check and honor robots.txt


- User-Agent: `SHADOWTAGAI-Intelligence-Bot/1.0 (+https://shadowtagai.ai/bot)`


- Explicit identification in all requests

**Rate Limiting**:


- **arXiv**: 3-second delay between requests (per API guidelines)


- **Hacker News**: 1 request/second max (Algolia best practice)


- **Reddit**: 60 requests/minute (PRAW default)


- **GitHub**: 10 requests/minute (unauthenticated) or 5,000/hour (authenticated)


- **Papers with Code**: 30 requests/minute

**Transparency Requirements**:


- Public documentation of crawling behavior


- Contact email in User-Agent


- Opt-out mechanism for content owners


- GDPR-compliant data handling (no PII collection)

### Legal Safeguards



- **Fair Use**: Academic/research context for paper abstracts


- **ToS Compliance**: All APIs used within terms of service


- **Attribution**: Source URLs preserved in all ingested items


- **Copyright**: No full-text scraping, abstracts/summaries only

---

## 🌐 Multi-Source Coverage Analysis

### Source Breakdown (Target Distribution)

| Source | Daily Target | Tier 1 % | Coverage Areas |
|--------|--------------|----------|----------------|
| **arXiv** | 100-200 papers | 80% | Research papers, preprints |
| **Hacker News** | 50-100 stories | 40% | Industry news, discussions |
| **Reddit** | 50-150 posts | 30% | Community insights, trends |
| **Papers with Code** | 20-50 papers | 70% | Implementation-focused research |
| **GitHub Trending** | 10-30 repos | 50% | Emerging tools, frameworks |

### Diversity Metrics



- **Topic Distribution**: ML/AI (60%), Infrastructure (25%), Tools (15%)


- **Geographic Coverage**: US (50%), EU (25%), Asia (20%), Other (5%)


- **Language**: English (95%), multilingual support planned


- **Recency**: <24 hours (60%), 24-48 hours (30%), older (10%)

### Gap Detection

Monitor for:


- Missing critical conferences (NeurIPS, ICML, ICLR)


- Underrepresented domains (edge AI, federated learning)


- Single-source dependency risks


- Stale sources (no updates >48 hours)

---

## 🏆 Tier Classification System

### Tier Definitions (vs. Judge #6's FP/FN Rates)

**Tier 1 (High Value)**: Directly actionable intelligence


- Research papers from top conferences/authors


- Production-ready tool releases


- Major architectural shifts in tracked repos


- **Target**: 30-40% of daily volume

**Tier 2 (Medium Value)**: Context-building information


- Preprints from arXiv without peer review


- Community discussions with high engagement


- Beta releases, experimental tools


- **Target**: 40-50% of daily volume

**Tier 3 (Low Value)**: Background noise


- Low-engagement discussions


- Duplicate content from multiple sources


- Marketing/promotional content


- **Target**: 10-20% of daily volume (acceptable noise floor)

### Classification Methodology



1. **Automated Scoring** (Gemini 2.0 Pro)


   - Title + abstract → 0-100 relevance score


   - Thresholds: Tier 1 (≥70), Tier 2 (40-69), Tier 3 (<40)


2. **Source Authority Weighting**


   - arXiv + PwC: +15 points


   - HN (>100 points): +10 points


   - Reddit (>50 upvotes): +5 points


3. **Recency Bonus**


   - <12 hours: +10 points


   - 12-24 hours: +5 points


   - >48 hours: -5 points

---

## 📬 AM Briefing Delivery Effectiveness

### Briefing Structure (NEW - Intelligence Output)

**Daily Intelligence Briefing** (Delivered by 06:00 UTC):

```markdown

# SHADOWTAGAI Daily Intelligence Briefing

**Date**: {YYYY-MM-DD} | **Items**: {count} | **Tier 1**: {count}

## 🔥 Top 3 Highlights



1. [{Tier 1 item}] - {one-sentence summary}


2. [{Tier 1 item}] - {one-sentence summary}


3. [{Tier 1 item}] - {one-sentence summary}

## 📚 Research Papers ({count})

### Tier 1 Papers ({count})



- [{title}]({arxiv_link}) - {authors} - {category}
  Summary: {2-sentence summary}

### Tier 2 Papers ({count})

{condensed list}

## 📰 Industry News ({count})

### HN Top Stories



- [{title}]({link}) - {points} points, {comments} comments

### Reddit Highlights



- r/{subreddit}: [{title}]({link}) - {score} upvotes

## 🛠️ Tool Releases ({count})

{GitHub trending, Papers with Code implementations}

## 📊 Collection Metrics



- **Total Items**: {count}


- **Sources Active**: {count}/5


- **Avg Relevance**: {score}%


- **Runtime**: {minutes} min


- **Cost**: ${amount}

```

### Delivery Channels



1. **Email**: Sent to shadowtagai-intelligence@domain.com


2. **Slack**: Posted to #daily-intelligence channel


3. **BigQuery**: Stored in `intelligence.daily_briefings` table


4. **GCS**: Archived in `gs://shadowtagai-briefings/{YYYY}/{MM}/{DD}.md`

### Effectiveness Metrics



- **Open Rate**: >80% (email tracking)


- **Time to First Action**: <2 hours (Slack engagement)


- **Follow-up Queries**: ≥5/week (indicates value)


- **False Positive Reports**: <5% of Tier 1 items

---

## 🔍 Analysis Framework

### Prompt Structure for Gemini 2.0 Pro

```xml
<analysis_request>
  <system_under_analysis>Gemini Ingestion Layer - SHADOWTAGAI Intelligence Pipeline</system_under_analysis>

  <input_documents>
    <!-- Provide these for analysis -->


    - shadowtagai_intelligence/ code documentation


    - infrastructure/bigquery_schemas.sql


    - infrastructure/gcs_lifecycle_policy.json


    - aggregators/ module documentation


    - GKE CronJob manifests (when available)


    - Cost analysis spreadsheets
  </input_documents>

  <analysis_dimensions>
    <dimension name="architecture">
      <focus>Multi-container orchestration, fault tolerance, scalability</focus>
      <questions>


        - How does the system handle partial failures (e.g., Reddit down)?


        - What's the recovery strategy for interrupted jobs?


        - How does it scale with 10x data volume?
      </questions>
    </dimension>

    <dimension name="cost_efficiency">
      <focus>$/item, resource utilization, optimization opportunities</focus>
      <questions>


        - What drives the $77/month cost? (Breakdown by service)


        - Where are inefficiencies in resource usage?


        - How does cost scale with volume?
      </questions>
    </dimension>

    <dimension name="ethical_compliance">
      <focus>Crawling ethics, rate limits, legal risks</focus>
      <questions>


        - Are all rate limits properly enforced?


        - Is robots.txt compliance implemented correctly?


        - What legal risks exist in current design?
      </questions>
    </dimension>

    <dimension name="data_quality">
      <focus>Relevance, timeliness, completeness, tier distribution</focus>
      <questions>


        - How is relevance scored and validated?


        - What percentage of items are truly actionable (Tier 1)?


        - Are there systematic biases in source coverage?
      </questions>
    </dimension>

    <dimension name="operational_reliability">
      <focus>Error handling, monitoring, alerting, recovery</focus>
      <questions>


        - What happens when embedding generation fails?


        - How are transient API errors handled?


        - Is there sufficient observability for debugging?
      </questions>
    </dimension>

    <dimension name="integration_health">
      <focus>Upstream triggers, downstream consumers, data handoffs</focus>
      <questions>


        - How does the scheduler ensure exactly-once execution?


        - What SLAs do downstream services expect?


        - Are there race conditions in concurrent writes?
      </questions>
    </dimension>
  </analysis_dimensions>

  <output_requirements>
    <format>Structured analysis with confidence scores</format>
    <sections>


      1. Executive Summary (2-3 paragraphs)


      2. Architecture Assessment (confidence: X%)


      3. Cost Efficiency Analysis (confidence: X%)


      4. Ethical Compliance Review (confidence: X%)


      5. Data Quality Evaluation (confidence: X%)


      6. Operational Reliability Check (confidence: X%)


      7. Integration Health Status (confidence: X%)


      8. Top 5 Risks (prioritized by impact × likelihood)


      9. Top 5 Optimization Opportunities (prioritized by ROI)


      10. Recommended Actions (short-term vs. long-term)
    </sections>

    <confidence_threshold>
      Overall confidence ≥60% required for actionable recommendations.
      Flag areas <50% confidence for further investigation.
    </confidence_threshold>
  </output_requirements>

  <constraints>
    <pre_production>
      System not yet deployed. Analysis based on:


      - Code documentation and architecture specs


      - Planned GKE configurations


      - Estimated metrics from similar systems
      Actual performance may vary ±30%.
    </pre_production>

    <scope_limits>
      Do NOT analyze:


      - Detailed security penetration testing (requires prod access)


      - User experience of briefing consumption (no user feedback yet)


      - Long-term trend accuracy (insufficient historical data)
    </scope_limits>
  </constraints>
</analysis_request>

```

---

## 🚀 Execution Workflow

### Analysis Stages

**Stage 1: Document Ingestion** (5 min)


- Load all provided documentation


- Extract architecture diagrams


- Parse code for key patterns


- Build mental model of system flow

**Stage 2: Dimensional Analysis** (30 min)


- Evaluate each of 6 dimensions independently


- Assign confidence scores based on evidence quality


- Identify gaps requiring assumptions


- Flag contradictions or unclear specs

**Stage 3: Risk Assessment** (10 min)


- Cross-reference findings across dimensions


- Identify systemic risks (e.g., single points of failure)


- Prioritize by impact × likelihood


- Suggest mitigations

**Stage 4: Optimization Discovery** (10 min)


- Look for inefficiencies in design


- Calculate potential ROI for improvements


- Prioritize quick wins vs. strategic investments


- Consider trade-offs (cost vs. quality vs. complexity)

**Stage 5: Synthesis** (5 min)


- Aggregate confidence scores


- Generate executive summary


- Produce actionable recommendation list


- Highlight blockers to production readiness

---

## 📈 Success Criteria

### Analysis Quality

**Must Achieve**:


- ✅ Overall confidence ≥60%


- ✅ All 6 dimensions evaluated with reasoning


- ✅ ≥5 specific risks identified


- ✅ ≥5 optimization opportunities with ROI estimates


- ✅ Clear short-term (0-3 months) and long-term (3-12 months) roadmap

**Bonus Achievements**:


- 🌟 Identify cost reduction >25% without quality loss


- 🌟 Spot ethical compliance gaps before legal review


- 🌟 Find architecture simplifications reducing complexity


- 🌟 Suggest quality improvements requiring <10% cost increase

### Output Usability

**For Engineering Team**:


- Actionable, specific recommendations (not vague suggestions)


- Code-level insights where possible (e.g., "add retry logic in arxiv_aggregator.py:243")


- Trade-off analysis for each suggestion

**For Product/Business**:


- ROI estimates for optimization opportunities


- Risk prioritization with business impact


- Cost projections for scaling scenarios

**For Leadership**:


- Go/no-go recommendation for production deployment


- Key metrics to track post-launch


- Resource requirements for identified improvements

---

## 🔄 Iteration and Improvement

### Post-Deployment Refinement

Once system is in production:


1. **Confidence Boost**: Re-run analysis with real metrics → expect ≥80% confidence


2. **Metric Validation**: Compare predicted vs. actual performance


3. **Risk Retrospective**: Which identified risks materialized? Which didn't?


4. **Optimization Measurement**: Track ROI of implemented suggestions

### Continuous Analysis

**Weekly** (automated):


- Cost trend analysis


- Quality gate compliance check


- Source coverage drift detection

**Monthly** (Gemini-powered):


- Full re-analysis with updated metrics


- Emerging risk identification


- New optimization discovery

**Quarterly** (strategic):


- Architecture evolution recommendations


- Competitive intelligence integration


- Scaling roadmap updates

---

## 📝 Template Instantiation Example

### Running the Analysis

```bash

# Prepare input documents

cd /path/to/shadowtagai-intelligence-pipeline

# Generate analysis input bundle

./scripts/prepare_analysis_input.sh > analysis_input.txt

# Submit to Gemini 2.0 Pro

# (Use this prompt + analysis_input.txt as context)

# Expected output: Structured analysis report in markdown

# Save to: docs/analysis/gemini_ingestion_layer_analysis_{YYYY-MM-DD}.md

```

### Sample Output Excerpt

```markdown

# Gemini Ingestion Layer Analysis Report

**Date**: 2025-11-15
**Analyst**: Gemini 2.0 Pro (claude-sonnet-4.5-20250514)
**Overall Confidence**: 67%

## Executive Summary

The SHADOWTAGAI Intelligence Ingestion Layer demonstrates a well-architected approach to multi-source data collection with strong ethical compliance foundations. Key strengths include modular source integration, comprehensive metadata capture, and cost-efficient design. Primary concerns center on error recovery mechanisms and tier classification accuracy validation.

**Deployment Recommendation**: APPROVED with 3 critical prerequisites (see Section 10).

## 1. Architecture Assessment (Confidence: 72%)

### Strengths



- ✅ Clean separation of concerns (coordinator → collectors → processors)


- ✅ Parallel container execution reduces runtime from 90min (sequential) to 45min


- ✅ GCS + BigQuery dual storage enables both analytics and archival

### Concerns



- ⚠️ No explicit circuit breaker for failing collectors (risk: one bad source blocks entire job)


- ⚠️ Embedding generation is synchronous (risk: Vertex AI quota exhaustion halts pipeline)


- ⚠️ Missing idempotency keys for BigQuery inserts (risk: duplicate data on retries)

### Recommendations



1. **[SHORT-TERM]** Add per-collector timeout (15 min) with fallback to partial results


2. **[SHORT-TERM]** Implement exponential backoff for Vertex AI calls


3. **[MEDIUM-TERM]** Add deduplication layer using content hashes before BigQuery writes
...

```

---

## 🎓 Key Differences from Judge #6 Analysis

| Aspect | Judge #6 | Gemini Ingestion Layer |
|--------|----------|------------------------|
| **System Type** | Enforcement/Validation | Collection/Intelligence |
| **Execution Pattern** | Real-time, per-request | Batch, nightly cron |
| **Primary Metric** | Latency (p99 ≤90ms) | Runtime (≤45 min/night) |
| **Quality Focus** | FP/FN rates, coverage | Relevance, timeliness, completeness |
| **Integration** | Calls 4 namespaces | Called by 4 namespaces |
| **Cost Model** | Per-API-call | Monthly operational (~$77) |
| **Unique Concerns** | ATP compliance, prompt injection | Ethical crawling, tier classification |
| **Confidence Target** | ≥70% (prod data) | ≥60% (pre-prod specs) |

---

## 🛠️ Supporting Tools and Scripts

### Analysis Input Generator

**File**: `shadowtagai_intelligence/scripts/prepare_analysis_input.sh`

```bash
#!/bin/bash

# Generates formatted input for Gemini analysis

echo "=== SHADOWTAGAI Intelligence Pipeline - Analysis Input Bundle ==="
echo "Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

echo "## Architecture Documentation"
cat docs/architecture.md 2>/dev/null || echo "Not found"

echo -e "\n## Code Structure"
find shadowtagai_intelligence -name "*.py" -exec echo "File: {}" \; -exec head -50 {} \; | head -1000

echo -e "\n## Infrastructure Schemas"
cat shadowtagai_intelligence/infrastructure/bigquery_schemas.sql

echo -e "\n## Configuration"
cat shadowtagai_intelligence/config/repositories.yaml | head -200

echo -e "\n## Dependencies"
cat requirements.txt

echo -e "\n## Cost Estimates"
cat docs/cost_analysis.md 2>/dev/null || echo "Not yet available"

echo -e "\n=== END INPUT BUNDLE ==="

```

### Confidence Score Aggregator

**File**: `shadowtagai_intelligence/scripts/aggregate_confidence.py`

```python
#!/usr/bin/env python3

"""
Parses Gemini analysis output and computes overall confidence score.
"""
import re
import sys

def extract_confidence_scores(markdown_text):
    """Extract confidence percentages from analysis sections."""
    pattern = r'\(confidence:\s*(\d+)%\)'
    scores = [int(m) for m in re.findall(pattern, markdown_text)]
    return scores

def compute_overall_confidence(scores):
    """Weighted average: higher weight to critical dimensions."""
    if not scores or len(scores) < 6:
        return None

    # Weights: arch, cost, ethics, quality, reliability, integration
    weights = [0.20, 0.15, 0.20, 0.20, 0.15, 0.10]

    weighted_sum = sum(s * w for s, w in zip(scores[:6], weights))
    return round(weighted_sum, 1)

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        analysis_text = f.read()

    scores = extract_confidence_scores(analysis_text)
    overall = compute_overall_confidence(scores)

    print(f"Dimension Scores: {scores}")
    print(f"Overall Confidence: {overall}%")
    print(f"Status: {'✅ APPROVED' if overall >= 60 else '❌ NEEDS WORK'}")

```

---

## 📚 References and Resources

### Official Documentation



- [SHADOWTAGAI Intelligence Pipeline Docs](../README.md)


- [BigQuery Schema Reference](../shadowtagai_intelligence/infrastructure/bigquery_schemas.sql)


- [Master Agent Prompt Framework](../MASTER_AGENT_PROMPT_FRAMEWORK.md)

### Compliance Standards



- [robots.txt RFC](https://www.robotstxt.org/robotstxt.html)


- [arXiv API Terms](https://info.arxiv.org/help/api/tou.html)


- [Reddit API Rules](https://www.reddit.com/wiki/api/)


- [GDPR Data Minimization](https://gdpr.eu/data-minimization/)

### Related Analyses



- Judge #6 Validation System Analysis (internal)


- SHADOWTAGAI Core Stack™ Architecture Review (internal)


- Multi-Source Intelligence Best Practices (internal)

---

**End of Gemini Ingestion Layer Analysis Prompt**
**Version**: 1.0.0
**Last Updated**: 2025-11-15
**Confidence in This Prompt**: 85% (validated against Master Agent Framework)
