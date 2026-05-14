# Gemini Ingestion Layer Analysis Prompt

## Objective
Perform a comprehensive pre-production analysis of the PNKLN Gemini Ingestion Layer using architectural specifications, documentation, and design artifacts. This prompt is optimized for Gemini 2.0 Pro's natural language reasoning capabilities.

## Context
The Gemini Ingestion Layer is the upstream intelligence collection component in the PNKLN Core Stack™, operating as a proactive data acquisition pipeline (vs. the downstream reactive Judge #6 validation system). It emphasizes ethical crawling, multi-source diversity, and holistic data quality over real-time performance.

## Analysis Framework

### 1. Direct Replacements from Judge #6 Template

The following substitutions adapt the proven Judge #6 analysis framework for ingestion-specific needs:

| Judge #6 Element | Gemini Ingestion Layer Replacement | Rationale |
|------------------|-------------------------------------|-----------|
| "Judge #6" references | "Gemini Ingestion Layer" | Domain relevance: collection vs. validation |
| `judge_six.py` script | Pipeline docs, architecture specs, flowcharts | Broader scope: distributed system vs. single script |
| p99 ≤90ms latency | ~45 min/night runtime efficiency | Batch processing: total time vs. per-request latency |
| 98% test coverage | Quality gates: items, sources, costs, scores | Multifaceted quality: "how good" vs. "how much" |

**Implication**: These swaps maintain analytical rigor while tailoring to upstream, batch-oriented operations.

### 2. Context-Specific Adaptations

#### Architecture
- **From**: Hybrid Gemini+PyTorch (real-time AI inference)
- **To**: GKE CronJob Multi-Container (batch orchestration)
- **Analysis Focus**:
  - Container orchestration efficiency
  - Fault tolerance (pod failures, retries)
  - Resource allocation (CPU/memory per source type)
  - Variable volume handling (holiday spikes, off-seasons)

#### Key Metrics
- **From**: Latency (p50/p95/p99), throughput (req/sec), block rate
- **To**: Items/day, source count, cost/item, runtime
- **Analysis Focus**:
  - Volume trends: growth rate, seasonality
  - Source diversity: platform mix, topic coverage
  - Cost efficiency: economies of scale, budget sensitivity
  - Runtime: parallelization opportunities, bottlenecks

#### Integration Position
- **From**: Caller (Judge #6 invokes 4 namespace services)
- **To**: Callee (services invoke Ingestion Layer)
- **Analysis Focus**:
  - Upstream triggers: what events initiate ingestion?
  - Downstream handoffs: data format, validation compatibility
  - Integration pain points: latency, failures, format mismatches

#### Unique Features
- **From**: ATP 5-19 compliance, JR validation logic
- **To**: Ethical crawling (robots.txt, rate limits), tier classification
- **Analysis Focus**:
  - Legal risk assessment: TOS violations, copyright
  - Ethical implementation: transparency, respect for servers
  - Tier logic: accuracy of classification, value distribution

#### Cost Model
- **From**: Per-validation API call costs
- **To**: Monthly operational budget (~$77)
- **Analysis Focus**:
  - Cost breakdown: APIs, compute, storage, network
  - Scaling sensitivity: 2x/4x volume scenarios
  - Optimization: batch API calls, cheaper compute tiers

#### Quality Focus
- **From**: False positive/false negative rates
- **To**: Relevance, timeliness, completeness
- **Analysis Focus**:
  - Relevance scoring: keyword match, topic alignment
  - Timeliness: freshness vs. archival balance
  - Completeness: field coverage, metadata richness

### 3. New Sections Added (Ingestion-Specific)

#### A. Ethical Compliance Model
**Purpose**: Ensure responsible web crawling, reduce legal/reputational risks.

**Analysis Tasks**:
1. **robots.txt Adherence**
   - How is robots.txt fetched and parsed?
   - Handling edge cases (invalid syntax, 404s, redirects)
   - Update frequency (cache duration)
   - Evidence of strict compliance in specs

2. **Rate Limiting**
   - Per-domain throttling strategy (requests/second)
   - Adaptive throttling (backing off on errors)
   - Politeness delays (mimicking human behavior)
   - Configuration: global vs. per-source tuning

3. **Transparency**
   - User-agent string: clear identification ("PNKLNBot")
   - Contact info: abuse reporting mechanism
   - Documentation: public disclosure of crawling practices

4. **Platform-Specific TOS**
   - YouTube Data API compliance (quota limits)
   - Twitter API terms (rate limits, content restrictions)
   - News aggregator policies (attribution requirements)

**Confidence Target**: ≥70% (critical for deployment)

#### B. Multi-Source Coverage Analysis
**Purpose**: Ensure diverse intelligence, avoid bias toward single platforms.

**Analysis Tasks**:
1. **Platform Inventory**
   - Enumerate all sources: YouTube, Twitter, News, RSS, Academic
   - Coverage gaps: missing platforms, geographic biases
   - Redundancy: overlapping sources (pro: reliability, con: inefficiency)

2. **Source Distribution**
   - Target mix: e.g., 30% social, 40% news, 20% video, 10% academic
   - Actual vs. target: identify skews (over-reliance on Twitter?)
   - Temporal balance: real-time vs. archival sources

3. **Topic Coverage**
   - Cross-platform topic mapping: politics, tech, science, culture
   - Blind spots: topics covered by only one source
   - Diversity metrics: entropy of topic × platform matrix

4. **Resilience**
   - Fallback strategies: if YouTube API fails, what backups exist?
   - Source prioritization: critical vs. optional platforms

**Confidence Target**: ≥65% (moderate, given spec-based analysis)

#### C. Tier Classification Metrics
**Purpose**: Assess value distribution, optimize resource allocation for high-priority data.

**Analysis Tasks**:
1. **Tier Definitions**
   - Tier 1: Criteria (authoritativeness, timeliness, uniqueness)
   - Tier 2: Criteria (moderate relevance, supplementary value)
   - Tier 3: Criteria (background noise, low signal)
   - Clarity: are definitions objective and measurable?

2. **Classification Logic**
   - Algorithm: rule-based, ML-based, or hybrid?
   - Features: source reputation, content freshness, engagement metrics
   - Validation: how is accuracy tested (human labeling, A/B tests)?

3. **Distribution Analysis**
   - Target: 20% Tier 1, 50% Tier 2, 30% Tier 3 (adjustable)
   - Simulated distribution: based on specs, what's expected?
   - Skew scenarios: what if 80% land in Tier 3? (quality alarm)

4. **Resource Allocation**
   - Processing priority: Tier 1 immediate, Tier 3 delayed
   - Storage: Tier 1 long-term, Tier 3 short-term purge
   - Downstream impact: Judge #6 validation depth by tier

**Confidence Target**: ≥60% (low, needs real data for validation)

#### D. AM Briefing Delivery Effectiveness
**Purpose**: Ensure ingested data produces actionable morning intelligence summaries.

**Analysis Tasks**:
1. **Format Specification**
   - Output: Markdown reports, JSON feeds, email summaries?
   - Structure: headlines, key insights, source citations
   - Customization: user-specific filters (topics, sources)

2. **Timeliness**
   - Target: delivered pre-7am local time
   - Cron schedule: alignment with 45-min runtime window
   - Timezone handling: multi-region deployments

3. **Effectiveness Metrics**
   - Actionability: % of insights leading to user actions (hypothetical)
   - Topic coverage: breadth vs. depth trade-off
   - Novelty: detection of breaking news vs. rehashing old stories

4. **Feedback Loop**
   - User ratings: thumbs up/down on insights
   - Iterative improvement: how is feedback incorporated into tier classification?

**Confidence Target**: ≥55% (very low, highly dependent on user behavior data)

### 4. Confidence Adjustments

#### Target: ≥60% Overall Confidence (Pre-Production)
**Rationale**:
- **No Production Data**: Analysis relies on specs, not telemetry
- **Gemini 2.0 Pro Capabilities**: Strong reasoning, but assumptions required
- **Pragmatic Bar**: Achievable for design-stage review, avoids frustration
- **Post-Deployment**: Raise to ≥70% once logs/metrics available

#### Section-Specific Confidence Floors
| Section | Min Confidence | Justification |
|---------|----------------|---------------|
| Architecture | 65% | Specs should be detailed for GKE deployment |
| Key Metrics | 60% | Estimates based on design targets |
| Ethical Compliance | 70% | Critical for legal risk, must be thorough |
| Multi-Source Coverage | 65% | Source list should be enumerable |
| Tier Classification | 60% | Logic specified, but accuracy unknown |
| AM Briefing Delivery | 55% | User-facing, needs behavioral data |

**Flag Low Confidence**: If any section falls below its floor, explicitly note assumptions and recommend data collection for next iteration.

## Analysis Workflow

### Phase 1: Document Review
1. **Ingest Specs**: Read all architecture docs, flowcharts, API contracts
2. **Extract Key Facts**: Populate metrics table (items/day, cost/item, runtime)
3. **Identify Gaps**: Flag missing info (e.g., no robots.txt parsing details)

### Phase 2: Section-by-Section Analysis
For each section (Architecture, Metrics, Ethical Compliance, etc.):
1. **Apply Framework**: Use analysis tasks from above
2. **Assess Confidence**: Rate 0-100% based on spec completeness
3. **Document Findings**: Strengths, weaknesses, assumptions, risks
4. **Recommend Actions**: Data to collect, design changes, tests to run

### Phase 3: Comparative Insights
1. **Judge #6 Handoff**: Analyze ingestion → validation data flow
2. **PNKLN Stack Integration**: Trace end-to-end from trigger → ingestion → judge → action
3. **Bottleneck Identification**: Where might the pipeline stall or degrade?

### Phase 4: Visualization Outputs
Generate tables/charts for digestibility:
- **Tier Distribution**: Pie chart (Tier 1/2/3 %)
- **Source Coverage**: Heatmap (platform × topic)
- **Cost Trends**: Line graph (projected monthly costs at 1x/2x/4x volume)
- **Runtime Breakdown**: Gantt chart (container startup, crawl, classify, handoff)

### Phase 5: Executive Summary
- **Overall Health**: Red/Yellow/Green rating
- **Top 3 Strengths**: e.g., ethical compliance rigor, cost efficiency
- **Top 3 Risks**: e.g., tier classification untested, source diversity gaps
- **Go/No-Go Recommendation**: For production deployment

## Edge Case Probing

### Failure Mode Analysis
1. **Source Outages**
   - Scenario: YouTube API down for 2 hours during nightly run
   - Expected Behavior: Fallback to RSS feeds, retry logic, partial success
   - Spec Coverage: Is this documented?

2. **Cost Spikes**
   - Scenario: Viral event causes 10x Twitter API usage
   - Expected Behavior: Auto-throttling, budget alerts, graceful degradation
   - Spec Coverage: Cost cap mechanisms?

3. **Tier Skew**
   - Scenario: 80% items classified as Tier 3 (low quality)
   - Expected Behavior: Alert operators, tune source selection, investigate classifier
   - Spec Coverage: Quality monitoring dashboards?

4. **Runtime Overruns**
   - Scenario: Job exceeds 45-minute target (e.g., 90 minutes)
   - Expected Behavior: Timeout, resume next night, or extend window?
   - Spec Coverage: SLA definitions?

### Stress Testing Recommendations
- **Synthetic Data**: Generate 10x volume mock data, measure runtime
- **API Throttling Simulation**: Inject 429 errors, test backoff logic
- **Malformed Data**: Invalid robots.txt, broken RSS feeds, test error handling

## Integration with Judge #6 (Combined Analysis)

### Handoff Protocol
1. **Data Format**
   - Ingestion output: JSON schema
   - Judge #6 input: Expected schema
   - Compatibility: Automated validation or manual mapping?

2. **Handoff Latency**
   - Ingestion → Judge delay: acceptable lag?
   - Real-time vs. batch handoff: implications for timeliness

3. **Error Propagation**
   - Bad ingestion data (malformed, irrelevant) → Judge failures?
   - Feedback loop: Does Judge #6 report quality issues back to Ingestion?

### End-to-End Quality Tracking
- **Ingested**: 1000 items/day
- **Validated** (Judge #6): 950 items pass (5% rejected)
- **Actioned**: 200 items trigger downstream actions (21% actionability)
- **Metrics**: Track funnel conversion, identify drop-off points

## Test Run Protocol

### Sample Specs Generation
Create dummy documentation for 3 fictional sources:
1. **FakeNews API**: News aggregator (200 items/day, Tier 2)
2. **MockTube**: Video platform (50 items/day, Tier 1)
3. **TweetSim**: Social media (500 items/day, mixed tiers)

### Gemini 2.0 Pro Calibration
1. Run analysis prompt on dummy specs
2. Evaluate outputs:
   - Does Gemini identify gaps in ethical compliance sections?
   - Are tier classifications reasonable given mock data?
   - Is confidence scoring accurate (vs. human expert assessment)?
3. Iterate: Adjust prompt wording, add examples, refine frameworks

## Success Criteria

### For This Analysis
- [ ] ≥60% overall confidence achieved
- [ ] All 6 main sections (Architecture, Metrics, Ethical, Coverage, Tier, Briefing) analyzed
- [ ] At least 2 visualizations generated (charts/tables)
- [ ] Top 3 risks identified with mitigation strategies
- [ ] Go/No-Go recommendation provided with justification

### For Production Readiness (Post-Analysis)
- [ ] Ethical compliance: 100% robots.txt adherence verified
- [ ] Multi-source coverage: ≥5 platforms active, no single-source >40% dependency
- [ ] Tier classification: ≥15% Tier 1 items in pilot run
- [ ] AM briefing: Delivered on-time (pre-7am) for 95% of days in pilot
- [ ] Runtime: ≤60 minutes (with 15-min buffer over 45-min target)
- [ ] Cost: ≤$100/month in pilot (with scaling projections validated)

## Deliverables

### Primary Output: Analysis Report
**Format**: Markdown document, ~2000-3000 words

**Structure**:
1. Executive Summary (1 page)
2. Section-by-Section Findings (6 sections × ~2 pages)
3. Visualizations (3-5 charts/tables)
4. Edge Case Analysis (1 page)
5. Integration Assessment (Judge #6 handoff, 1 page)
6. Recommendations (prioritized, 1 page)
7. Confidence Assessment (per-section + overall)

### Secondary Outputs
- **Risk Register**: Top 10 risks, likelihood × impact matrix
- **Test Plan**: For post-deployment validation (what to measure, when)
- **Spec Gaps Document**: Missing info for next design iteration

## Iterative Refinement Suggestions

### After First Run
1. **Test Runs**: Apply to dummy specs, calibrate Gemini outputs
2. **Expert Review**: Have human architect validate findings, adjust prompt
3. **Visualization**: Add requests for specific chart types (pie, heatmap, Gantt)
4. **Edge Cases**: Expand failure mode list based on similar systems

### After Pilot Deployment
1. **Confidence Boost**: Raise target to ≥70% with real logs/metrics
2. **A/B Testing**: Compare Gemini analysis vs. human analysis, measure agreement
3. **Automation**: Script prompt execution, integrate into CI/CD for design reviews

### Future Enhancements
1. **Combined Prompt**: Merge with Judge #6 analysis for end-to-end stack review
2. **Benchmarking**: Compare against industry standards (e.g., Common Crawl efficiency)
3. **Predictive Modeling**: Use historical data to forecast scaling costs, runtime trends

---

## Prompt Execution Instructions (For Gemini 2.0 Pro)

**Input**:
- Architectural specification documents (Markdown, PDF, diagrams)
- API contracts (OpenAPI/Swagger specs)
- Cost models (spreadsheets, budget docs)
- Ethical guidelines (robots.txt policies, TOS summaries)

**Processing**:
1. Read all input documents thoroughly
2. Apply the analysis framework section by section
3. For each section, assess confidence based on spec completeness
4. Generate visualizations where data is sufficient
5. Flag assumptions explicitly when inferring from incomplete specs
6. Produce structured Markdown output per deliverables template

**Output**:
- Full analysis report (Markdown)
- Risk register (table)
- Confidence scores (table with justifications)
- Recommendations (prioritized list)

**Quality Checks**:
- ✅ No hallucinated metrics (only use data from specs or clearly state assumptions)
- ✅ Confidence scores justified (explain why 65% vs. 70%)
- ✅ Actionable recommendations (specific, measurable, time-bound)
- ✅ Comparative insights (vs. Judge #6, vs. industry standards)

---

**Status**: Ready for execution on Gemini 2.0 Pro
**Version**: 1.0 (adapted from Judge #6 template)
**Last Updated**: 2025-11-15
**Next Review**: After first test run with dummy specs
