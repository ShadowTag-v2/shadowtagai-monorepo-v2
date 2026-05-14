# Gemini Ingestion Layer Analysis Prompt

**Target Model**: Gemini 2.0 Pro
**Analysis Type**: Pre-Production System Analysis (Specifications-Based)
**Confidence Target**: ≥60% (specs-only, no production telemetry)
**Version**: 1.0
**Date**: 2025-11-15

---

## Executive Summary Request

You are analyzing the **Gemini Ingestion Layer**, a critical upstream component in the PNKLN Core Stack™ intelligence collection pipeline. This is a **preventive, acquisitive system** that feeds high-quality data to downstream validators and processors.

Provide a comprehensive analysis covering:
1. **Architecture & Design** (GKE CronJob multi-container orchestration)
2. **Performance & Efficiency** (~45 min/night runtime target)
3. **Quality Gates** (items, sources, costs, scores)
4. **Ethical Compliance** (robots.txt, rate limiting, transparency)
5. **Multi-Source Coverage** (YouTube, Twitter, News, etc.)
6. **Tier Classification** (Tier 1/2/3 distribution)
7. **AM Briefing Delivery** (effectiveness and timeliness)
8. **Integration Points** (called by services in 4 namespaces)
9. **Cost Model** (monthly operational budget ~$77)
10. **Recommendations** (optimizations, risks, next steps)

---

## System Context

### Primary Function
**Intelligence Collection & Pre-Processing**
The Gemini Ingestion Layer is a nightly batch job that:
- Crawls multiple web sources (social media, news, forums)
- Classifies content by relevance tier (1-3)
- Validates ethical compliance (robots.txt, rate limits)
- Prepares morning briefing data for downstream consumers
- Operates as foundational data layer for PNKLN stack

### Architecture Overview
**GKE CronJob Multi-Container Design**
- **Platform**: Google Kubernetes Engine (GKE)
- **Execution**: Nightly cron job (~3:00 AM - 3:45 AM)
- **Containers**:
  - Source crawler pods (parallel execution)
  - Classification container (Gemini-based tier assignment)
  - Compliance validator (ethical checks)
  - Briefing generator (AM summary output)
- **Storage**: Cloud Storage for raw data, Cloud SQL for metadata
- **Orchestration**: Kubernetes CronJob with multi-pod coordination

### Key Performance Metrics

| Metric | Target | Measurement Period |
|--------|--------|-------------------|
| **Runtime Efficiency** | ~45 min/night | Daily batch window |
| **Daily Items Ingested** | 500-2000 items | Per execution |
| **Source Diversity** | ≥8 active sources | Per night |
| **Cost per Item** | ≤$0.04 | Monthly average |
| **Tier 1 Ratio** | ≥30% | High-value content |
| **Compliance Rate** | 100% | robots.txt adherence |
| **Briefing Delivery** | 6:00 AM ±10 min | Daily deadline |

### Integration Points
**Called By Services in 4 Namespaces:**
1. **AutoGen Namespace**: Triggers nightly execution, consumes briefing data
2. **Cognitive Namespace**: Requests on-demand re-crawls for specific sources
3. **ShadowTag Namespace**: Watermarking service for ingested content provenance
4. **AiyouJr Namespace**: Core intelligence consumer for downstream processing

**Upstream Position**: Foundational layer - provides data to all downstream validators (including Judge #6)

### Unique Features
1. **Ethical Crawling Framework**
   - robots.txt compliance checker
   - Adaptive rate limiting per source
   - Attribution tracking for all content
   - GDPR/privacy-aware data handling

2. **Tier Classification System**
   - **Tier 1**: High-value, actionable intelligence (priority sources)
   - **Tier 2**: Relevant but lower priority (background context)
   - **Tier 3**: Low-value or noise (filtered but retained for completeness)
   - Gemini 2.0 Pro used for dynamic tier assignment

3. **Multi-Source Coverage**
   - YouTube (video metadata, comments)
   - Twitter/X (trending topics, key accounts)
   - News aggregators (RSS feeds, APIs)
   - Reddit (targeted subreddits)
   - Hacker News, specialized forums
   - Configurable source priority matrix

4. **AM Briefing Pipeline**
   - Summarizes top Tier 1 items
   - Highlights emerging patterns
   - Delivers via email/API by 6:00 AM
   - Customizable recipient groups

### Cost Model
**Monthly Operational Budget: ~$77**
- **GKE Compute**: ~$45/month (preemptible nodes, nightly 45min runtime)
- **API Costs**: ~$20/month (Gemini API for tier classification)
- **Storage**: ~$8/month (Cloud Storage + Cloud SQL)
- **Networking**: ~$4/month (egress for crawling)

**Scaling Sensitivity**:
- If item volume doubles (1000 → 2000/night), costs rise to ~$110/month
- Cost per item decreases with scale (economies of scale in GKE)

### Quality Focus
**Holistic Data Quality Over Speed**

| Dimension | Target | Measurement |
|-----------|--------|-------------|
| **Relevance** | ≥85% Tier 1+2 | Downstream consumer feedback |
| **Timeliness** | <24 hours old | Timestamp validation |
| **Completeness** | All sources checked | Source availability matrix |
| **Accuracy** | Correct attribution | Metadata validation |
| **Diversity** | ≥8 sources/night | Source coverage report |

**Quality Gates (replaces Judge #6's 98% coverage):**
- **Items Gate**: 500-2000 items/night (blocks if <500 or >3000)
- **Sources Gate**: ≥8 sources active (alerts if <6)
- **Cost Gate**: ≤$0.05/item (alerts if exceeded)
- **Scores Gate**: ≥30% Tier 1 (rebalances source weights if <20%)

---

## Analysis Request

### 1. Architecture & Design Analysis
**Based on pipeline documentation and architecture specifications:**

- Evaluate the GKE CronJob multi-container design
  - Is the container separation (crawler/classifier/validator/generator) optimal?
  - Are there single points of failure in the orchestration?
  - How does fault tolerance handle partial source failures?

- Assess resource allocation strategy
  - Is the 45-minute runtime window realistic for 500-2000 items?
  - Can parallel crawler pods scale efficiently?
  - What's the risk of cost overruns with variable data volumes?

- Review integration architecture
  - How cleanly does it interface with 4 downstream namespaces?
  - Are API contracts well-defined for briefing delivery?
  - What happens if AM briefing misses 6:00 AM deadline?

**Confidence Requirement**: Flag assumptions where specs are unclear (≥60% confidence target).

### 2. Performance & Efficiency Review
**Runtime Target: ~45 min/night**

- Analyze batch processing efficiency
  - What are bottlenecks in the 45-minute window?
  - Can crawling be parallelized further?
  - Is Gemini API latency for tier classification a limiter?

- Evaluate resource utilization
  - Are GKE preemptible nodes risky for nightly jobs?
  - How does memory/CPU scale with item volume spikes?
  - What's the overhead from compliance checks?

- Suggest optimizations
  - Can sources be prioritized to front-load Tier 1 content?
  - Should tier classification batch multiple items per API call?
  - Are there opportunities for caching/incremental crawling?

### 3. Quality Gates Validation
**Targets: 500-2000 items, ≥8 sources, ≤$0.04/item, ≥30% Tier 1**

- Assess gate thresholds
  - Are the numeric targets (500 min, 2000 max items) evidence-based?
  - Is the ≥30% Tier 1 ratio achievable with current sources?
  - What's the tolerance for cost spikes (e.g., API rate increases)?

- Review enforcement mechanisms
  - How are gate violations detected and alerted?
  - Do gates block execution or just warn?
  - Can gates adapt to seasonal data volume changes?

- Evaluate multi-dimensional balance
  - Does optimizing for item count degrade tier quality?
  - Is there tension between source diversity and cost efficiency?
  - How are trade-offs between relevance and completeness handled?

### 4. Ethical Compliance Model
**New Section (not in Judge #6 prompt)**

- **robots.txt Compliance**
  - Is there automated checking before each source crawl?
  - How are robots.txt updates detected (cache invalidation)?
  - What's the fallback if robots.txt disallows all crawling?

- **Rate Limiting Framework**
  - Are limits adaptive per source (e.g., 1 req/sec for Twitter, 10/sec for RSS)?
  - How does the system avoid bans or throttling?
  - Is there exponential backoff for 429 errors?

- **Transparency & Attribution**
  - Is all content tagged with source URLs and timestamps?
  - Are there provenance records for downstream traceability (e.g., ShadowTag integration)?
  - How is user privacy handled (e.g., anonymizing social media handles)?

- **Legal Risk Assessment**
  - Are there regions/sources with high GDPR or copyright risk?
  - Is scraping activity logged for audit trails?
  - What's the plan if a source sends a cease-and-desist?

**Critical**: Flag any gaps in ethical safeguards that could expose PNKLN to legal liability.

### 5. Multi-Source Coverage Analysis
**Target: ≥8 active sources/night**

- **Current Source Matrix** (evaluate breadth)
  - YouTube: Video metadata, trending topics
  - Twitter/X: Key accounts, hashtag tracking
  - News: RSS feeds (AP, Reuters, BBC, etc.)
  - Reddit: Targeted subreddits (r/technology, r/worldnews, etc.)
  - Hacker News: Front page + "Ask HN"
  - Specialized forums: Security, AI research
  - Government/Public Data: APIs for official announcements
  - Academic: arXiv preprints (optional)

- **Coverage Gaps & Biases**
  - Are sources geographically diverse (US-centric vs. global)?
  - Is there over-reliance on English-language content?
  - Are niche but high-value sources missing (e.g., Telegram channels)?
  - How are new sources prioritized for addition?

- **Source Reliability Scoring**
  - Are sources pre-vetted for credibility?
  - Is there a feedback loop from downstream consumers on source quality?
  - How are low-performing sources pruned?

- **Redundancy & Resilience**
  - If 2-3 sources go offline, does the system still function?
  - Are there backup sources for critical categories (e.g., news)?
  - How quickly can new sources be onboarded?

**Recommendation**: Identify top 3 missing sources that would maximize Tier 1 yield.

### 6. Tier Classification Metrics
**Target: ≥30% Tier 1, with balanced Tier 2/3**

- **Tier Distribution Analysis**
  - What's the current ratio (Tier 1 / Tier 2 / Tier 3)?
  - Is 30% Tier 1 realistic, or aspirational?
  - Are most items clustering in Tier 2 (safe but low-value)?

- **Gemini Classification Accuracy**
  - How is tier assignment validated (ground truth labels)?
  - Are there systematic misclassifications (e.g., all Twitter flagged as Tier 3)?
  - Can tier definitions be tuned (prompt engineering for Gemini)?

- **Value vs. Volume Trade-off**
  - Should the system prioritize more Tier 1 items (quality) or total volume (completeness)?
  - Are Tier 3 items worth the crawling cost, or should they be filtered earlier?
  - How does tier distribution affect downstream consumer satisfaction?

- **Dynamic Tier Adjustment**
  - Can source weights be auto-tuned based on tier yield?
  - Should low-Tier 1 sources be temporarily deprioritized?
  - Is there a feedback mechanism from AutoGen/Cognitive namespaces on tier utility?

**Metric to Track**: "Tier 1 Yield per Source" (items/source/night) to optimize source mix.

### 7. AM Briefing Delivery Effectiveness
**Target: 6:00 AM ±10 min delivery**

- **Pipeline Reliability**
  - What's the success rate of on-time delivery (6:00 AM target)?
  - Are there failure modes (e.g., briefing generated but email fails)?
  - How are delays communicated to recipients?

- **Content Quality**
  - Is the briefing format digestible (summary + links)?
  - Do recipients actually read/act on it (engagement metrics)?
  - Are there customization options (e.g., focus areas per recipient)?

- **Timeliness vs. Completeness**
  - If the nightly job runs late (>45 min), does briefing delay or use partial data?
  - Should there be a "preliminary briefing" at 5:00 AM + "full update" at 7:00 AM?
  - How stale can data be before it's excluded from briefing?

- **Delivery Mechanisms**
  - Email: Reliability, spam filter issues?
  - API: Synchronous vs. asynchronous delivery?
  - Dashboard: Real-time vs. cached briefing view?

**Success Metric**: "Briefing Actionability Score" (% of items that trigger downstream action).

### 8. Integration Points (Upstream Position)
**Called by 4 Namespaces (AutoGen, Cognitive, ShadowTag, AiyouJr)**

- **API Contract Review**
  - Are ingestion endpoints well-documented (OpenAPI/Swagger)?
  - Do consumers poll for data, or push notifications trigger?
  - What's the SLA for on-demand re-crawls (e.g., Cognitive triggers)?

- **Data Handoff Quality**
  - Is ingested data standardized (schema, format)?
  - How is data versioning handled (v1, v2 schemas)?
  - Are there backward-compatibility guarantees for downstream consumers?

- **Cross-Namespace Dependencies**
  - If ShadowTag watermarking is slow, does it block ingestion pipeline?
  - How does AutoGen orchestration signal ingestion to start/stop?
  - What happens if AiyouJr's storage quota is full?

- **Failure Propagation**
  - If ingestion fails, do downstream services degrade gracefully?
  - Are there retry policies or dead-letter queues for failed handoffs?
  - How are downstream consumers alerted to stale data?

**Dependency Map**: Visualize how ingestion feeds into Judge #6 and other validators.

### 9. Cost Model & Scalability
**Monthly Budget: ~$77 (~$0.04/item at 500-2000 items/night)**

- **Cost Breakdown Validation**
  - Is $45/month GKE cost realistic for 45 min/night on preemptible nodes?
  - Are Gemini API costs ($20/month) based on actual item counts?
  - What's the risk of API price increases (e.g., Gemini 2.0 Pro pricing changes)?

- **Scaling Scenarios**
  - At 2000 items/night: ~$77/month (baseline)
  - At 4000 items/night: ~$110/month (doubles compute, API calls)
  - At 500 items/night: ~$60/month (fixed costs dominate)
  - What's the break-even point where economies of scale kick in?

- **Cost Optimization Opportunities**
  - Can Gemini API batching reduce per-item classification cost?
  - Are there cheaper tier classification alternatives (e.g., fine-tuned small model)?
  - Should low-value Tier 3 sources be crawled less frequently (weekly vs. nightly)?

- **Budget Alerts**
  - Are there automated alerts at 70% and 90% of monthly budget?
  - How are cost spikes (e.g., unexpected API rate hikes) detected?
  - What's the kill-switch if costs exceed $100/month?

**Risk**: Preemptible nodes may fail mid-job, requiring re-runs and doubling costs.

### 10. Recommendations & Next Steps
**Pre-Production → Production Transition**

- **High-Priority Actions** (before prod deployment)
  1. Stress-test with 3000+ items/night to validate 45-minute window
  2. Simulate source outages (e.g., Twitter API down) to test resilience
  3. Validate ethical compliance (manual audit of robots.txt checks)
  4. Benchmark Gemini tier classification accuracy (ground truth validation)
  5. Establish on-call runbooks for briefing delivery failures

- **Medium-Priority Optimizations** (first 3 months post-launch)
  1. Implement "Tier 1 Yield per Source" metric to optimize source mix
  2. Add A/B testing for tier classification prompts (improve Tier 1 ratio)
  3. Build cost sensitivity dashboard (real-time spend tracking)
  4. Integrate downstream consumer feedback loops (tier utility scoring)
  5. Explore incremental crawling to reduce redundant data fetching

- **Long-Term Strategic Enhancements** (6-12 months)
  1. Multi-region ingestion for global source coverage (EU, APAC)
  2. Real-time ingestion supplement (critical breaking news, not just nightly)
  3. Advanced tier classification (fine-tuned Gemini model on historical data)
  4. Self-healing source management (auto-prune low-yield, auto-discover new sources)
  5. Ingestion → Judge #6 end-to-end flow analysis (combined prompt)

- **Risk Mitigation**
  1. **Legal**: Formal review of robots.txt compliance with legal counsel
  2. **Cost**: Set hard budget cap at $100/month with auto-shutoff
  3. **Reliability**: Migrate from preemptible to on-demand nodes if failure rate >5%
  4. **Ethics**: Public transparency report on data sources and handling

- **Edge Cases to Test**
  - Source returns 10x normal data volume (e.g., viral event)
  - All Tier 1 sources offline simultaneously
  - Gemini API rate limit hit mid-classification
  - Briefing delivery at 8:00 AM (2 hours late) - acceptable or re-run?
  - Cost spike to $150/month due to API price increase

---

## Output Format Requested

### 1. Executive Summary (2-3 paragraphs)
- Overall health of Gemini Ingestion Layer design
- Top 3 strengths and top 3 risks
- Go/no-go recommendation for production deployment

### 2. Detailed Analysis (by section 1-9 above)
- For each section: findings, confidence level, assumptions flagged
- Use tables/charts where helpful (e.g., tier distribution, cost breakdown)
- Highlight gaps in specifications that need clarification

### 3. Prioritized Recommendations
- **Critical (do before prod)**: Must-fix issues
- **Important (do in 3 months)**: Performance/cost optimizations
- **Strategic (do in 6-12 months)**: Long-term enhancements

### 4. Comparison to Judge #6 (Optional)
- How does ingestion layer's design philosophy differ from Judge #6's enforcement model?
- Are there lessons from Judge #6 that apply here (or vice versa)?
- How do the two systems complement each other in PNKLN stack?

### 5. Questions/Clarifications Needed
- List any missing information that prevents ≥60% confidence analysis
- Suggest specific docs/metrics to review for full assessment

---

## Confidence Calibration

**Target: ≥60% confidence (specs-only, pre-production)**

This is lower than Judge #6's ≥70% because:
- No production telemetry (logs, metrics, real user feedback)
- Specs may be aspirational vs. tested
- Ethical compliance is harder to validate without live crawling data
- Tier classification accuracy unknown without ground truth

**When to flag low confidence (<60%)**:
- Cost estimates seem speculative (no actual GKE bills)
- Source coverage claims lack evidence (are all 8 sources integrated?)
- Tier distribution targets (30% Tier 1) appear arbitrary
- Briefing delivery SLA not backed by test data
- Integration contracts with 4 namespaces undefined

**How to improve confidence post-deployment**:
- Add runtime metrics (Cloud Monitoring dashboards)
- Collect tier classification accuracy data (human labelers)
- Track actual costs vs. budget (billing alerts)
- Monitor briefing engagement (open rates, click-throughs)
- Gather downstream consumer feedback (tier utility surveys)

---

## Success Criteria for This Analysis

A successful Gemini 2.0 Pro analysis will:
1. ✅ Identify ≥3 architectural risks before production deployment
2. ✅ Validate or challenge the 45-minute runtime assumption
3. ✅ Assess ethical compliance robustness (robots.txt, rate limits)
4. ✅ Recommend ≥5 specific cost optimizations
5. ✅ Evaluate tier classification strategy (30% Tier 1 target)
6. ✅ Flag ≥10 missing specification details that need clarification
7. ✅ Provide go/no-go recommendation with clear rationale
8. ✅ Suggest tests to run before prod (load, failure scenarios)
9. ✅ Compare/contrast with Judge #6 (complementary roles)
10. ✅ Maintain ≥60% confidence throughout (flag assumptions clearly)

---

## Appendix: Key Differences from Judge #6 Analysis Prompt

| Dimension | Judge #6 (Enforcement) | Gemini Ingestion Layer (Collection) |
|-----------|------------------------|-------------------------------------|
| **Primary Function** | Validate/block content in real-time | Crawl/classify content in batch |
| **Architecture** | Hybrid Gemini + PyTorch (3-layer) | GKE CronJob multi-container |
| **Performance SLA** | p99 ≤90ms (real-time latency) | ~45 min/night (batch runtime) |
| **Key Metrics** | Latency, throughput, block rate | Items/day, sources, cost/item |
| **Integration** | Calls services in 4 namespaces | Called by services (foundational) |
| **Unique Features** | ATP 5-19, JR validation rules | Ethical crawling, tier classification |
| **Cost Model** | Per-API-call validation costs | Monthly operational ~$77 |
| **Quality Focus** | False positive/negative rates | Relevance, timeliness, completeness |
| **Confidence Target** | ≥70% (production data available) | ≥60% (specs-only, pre-production) |
| **New Sections** | — | Ethical compliance, multi-source coverage, tier metrics, AM briefing |

**Complementary Roles**:
- **Ingestion Layer**: Acquires intelligence upstream (preventive, proactive)
- **Judge #6**: Validates intelligence downstream (defensive, reactive)
- **Data Flow**: Ingestion → [AutoGen/Cognitive processing] → Judge #6 → Final output

---

## Execution Instructions

**To run this analysis:**

1. Load this prompt into Gemini 2.0 Pro
2. Provide accompanying documents:
   - Gemini Ingestion Layer architecture specifications
   - Source configuration matrix
   - Cost breakdown spreadsheet
   - Integration API contracts (if available)
   - Ethical compliance policy docs
3. Request output in markdown format
4. Review findings for:
   - Critical risks requiring pre-production fixes
   - Cost optimization opportunities
   - Missing specs that need clarification
5. Iterate with refinements based on initial analysis
6. Use insights to inform production deployment decision

**Expected Analysis Time**: 10-15 minutes for Gemini 2.0 Pro (comprehensive review)

---

**End of Prompt**


================================================================================



## Supporting Documents

_The following documents were provided to support the analysis:_

### Document: cost-model.md

```md
# Cost Model - Gemini Ingestion Layer

**Version**: 1.0-draft
**Status**: Pre-Production Estimates
**Last Updated**: 2025-11-15
**Monthly Budget Target**: $77

---

## Cost Breakdown (Monthly)

### 1. GKE Compute Costs
**Component**: Google Kubernetes Engine cluster

| Resource | Specification | Cost/Hour | Hours/Month | Monthly Cost |
|----------|---------------|-----------|-------------|--------------|
| **Control Plane** | GKE Autopilot | $0.10/hour | 730 | $73.00 |
| **Worker Nodes** | 2× e2-standard-4 (preemptible) | $0.067/node/hour | 22.5 hours/month<br/>(45 min/night × 30 nights) | $3.02 |
| **Persistent Volumes** | 5GB ephemeral (no cost) | $0 | - | $0 |
| **Load Balancer** | Not needed (batch job) | $0 | - | $0 |

**Subtotal GKE**: ~$76.02/month

**Cost Optimization**:
- Using **Autopilot** (pay-per-pod) instead of Standard saves ~40%
- **Preemptible nodes** save 80% vs on-demand ($0.067 vs $0.335/hour)
- **No persistent storage** (ephemeral volumes only)
- **No load balancer** (batch job, not web-facing)

**Risk**: Preemptible nodes can be interrupted mid-job (~5% failure rate)

---

### 2. API Costs

#### Gemini 2.0 Pro API (Tier Classification)
**Usage**: 1000-2000 items/night classified

| Tier | Price | Items/Night | API Calls | Monthly Cost |
|------|-------|-------------|-----------|--------------|
| **Gemini 2.0 Pro** | $0.001/1K chars input<br/>$0.003/1K chars output | 1500 avg | 150 calls<br/>(batch 10 items/call) | $18.00 |

**Assumptions**:
- Average item size: 500 characters (title + snippet)
- Batch size: 10 items per API call
- Input tokens: 500 chars × 10 items = 5K chars/call = $0.005/call
- Output tokens: ~200 chars/call (tier + score) = $0.0006/call
- Total per call: ~$0.006 × 150 calls/night × 30 nights = $27/month

**Actual estimate (with buffers)**: $18-20/month

**Cost Optimization**:
- **Batching**: 10 items/call vs 1 item/call saves 90% on API overhead
- **Caching**: Identical items (repost detection) skip classification
- **Fallback**: Rule-based classifier for obvious Tier 3 (spam) saves API calls

---

#### Source API Costs

| Source | API | Price | Usage | Monthly Cost |
|--------|-----|-------|-------|--------------|
| **YouTube** | Data API v3 | $0.001/quota unit | 10K units/night × 30 | $0.30 |
| **Twitter** | API v2 Elevated | $100/month base | Included in subscription | $3.33 (amortized) |
| **Reddit** | PRAW API | Free | N/A | $0 |
| **Hacker News** | Firebase | Free | N/A | $0 |
| **arXiv** | OAI-PMH | Free | N/A | $0 |
| **Others** | Various | Free/public | N/A | $0 |

**Subtotal APIs**: ~$21.63/month

---

### 3. Storage Costs

#### Cloud Storage (Raw Data)
**Usage**: Store raw crawl data for 30 days (audit/reprocessing)

| Storage Type | Data Volume | Price | Monthly Cost |
|--------------|-------------|-------|--------------|
| **Standard Storage** | 1500 items × 1KB avg × 30 nights = 45MB/month cumulative | $0.020/GB | $0.001 |
| **Operations** | 1500 writes/night × 30 = 45K ops | $0.005/10K ops | $0.02 |

**Subtotal Cloud Storage**: ~$0.02/month (negligible)

---

#### Cloud SQL (Metadata)
**Usage**: Store item metadata, source health metrics

| Resource | Specification | Price | Monthly Cost |
|----------|---------------|-------|--------------|
| **Instance** | db-f1-micro (shared, 0.6GB RAM) | $7.67/month | $7.67 |
| **Storage** | 10GB SSD | $0.17/GB/month | $1.70 |

**Subtotal Cloud SQL**: ~$9.37/month

**Alternative**: Use Cloud Firestore (serverless) for ~$1-2/month at current scale

---

### 4. Networking Costs

#### Egress (Crawling External Sources)

| Traffic Type | Volume | Price | Monthly Cost |
|--------------|--------|-------|--------------|
| **Egress to Internet** | 1500 items × 2KB avg × 30 nights = 90MB/month | $0.12/GB (first 1GB free) | $0 (under 1GB) |
| **Ingress** | Free | $0 | $0 |

**Subtotal Networking**: ~$0/month (under free tier)

---

### 5. Monitoring & Logging

#### Cloud Monitoring + Logging

| Service | Usage | Price | Monthly Cost |
|---------|-------|-------|--------------|
| **Metrics** | ~100 metrics × 30 days | $0.258/MB ingested | $0.50 |
| **Logs** | 1GB logs/month (job output) | $0.50/GB | $0.50 |

**Subtotal Monitoring**: ~$1.00/month

---

## Total Monthly Cost Summary

| Category | Cost | % of Total |
|----------|------|------------|
| **GKE Compute** | $76.02 | 62.5% |
| **APIs (Gemini + Sources)** | $21.63 | 17.8% |
| **Storage (Cloud SQL + GCS)** | $9.39 | 7.7% |
| **Networking** | $0.00 | 0% |
| **Monitoring** | $1.00 | 0.8% |
| **TOTAL** | **$108.04** | 100% |

**Note**: Exceeds target of $77/month by $31. Need optimization.

---

## Cost Optimization Strategies

### Option 1: Use Cloud Run Instead of GKE
**Savings**: ~$70/month (no Autopilot control plane cost)

| Resource | Cloud Run Cost | GKE Cost | Savings |
|----------|---------------|----------|---------|
| **Compute** | $0.00002/vCPU-sec × 4 vCPU × 2700 sec = $0.216/night | $3.02/month | Minimal |
| **Control Plane** | $0 (serverless) | $73/month | **$73/month** |

**Trade-off**: Cloud Run has 60-minute max runtime (vs GKE unlimited). For 45-minute target, acceptable.

**Recommended**: Migrate to Cloud Run to hit $77 budget.

---

### Option 2: Reduce Gemini API Usage
**Savings**: ~$10/month

- Pre-filter obvious Tier 3 (spam) with rule-based classifier (saves ~30% of API calls)
- Increase batch size from 10 to 20 items/call (saves ~10% on overhead)
- Cache classification for duplicate items (retweets, cross-posts)

**New API Cost**: $18 → $8/month

---

### Option 3: Use Smaller Cloud SQL Instance
**Savings**: ~$5/month

- Migrate from Cloud SQL ($9/month) to Firestore ($1-2/month)
- Store only metadata in Firestore, raw data in Cloud Storage

**New Storage Cost**: $9.37 → $2/month

---

### Option 4: Optimize Source Crawling
**Savings**: ~$5/month

- Remove or reduce frequency of low-yield sources (YouTube at 25% Tier 1)
- Focus on high-yield sources (Hacker News, News RSS, Government at 45-70% Tier 1)
- Reduces item count from 1500 → 1000/night, but maintains Tier 1 absolute count

**New Item Count**: 1500 → 1000/night
**Tier 1 Count**: 450 → 400/night (still meets targets)

---

## Revised Cost Model (With Optimizations)

| Category | Original | Optimized | Savings |
|----------|----------|-----------|---------|
| **Compute** | $76.02 (GKE) | $6.48 (Cloud Run) | **$69.54** |
| **APIs** | $21.63 | $11.63 | **$10.00** |
| **Storage** | $9.39 | $2.00 (Firestore) | **$7.39** |
| **Networking** | $0.00 | $0.00 | $0 |
| **Monitoring** | $1.00 | $1.00 | $0 |
| **TOTAL** | **$108.04** | **$21.11** | **$86.93** |

**New Monthly Cost**: ~$21/month (well under $77 budget)

**Margin**: $77 - $21 = **$56/month buffer** for growth

---

## Scaling Scenarios

### Scenario A: 2× Item Volume (3000 items/night)
| Category | Cost Impact | New Cost |
|----------|-------------|----------|
| Compute (Cloud Run) | 2× runtime (90 min/night) | $12.96 |
| APIs | 2× Gemini calls | $23.26 |
| Storage | 2× data | $3.00 |
| Other | Unchanged | $1.00 |
| **TOTAL** | | **$40.22/month** |

**Still under budget** ($77 target)

---

### Scenario B: 5× Item Volume (7500 items/night)
| Category | Cost Impact | New Cost |
|----------|-------------|----------|
| Compute | 5× runtime (225 min = 3.75 hours) | $32.40 |
| APIs | 5× Gemini calls | $58.15 |
| Storage | 5× data | $8.00 |
| Other | Unchanged | $1.00 |
| **TOTAL** | | **$99.55/month** |

**Exceeds budget** by $22.55 (need to increase budget or optimize further)

---

### Scenario C: 10× Item Volume (15,000 items/night)
| Category | Cost Impact | New Cost |
|----------|-------------|----------|
| Compute | 10× runtime (450 min = 7.5 hours) | $64.80 |
| APIs | 10× Gemini calls | $116.30 |
| Storage | 10× data | $15.00 |
| Other | Unchanged | $1.00 |
| **TOTAL** | | **$197.10/month** |

**Exceeds budget** by $120.10 (need to re-architect or significantly increase budget)

**Economies of Scale**: Cost/item decreases from $0.021 (1000 items) → $0.013 (15K items)

---

## Cost per Item Analysis

### Current (Optimized)
- **Total Cost**: $21.11/month
- **Items**: 1000 items/night × 30 nights = 30,000 items/month
- **Cost/Item**: $21.11 / 30,000 = **$0.0007/item** (well under $0.04 target)

### Original (Unoptimized)
- **Total Cost**: $108.04/month
- **Items**: 45,000 items/month
- **Cost/Item**: $108.04 / 45,000 = **$0.0024/item** (still under $0.04 target)

**Target**: $0.04/item (conservative)
**Actual**: $0.0007-0.0024/item (16-57× better than target)

**Implication**: Cost targets are very conservative, significant headroom for growth.

---

## Budget Alerts Configuration

### Alert Thresholds
- **70% of budget** ($53.90): Warning alert to Slack
- **90% of budget** ($69.30): Critical alert to on-call + email
- **100% of budget** ($77): Auto-shutdown + PagerDuty alert

### Alert Triggers
```yaml
# Cloud Monitoring alert policy
- name: ingestion-cost-warning
  condition: monthly_cost >= 53.90
  notification: slack-#pnkln-alerts

- name: ingestion-cost-critical
  condition: monthly_cost >= 69.30
  notification:
    - slack-#pnkln-alerts
    - email-oncall@pnkln.ai

- name: ingestion-cost-exceeded
  condition: monthly_cost >= 77.00
  notification: pagerduty-high
  action: disable-cronjob
```

---

## Open Questions (for Analysis)

1. **Should we migrate from GKE to Cloud Run** for $70/month savings?
2. **Is $21/month realistic**, or are we missing hidden costs (data transfer spikes, etc.)?
3. **What's the acceptable buffer** (50% under budget = $35-40/month target)?
4. **How do we handle unexpected API price increases** (e.g., Gemini pricing up 50%)?
5. **Should we set up billing export to BigQuery** for detailed cost attribution per source?
6. **What's the cost impact of adding 5 more sources** (Telegram, Discord, Medium)?

---

**Status**: Draft cost model for analysis review
**Recommendation**: Implement all 4 optimizations to achieve $21/month (vs $77 budget)
**Next Steps**: Gemini 2.0 Pro analysis of cost assumptions, scaling risks, optimization trade-offs

```

### Document: gke-cronjob-spec.md

```md
# Gemini Ingestion Layer - GKE CronJob Specification

**Version**: 1.0-draft
**Status**: Pre-Production Design
**Date**: 2025-11-15

---

## CronJob Definition

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ingestion-nightly
  namespace: ingestion
  labels:
    app: gemini-ingestion
    component: batch-crawler
    tier: foundational
spec:
  # Run nightly at 3:00 AM UTC
  schedule: "0 3 * * *"
  timeZone: "UTC"
  concurrencyPolicy: Forbid  # Don't allow overlapping runs
  successfulJobsHistoryLimit: 7
  failedJobsHistoryLimit: 3

  jobTemplate:
    spec:
      # 45-minute timeout for entire job
      activeDeadlineSeconds: 2700  # 45 minutes
      backoffLimit: 1  # Only retry once on failure

      template:
        metadata:
          labels:
            app: gemini-ingestion
            batch: nightly
        spec:
          restartPolicy: Never
          serviceAccountName: ingestion-sa

          # Init container: Pre-flight checks
          initContainers:
          - name: preflight
            image: gcr.io/pnkln-prod/ingestion-preflight:v1.0
            command: ["/bin/sh", "-c"]
            args:
              - |
                echo "Checking source availability..."
                # Validate all 8 sources are reachable
                python /app/check_sources.py
                echo "Validating robots.txt compliance..."
                python /app/validate_robots.py
                echo "Preflight checks complete"
            resources:
              requests:
                cpu: 100m
                memory: 128Mi
              limits:
                cpu: 200m
                memory: 256Mi

          # Main containers: Parallel execution
          containers:
          # Container 1: Source Crawler (YouTube)
          - name: crawler-youtube
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "youtube"
            - name: API_KEY
              valueFrom:
                secretKeyRef:
                  name: youtube-api-key
                  key: key
            - name: RATE_LIMIT
              value: "10"  # 10 requests/sec
            - name: MAX_ITEMS
              value: "300"
            command: ["/app/crawler.py"]
            args: ["--source", "youtube", "--output", "/data/youtube.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 500m
                memory: 512Mi
              limits:
                cpu: 1000m
                memory: 1Gi

          # Container 2: Source Crawler (Twitter)
          - name: crawler-twitter
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "twitter"
            - name: BEARER_TOKEN
              valueFrom:
                secretKeyRef:
                  name: twitter-api-token
                  key: bearer
            - name: RATE_LIMIT
              value: "1"  # 1 request/sec (Twitter strict)
            - name: MAX_ITEMS
              value: "250"
            command: ["/app/crawler.py"]
            args: ["--source", "twitter", "--output", "/data/twitter.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 512Mi
              limits:
                cpu: 500m
                memory: 1Gi

          # Container 3: Source Crawler (News RSS)
          - name: crawler-news
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "news"
            - name: RATE_LIMIT
              value: "20"  # 20 requests/sec for RSS
            - name: MAX_ITEMS
              value: "400"
            command: ["/app/crawler.py"]
            args: ["--source", "news", "--output", "/data/news.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 256Mi
              limits:
                cpu: 500m
                memory: 512Mi

          # Container 4: Source Crawler (Reddit)
          - name: crawler-reddit
            image: gcr.io/pnkln-prod/ingestion-crawler:v1.0
            env:
            - name: SOURCE_TYPE
              value: "reddit"
            - name: CLIENT_ID
              valueFrom:
                secretKeyRef:
                  name: reddit-api-creds
                  key: client_id
            - name: CLIENT_SECRET
              valueFrom:
                secretKeyRef:
                  name: reddit-api-creds
                  key: client_secret
            - name: RATE_LIMIT
              value: "5"  # 5 requests/sec
            - name: MAX_ITEMS
              value: "200"
            command: ["/app/crawler.py"]
            args: ["--source", "reddit", "--output", "/data/reddit.jsonl"]
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 512Mi
              limits:
                cpu: 500m
                memory: 1Gi

          # Container 5: Classifier (runs after crawlers complete)
          - name: classifier
            image: gcr.io/pnkln-prod/ingestion-classifier:v1.0
            env:
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gemini-api-key
                  key: key
            - name: BATCH_SIZE
              value: "10"  # Batch 10 items per API call
            - name: TIER1_THRESHOLD
              value: "0.7"  # Confidence score for Tier 1
            command: ["/bin/sh", "-c"]
            args:
              - |
                # Wait for crawlers to finish
                while [ ! -f /data/.crawl_complete ]; do sleep 10; done
                echo "Starting classification..."
                python /app/classify.py --input /data/*.jsonl --output /data/classified.jsonl
                echo "Classification complete"
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 500m
                memory: 1Gi
              limits:
                cpu: 1000m
                memory: 2Gi

          # Container 6: Compliance Validator
          - name: validator
            image: gcr.io/pnkln-prod/ingestion-validator:v1.0
            command: ["/bin/sh", "-c"]
            args:
              - |
                # Wait for classification
                while [ ! -f /data/classified.jsonl ]; do sleep 10; done
                echo "Validating ethical compliance..."
                python /app/validate.py --input /data/classified.jsonl --output /data/validated.jsonl
                echo "Validation complete"
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 200m
                memory: 256Mi
              limits:
                cpu: 500m
                memory: 512Mi

          # Container 7: Briefing Generator
          - name: briefing
            image: gcr.io/pnkln-prod/ingestion-briefing:v1.0
            env:
            - name: DELIVERY_TIME
              value: "06:00"  # 6:00 AM target
            - name: RECIPIENT_EMAILS
              value: "team@pnkln.ai"
            command: ["/bin/sh", "-c"]
            args:
              - |
                # Wait for validation
                while [ ! -f /data/validated.jsonl ]; do sleep 10; done
                echo "Generating AM briefing..."
                python /app/generate_briefing.py --input /data/validated.jsonl --output /data/briefing.html
                python /app/send_email.py --briefing /data/briefing.html
                echo "Briefing delivered"
            volumeMounts:
            - name: data-volume
              mountPath: /data
            resources:
              requests:
                cpu: 300m
                memory: 512Mi
              limits:
                cpu: 500m
                memory: 1Gi

          # Shared volume for inter-container communication
          volumes:
          - name: data-volume
            emptyDir:
              sizeLimit: 5Gi

---

## Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ingestion-quota
  namespace: ingestion
spec:
  hard:
    requests.cpu: "5"
    requests.memory: "8Gi"
    limits.cpu: "10"
    limits.memory: "16Gi"
    pods: "20"
```

---

## Node Pool Configuration (Preemptible)

```yaml
# Terraform configuration for GKE node pool
resource "google_container_node_pool" "ingestion_pool" {
  name       = "ingestion-preemptible"
  cluster    = google_container_cluster.primary.name
  node_count = 2  # Auto-scale 2-5 nodes

  autoscaling {
    min_node_count = 2
    max_node_count = 5
  }

  node_config {
    preemptible  = true  # Cost savings
    machine_type = "e2-standard-4"  # 4 vCPU, 16GB RAM

    labels = {
      workload = "ingestion"
    }

    taint {
      key    = "workload"
      value  = "ingestion"
      effect = "NO_SCHEDULE"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
```

---

## Performance Targets

| Metric | Target | Current Status |
|--------|--------|----------------|
| **Total Runtime** | ≤45 minutes | Untested (pre-prod) |
| **Crawler Phase** | ≤20 minutes | Estimated |
| **Classification Phase** | ≤15 minutes | Estimated (1000 items @ 10/batch) |
| **Validation Phase** | ≤5 minutes | Estimated |
| **Briefing Phase** | ≤5 minutes | Estimated |

---

## Failure Scenarios & Recovery

### Scenario 1: Single Crawler Failure
- **Detection**: Container exit code ≠ 0
- **Impact**: Partial data (e.g., YouTube down, but Twitter/News/Reddit succeed)
- **Recovery**: Job continues with available data, alerts Slack channel

### Scenario 2: Classification API Timeout
- **Detection**: Gemini API returns 504
- **Impact**: Items remain unclassified
- **Recovery**: Retry with exponential backoff (2s, 4s, 8s), fallback to rule-based classifier

### Scenario 3: Briefing Delivery Failure
- **Detection**: Email send fails
- **Impact**: Team doesn't receive AM briefing
- **Recovery**: Store briefing in Cloud Storage, send Slack notification with link

### Scenario 4: Job Exceeds 45-Minute Deadline
- **Detection**: `activeDeadlineSeconds` triggers
- **Impact**: Incomplete data ingestion
- **Recovery**: Job terminates, alerts on-call engineer, reschedule for next night

---

## Open Questions (for Analysis)

1. **Resource Sizing**: Are 4 vCPU/16GB RAM nodes sufficient for 2000 items/night?
2. **Preemptible Risk**: What's acceptable failure rate for cost savings?
3. **Container Dependencies**: Should we use Kubernetes Jobs instead of sidecar containers?
4. **Data Persistence**: Should intermediate data (crawl results) be stored in Cloud Storage?
5. **Monitoring**: What metrics should trigger alerts (runtime >40 min? cost >$3/night?)?

---

**Status**: Draft specification for analysis review
**Next Steps**: Run Gemini 2.0 Pro analysis, address findings before implementation

```

### Document: source-matrix.md

```md
# Source Configuration Matrix

**Version**: 1.0-draft
**Status**: Pre-Production
**Last Updated**: 2025-11-15

---

## Active Sources (8 configured)

### 1. YouTube
**Type**: Video platform
**Access Method**: YouTube Data API v3
**Rate Limit**: 10 requests/second
**Daily Quota**: 10,000 API units
**Authentication**: API key

**Crawl Targets**:
- Trending videos (Technology, News categories)
- Specific channel uploads (top 20 tech channels)
- Video comments (top 100 per video)

**Expected Items/Night**: 300-400
**Expected Tier 1 Ratio**: 25% (video metadata), 35% (trending tech)
**Cost/Item**: ~$0.03 (API quota costs)

**robots.txt Compliance**: N/A (using official API)
**Rate Limiting Strategy**: Token bucket (10/sec sustained, burst 20)

---

### 2. Twitter/X
**Type**: Social media
**Access Method**: Twitter API v2 (Elevated access)
**Rate Limit**: 1 request/second (strict)
**Daily Quota**: 500,000 tweets/month
**Authentication**: Bearer token (OAuth 2.0)

**Crawl Targets**:
- Key accounts: @elonmusk, @sama, @ylecun, @ID_AA_Carmack (50 accounts total)
- Trending hashtags: #AI, #ML, #GKE, #Kubernetes
- Search: "breaking news" OR "announcement"

**Expected Items/Night**: 250-300
**Expected Tier 1 Ratio**: 40% (breaking news), 20% (general tweets)
**Cost/Item**: ~$0.05 (API costs at scale)

**robots.txt Compliance**: N/A (using official API)
**Rate Limiting Strategy**: Fixed 1 req/sec with queue

---

### 3. News Aggregators (RSS)
**Type**: News feeds
**Access Method**: RSS/Atom feeds (public)
**Rate Limit**: 20 requests/second (self-imposed)
**Daily Quota**: Unlimited (public feeds)
**Authentication**: None

**Crawl Targets** (15 feeds):
- AP News: https://apnews.com/rss
- Reuters: https://www.reutersagency.com/feed/
- BBC News: http://feeds.bbci.co.uk/news/rss.xml
- TechCrunch: https://techcrunch.com/feed/
- Ars Technica: https://arstechnica.com/feed/
- The Verge: https://www.theverge.com/rss/index.xml
- Hacker News: https://news.ycombinator.com/rss
- (8 more feeds)

**Expected Items/Night**: 400-500
**Expected Tier 1 Ratio**: 30% (breaking news), 50% (tech news)
**Cost/Item**: ~$0.01 (bandwidth + processing)

**robots.txt Compliance**: Feeds are public, no robots.txt restrictions
**Rate Limiting Strategy**: 1 req/5sec per feed (polite crawling)

---

### 4. Reddit
**Type**: Social news aggregation
**Access Method**: Reddit API (PRAW)
**Rate Limit**: 5 requests/second
**Daily Quota**: 60 requests/minute/client
**Authentication**: OAuth 2.0 (client ID + secret)

**Crawl Targets** (10 subreddits):
- r/technology (3.5M subscribers)
- r/worldnews (32M subscribers)
- r/programming (6M subscribers)
- r/artificial (500K subscribers)
- r/MachineLearning (2.8M subscribers)
- r/kubernetes (180K subscribers)
- r/GoogleCloud (50K subscribers)
- (3 more subreddits)

**Expected Items/Night**: 200-250
**Expected Tier 1 Ratio**: 25% (highly upvoted posts)
**Cost/Item**: ~$0.02 (API + processing)

**robots.txt Compliance**: Using official API (compliant)
**Rate Limiting Strategy**: 5 req/sec with exponential backoff on 429

---

### 5. Hacker News
**Type**: Tech news aggregator
**Access Method**: Hacker News API (Firebase)
**Rate Limit**: No official limit (self-imposed 10/sec)
**Daily Quota**: Unlimited
**Authentication**: None

**Crawl Targets**:
- Front page stories (top 30)
- Ask HN posts
- Show HN posts
- Comments on trending stories

**Expected Items/Night**: 150-200
**Expected Tier 1 Ratio**: 45% (curated tech content)
**Cost/Item**: ~$0.01 (Firebase reads + processing)

**robots.txt Compliance**: API-based (compliant)
**Rate Limiting Strategy**: 10 req/sec max

---

### 6. arXiv (Academic Preprints)
**Type**: Research papers
**Access Method**: arXiv API (OAI-PMH)
**Rate Limit**: 1 request/3 seconds (per guidelines)
**Daily Quota**: Unlimited (bulk downloads discouraged)
**Authentication**: None

**Crawl Targets**:
- cs.AI (Artificial Intelligence)
- cs.LG (Machine Learning)
- cs.CL (Computation and Language/NLP)
- Daily new submissions

**Expected Items/Night**: 50-100
**Expected Tier 1 Ratio**: 60% (peer-reviewed research)
**Cost/Item**: ~$0.01 (processing only)

**robots.txt Compliance**: API usage complies with arXiv terms
**Rate Limiting Strategy**: 1 req/3sec strict

---

### 7. Government/Public Data
**Type**: Official announcements
**Access Method**: Data.gov APIs, agency RSS feeds
**Rate Limit**: Varies by agency (typically 10-50/min)
**Daily Quota**: Agency-specific
**Authentication**: API keys (where required)

**Crawl Targets**:
- Data.gov API: https://api.data.gov/
- NIST announcements
- CISA cybersecurity alerts
- Federal Register (tech-related notices)

**Expected Items/Night**: 30-50
**Expected Tier 1 Ratio**: 70% (official, high-credibility)
**Cost/Item**: ~$0.01 (processing only)

**robots.txt Compliance**: Public data, API-based
**Rate Limiting Strategy**: Agency-specific limits respected

---

### 8. Specialized Forums
**Type**: Niche communities
**Access Method**: Web scraping (ethical, with permission where possible)
**Rate Limit**: 1 request/10 seconds per site
**Daily Quota**: Self-imposed max 100 items/site
**Authentication**: None (public forums)

**Crawl Targets**:
- Stack Overflow (tagged: kubernetes, gke, machine-learning)
- GitHub Discussions (selected repos)
- GitLab Forums
- Security forums (with permission)

**Expected Items/Night**: 100-150
**Expected Tier 1 Ratio**: 20% (signal-to-noise challenge)
**Cost/Item**: ~$0.02 (scraping overhead)

**robots.txt Compliance**: CRITICAL - check robots.txt before every crawl
**Rate Limiting Strategy**: Very conservative (1 req/10sec)

---

## Source Priority Tiers

### High Priority (Crawl First)
1. News RSS (fast, high Tier 1 yield)
2. Hacker News (fast, high Tier 1 yield)
3. Government/Public Data (high credibility)

### Medium Priority
4. Twitter (slow due to rate limits, but timely)
5. Reddit (moderate Tier 1 yield)
6. arXiv (high quality, but niche)

### Low Priority (Crawl Last)
7. YouTube (slow API, mixed quality)
8. Specialized Forums (scraping overhead, low Tier 1)

---

## Coverage Analysis (Pre-Production)

### Geographic Coverage
- **US-centric**: 70% (News, Government, Hacker News)
- **Global**: 30% (BBC, Reuters, arXiv)
- **Gap**: Underrepresented regions (APAC, LATAM)

### Language Coverage
- **English**: 95%
- **Other**: 5% (minimal non-English sources)
- **Gap**: Need multilingual sources for global intelligence

### Topic Coverage
- **Technology**: 60% (strong)
- **General News**: 25% (moderate)
- **Academic/Research**: 10% (niche)
- **Security**: 5% (weak - needs expansion)

### Source Reliability
- **High Credibility** (Tier 1 sources): News RSS, Government, arXiv (50%)
- **Medium Credibility**: Reddit, Hacker News, YouTube (35%)
- **Low Credibility**: Specialized Forums (15% - requires validation)

---

## Redundancy Matrix

| Category | Primary Sources | Backup Sources | Risk Level |
|----------|----------------|----------------|------------|
| **Breaking News** | News RSS, Twitter | Reddit, Hacker News | Low |
| **Tech News** | Hacker News, TechCrunch | Reddit, Twitter | Low |
| **Research** | arXiv | YouTube (lectures), Forums | Medium |
| **Security** | Government, CISA | Forums, Reddit | High (gaps) |
| **Community Insights** | Reddit, Forums | Twitter, Hacker News | Medium |

**Critical Gap**: If Twitter AND Reddit fail, community insights severely limited.

---

## Planned Source Additions (Future)

### Next 3 Months
1. **Telegram Channels** (breaking news, crypto/tech communities)
2. **Discord Servers** (dev communities - with permission)
3. **Medium** (long-form tech articles)

### Next 6-12 Months
4. **Non-English News** (BBC World Service, Al Jazeera, etc.)
5. **Podcasts** (transcriptions of tech podcasts)
6. **Academic Journals** (beyond arXiv - IEEE, ACM with subscriptions)

---

## Source Health Monitoring

### Metrics Tracked per Source
- **Availability**: % uptime (target: 95%+)
- **Item Yield**: Items/night (vs expected)
- **Tier 1 Ratio**: % Tier 1 items (vs expected)
- **Cost Efficiency**: $/item (vs budget)
- **Rate Limit Hits**: # of 429 errors (target: 0)
- **robots.txt Violations**: # of violations (target: 0)

### Auto-Prune Criteria
Remove source if:
- Availability <80% for 7 consecutive days
- Tier 1 ratio <5% for 30 days
- Cost/item >$0.10 sustained
- robots.txt violations >0 (immediate removal)

### Auto-Discover (Future)
- Monitor Hacker News/Reddit for trending new sources
- A/B test new sources (1 week trial)
- Promote to permanent if Tier 1 ratio >20%

---

## Ethical Compliance Checklist

### Pre-Crawl (Automated)
- [ ] Check robots.txt (cache for 24 hours)
- [ ] Verify API quota available
- [ ] Confirm rate limit tokens available
- [ ] Log crawl start (audit trail)

### During Crawl
- [ ] Respect rate limits (enforce with token bucket)
- [ ] Handle 429/503 errors with exponential backoff
- [ ] Stop crawling if robots.txt changes mid-crawl
- [ ] Anonymize PII (social media handles, emails)

### Post-Crawl
- [ ] Log crawl completion (items, duration, errors)
- [ ] Report rate limit hits (Slack alert if >5%)
- [ ] Flag any robots.txt violations for review
- [ ] Store attribution metadata (source URL, timestamp)

---

## Open Questions (for Analysis)

1. **Is 8 sources sufficient**, or should we onboard more to reach 2000 items/night?
2. **Are Tier 1 yield estimates realistic** (25-70% range)?
3. **Should we deprioritize low-yield sources** (e.g., YouTube at 25%)?
4. **What's the risk of over-reliance on News RSS** (40%+ of total volume)?
5. **How do we handle source outages** (Twitter API down for 24 hours)?
6. **Should we add real-time sources** (WebSockets for breaking news)?

---

**Status**: Draft configuration for analysis review
**Next Steps**: Gemini 2.0 Pro analysis of coverage gaps, redundancy, ethics

```

