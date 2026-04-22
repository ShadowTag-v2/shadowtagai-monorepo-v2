# Gemini Ingestion Layer Analysis Prompt

**Version:** 1.0 (Evolved from Judge 6 v1.0)
**Target Model:** Gemini 2.0 Pro
**Confidence Threshold:** ≥60% (Pre-Production)
**Last Updated:** 2025-11-15

---

## Executive Summary

You are analyzing the **Gemini Ingestion Layer**, an intelligent data collection pipeline within the PNKLN Core Stack™. This system runs nightly as a GKE CronJob to ingest ~10,000 items/day from multiple sources (YouTube, Twitter, News, Reddit, RSS), classify them into quality tiers, and deliver morning intelligence briefings to 4 downstream namespaces.

**Your Role:** Perform a comprehensive technical analysis covering architecture, quality gates, ethical compliance, cost efficiency, and integration patterns. Output a structured report with confidence scores for each finding.

---

## System Context

### Architecture Overview

- **Deployment:** GKE CronJob (daily at 2 AM UTC)
- **Runtime:** Multi-container pod (Python 3.11 + Prometheus sidecar)
- **Storage:** GCS bucket (`pnkln-ingestion-data`, 90-day retention) + BigQuery
- **AI Model:** Gemini 2.5 Flash-Lite (cost-optimized: $0.10/$0.40 per million tokens)
- **Orchestration:** Async Python (aiohttp, asyncio) with 5 source adapters

### Key Metrics (Pre-Production Targets)

| Metric | Target | Minimum/Maximum | Rationale |
|--------|--------|-----------------|-----------|
| **Daily Items** | 10,000 | 8,000 min | Volume for downstream intelligence |
| **Unique Sources** | 5+ | — | Diversity prevents bias |
| **Cost/Item** | $0.001 | $0.002 max | Sustainable economics at scale |
| **Relevance Score** | 60%+ | — | Pre-prod threshold (70% in prod) |
| **Timeliness** | 90% <24h | — | Fresh intelligence |
| **Completeness** | 85%+ | — | Usable metadata fields |
| **Runtime** | 45 min | 60 min max | Nightly batch window |

### Integration Points

- **Upstream Callers:** 4 namespaces (intelligence, analytics, reporting, api-gateway)
- **Downstream Outputs:** Morning briefings (Markdown), BigQuery tables, GCS artifacts
- **Cross-Service:** Consumed by analytics dashboards, enforcement layers (e.g., Judge 6)

### Monthly Cost Model

- **Total:** ~$77/month
  - Gemini API: ~$50
  - GKE compute: ~$15
  - GCS storage: ~$5
  - BigQuery: ~$5
  - Networking: ~$2

---

## Analysis Framework

### 1. Architecture & Design (20% weight)

**Focus Areas:**

- **Multi-Container Orchestration:** Analyze main app + Prometheus sidecar interaction in GKE. How does metrics collection handle CronJob failures?
- **Async Patterns:** Evaluate aiohttp concurrency for 5 sources. Are rate limits per-domain sufficient? Any potential deadlocks?
- **Storage Strategy:** Review GCS (raw data) + BigQuery (analytics) split. Does 90-day retention align with compliance needs?
- **AI Model Selection:** Justify Gemini 2.5 Flash-Lite vs. Pro. Does cost-performance trade-off hold at 10K items/day?

**Deliverables:**

- Architecture diagram assessment (if provided)
- Scalability bottleneck identification
- Failure mode analysis (source outages, API rate limits, GKE pod evictions)

**Confidence Target:** ≥60% (limited by lack of production telemetry)

---

### 2. Ethical Compliance Model (15% weight)

**Focus Areas:**

- **robots.txt Compliance:** Verify crawling logic honors disallow directives. How are changes detected?
- **Rate Limiting:** Token bucket algorithm (60 RPM default). Is per-domain tracking granular enough for CDN-backed sites?
- **Transparency:** User-Agent string `PNKLN-Gemini-Ingestion/0.1.0 (+https://pnkln.ai/bot)`. Does the linked page explain opt-out?
- **Timeout Handling:** 30-second request timeout. How are partial responses or retries managed?

**Deliverables:**

- Compliance scorecard (robots.txt, rate limiting, transparency)
- Risk assessment for legal exposure (GDPR, CCPA, CFAA)
- Recommendations for ethical improvements

**Confidence Target:** ≥65% (specifications should detail policies)

---

### 3. Multi-Source Coverage Analysis (15% weight)

**Focus Areas:**

- **Source Diversity:** 5 sources (YouTube, Twitter, News, Reddit, RSS). Are API quotas/costs balanced?
- **Bias Detection:** Does reliance on English-language Twitter introduce geographic/cultural bias?
- **Fallback Mechanisms:** If one source fails, how does the system compensate to hit 8K minimum items?
- **Extensibility:** How easy is adding new sources (e.g., LinkedIn, academic databases)?

**Deliverables:**

- Source contribution breakdown (estimated items/day per source)
- Bias risk matrix (language, region, topic)
- Expansion roadmap for additional sources

**Confidence Target:** ≥60% (based on code structure + API docs)

---

### 4. Tier Classification Metrics (20% weight)

**Focus Areas:**

- **Tier Definitions:**
  - **Tier 1 (30% target):** Reuters, AP, BBC, Bloomberg, Nature, Science, ArXiv, .gov
  - **Tier 2 (50% target):** TechCrunch, Wired, Ars Technica, reputable industry blogs
  - **Tier 3 (20% max):** Social media, UGC, unverified sources
- **Classification Logic:** Gemini 2.5 Flash-Lite with 60% confidence threshold. How are edge cases (e.g., BBC tweet vs. BBC article) handled?
- **Distribution Validation:** What happens if Tier 3 exceeds 20%? Auto-throttling or just warnings?
- **Cost Impact:** At $0.10/$0.40 per million tokens, is per-item classification cost <$0.0005?

**Deliverables:**

- Tier accuracy assessment (if test data available)
- Mis-classification risk analysis (false Tier 1 assignments)
- Cost-per-classification breakdown

**Confidence Target:** ≥55% (pre-prod, no ground truth data yet)

---

### 5. Quality Gates Evaluation (20% weight)

**The 7 Gates:**

1. **Items Volume:** 10K target / 8K minimum
2. **Source Diversity:** ≥5 unique sources
3. **Cost Efficiency:** $0.001 target / $0.002 max per item
4. **Relevance Score:** ≥60% average (Gemini-assessed)
5. **Timeliness:** 90% within 24 hours of publication
6. **Completeness:** ≥85% metadata fields populated (title, source, URL, timestamp, summary)
7. **Runtime Efficiency:** 45 min target / 60 min max

**Focus Areas:**

- **Gate Interdependencies:** Does prioritizing cost (Gate 3) degrade relevance (Gate 4)?
- **Failure Policies:** Which gates are hard stops vs. warnings? Can a run succeed with 7K items if relevance is 70%?
- **Measurement Accuracy:** How is "relevance" computed pre-prod without user feedback?

**Deliverables:**

- Gate-by-gate feasibility analysis
- Trade-off recommendations (e.g., relax timeliness to improve completeness)
- Monitoring dashboard suggestions

**Confidence Target:** ≥60%

---

### 6. AM Briefing Delivery Effectiveness (10% weight)

**Focus Areas:**

- **Content Curation:** Top 10 Tier 1 + Top 5 Tier 2 items. How is "top" determined (recency, engagement, Gemini score)?
- **Format:** Markdown output. Does it render well in target platforms (Slack, email, web dashboards)?
- **Delivery Mechanisms:** 4 namespaces. Are delivery failures retried? Logged?
- **User Feedback Loop:** How will briefing quality be measured post-launch (click-through, dwell time)?

**Deliverables:**

- Sample briefing review (format, clarity, actionability)
- Delivery reliability assessment
- Feedback integration plan

**Confidence Target:** ≥65% (format specs should be clear)

---

## Output Requirements

### Report Structure

```markdown
# Gemini Ingestion Layer Analysis Report
**Analyst:** Gemini 2.0 Pro
**Analysis Date:** [YYYY-MM-DD]
**Overall Confidence:** [XX%]

## 1. Executive Summary
[2-3 paragraphs: key findings, critical risks, go/no-go recommendation]

## 2. Architecture & Design (Confidence: XX%)
### Findings
- [Finding 1 with evidence from specs/code]
- [Finding 2...]

### Recommendations
- [Actionable improvement 1]
- [Actionable improvement 2]

### Risks
- [Risk 1 with severity: Critical/High/Medium/Low]

## 3. Ethical Compliance Model (Confidence: XX%)
[Same structure as above]

## 4. Multi-Source Coverage (Confidence: XX%)
[Same structure]

## 5. Tier Classification (Confidence: XX%)
[Same structure]

## 6. Quality Gates (Confidence: XX%)
[Same structure]

## 7. AM Briefing Delivery (Confidence: XX%)
[Same structure]

## 8. Cross-Cutting Concerns
### Integration Handoffs
[Analysis of interactions with Judge 6, analytics, etc.]

### Cost Sensitivity Analysis
[What if item volume doubles? API price increases?]

### Failure Mode Testing
[Resilience to source outages, GKE disruptions, API quota exhaustion]

## 9. Readiness Assessment
| Category | Status | Blocker Count | Notes |
|----------|--------|---------------|-------|
| Architecture | Green/Yellow/Red | X | [Brief note] |
| Ethics | ... | ... | ... |
| Coverage | ... | ... | ... |
| Classification | ... | ... | ... |
| Quality Gates | ... | ... | ... |
| Briefing | ... | ... | ... |

**Overall:** Ready for Production / Needs Minor Fixes / Major Rework Required

## 10. Next Steps
1. [Immediate action item 1]
2. [Monitoring setup recommendation]
3. [Post-launch validation plan]
```

### Visualization Requests

Where applicable, output tables or ASCII diagrams:

- **Tier Distribution Chart:** `[Tier 1: 30%] [Tier 2: 50%] [Tier 3: 20%]`
- **Cost Breakdown:** Table of per-component monthly costs
- **Source Contribution:** Estimated items/day per source

---

## Comparison to Judge 6 (Context)

For reference, this prompt evolved from the Judge 6 analysis prompt. Key differences:

| Aspect | Judge 6 (Validation System) | Gemini Ingestion Layer |
|--------|------------------------------|------------------------|
| **Role** | Reactive enforcement (downstream) | Proactive collection (upstream) |
| **Architecture** | Hybrid Gemini+PyTorch | GKE CronJob multi-container |
| **Key Metrics** | Latency (p99 ≤90ms), Throughput, Block Rate | Items/day, Sources, Cost/item, Scores |
| **Performance** | Real-time (<100ms) | Batch (~45 min/night) |
| **Integration** | Calls 4 namespace services | Called by 4 namespace services |
| **Quality Focus** | False Positive/Negative rates, 98% coverage | Relevance, Timeliness, Completeness |
| **Unique Features** | ATP 5-19 compliance, JR validation | Ethical crawling, Tier classification |
| **Cost Model** | Per-API-call pricing | Monthly operational (~$77) |
| **Confidence** | ≥70% (production data available) | ≥60% (pre-prod, specs-only) |

This context helps you understand the ingestion layer as **foundational** to the PNKLN stack, feeding validated intelligence to enforcement layers like Judge 6.

---

## Analysis Guidelines

### Confidence Calibration

- **70-100%:** Production data or detailed specs with test results
- **60-69%:** Specifications + architecture docs (pre-prod baseline)
- **50-59%:** Partial documentation, inferred from code
- **<50%:** Speculation or missing critical info (flag as assumption)

**For this analysis:** Aim for ≥60% overall. If certain areas lack documentation, state assumptions explicitly.

### Edge Case Probing

Stress-test the system conceptually:

- **Source Outage:** What if Twitter API goes down for 6 hours during the run?
- **Cost Spike:** What if Gemini pricing doubles overnight?
- **Volume Surge:** Can the system handle 50K items/day without code changes?
- **Tier Collapse:** What if 80% of items are classified as Tier 3?

### Integration Analysis

Since this feeds Judge 6 and other services:

- **Data Contracts:** Are output schemas versioned? Breaking changes handled?
- **Latency Tolerance:** Can analytics wait 2 AM for fresh data, or need real-time?
- **Backfill Strategy:** If a run fails, how is the gap filled?

---

## Input Materials

When conducting the analysis, reference the following (provided separately):

1. **`ARCHITECTURE.md`** - System design documentation
2. **`src/gemini_ingestion_layer/`** - Source code (main.py, sources/, classification/, quality/, etc.)
3. **`k8s/cronjob.yaml`** - GKE deployment configuration
4. **`requirements.txt`** - Dependencies and versions
5. **`tests/`** - Unit tests for classification and quality gates
6. **`README.md`** - Quick-start and operational overview
7. **(Optional) Diagrams** - Architecture flowcharts, data pipelines

If any materials are missing, note the gap and adjust confidence scores accordingly.

---

## Success Criteria

This analysis is successful if it:

1. **Identifies 3+ critical risks** with mitigation strategies
2. **Validates cost model** accuracy (is $77/month realistic at 10K items/day?)
3. **Assesses ethical compliance** as Green/Yellow/Red
4. **Evaluates tier classification** accuracy and cost-effectiveness
5. **Provides actionable next steps** for pre-prod → prod transition
6. **Maintains ≥60% confidence** across all sections

---

## Iteration Notes

### Suggested Refinements Post-Analysis

- **Test Runs:** Validate on dummy specs to calibrate output quality
- **Visualization:** Add Mermaid diagrams or tables for tier distributions
- **Combined Analysis:** Cross-reference with Judge 6 analysis to map end-to-end data flow
- **Feedback Loop:** Incorporate production telemetry once available to bump confidence to ≥70%

---

## Appendix: PNKLN Core Stack Integration

The Gemini Ingestion Layer is one component in a broader intelligence pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    PNKLN Core Stack™                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Gemini Ingestion Layer] ──► [Storage (GCS/BigQuery)]     │
│         │                              │                    │
│         │                              ▼                    │
│         │                    [Analytics Namespace]          │
│         │                              │                    │
│         └──────────────────► [Judge 6 (Validation)]        │
│                                        │                    │
│                                        ▼                    │
│                              [API Gateway Namespace]        │
│                                        │                    │
│                                        ▼                    │
│                              [Intelligence Namespace]       │
│                                        │                    │
│                                        ▼                    │
│                              [Reporting Namespace]          │
│                                        │                    │
│                                        ▼                    │
│                              [AM Briefing Delivery]         │
└─────────────────────────────────────────────────────────────┘
```

**Your analysis should consider:**

- How ingestion quality cascades to downstream accuracy
- Whether Judge 6's validation needs match ingestion's output schema
- If analytics can detect ingestion drift (e.g., source bias creep)

---

## License & Attribution

This prompt is part of the PNKLN Core Stack™ internal documentation.
Evolved from Judge 6 Analysis Prompt v1.0 (2025-Q4).
Maintained by: PNKLN Architecture Team
Contact: <redacted@shadowtag-v4.local> (example - update as needed)

---

**Ready for Execution:** Yes
**Recommended Model:** Gemini 2.0 Pro (2M token context window)
**Estimated Analysis Time:** 15-30 minutes (depending on documentation depth)
**Output Format:** Markdown report (8-12 pages)
