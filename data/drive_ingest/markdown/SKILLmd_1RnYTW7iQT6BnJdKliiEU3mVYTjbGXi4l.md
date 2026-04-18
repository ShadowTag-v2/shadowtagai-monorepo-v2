# SHADOWTAGAI Component Analysis Skill

**Purpose:** AI-powered analysis templates for SHADOWTAGAI Core Stack™ components
**Enforcement:** `"suggest"`
**Priority:** `"high"`
**Version:** 1.0.0

---

## Overview

This skill provides structured templates for analyzing SHADOWTAGAI stack components using Gemini 2.0 Pro or similar LLMs. It enables deep architectural review, performance optimization, and quality validation across the entire stack—from ingestion layers to enforcement systems.

**Core Principle:** Reusable analysis patterns that adapt to each component's role (collection, transformation, validation, enforcement, delivery).

**Auto-Activation Triggers:**
- Keywords: `analyze`, `review`, `audit`, `shadowtagai`, `component`, `architecture`
- Files: Architecture specs, pipeline docs, component READMEs
- Content: System design documents, performance analysis requests

---

## Component Analysis Framework

Every SHADOWTAGAI component can be analyzed using this structured approach:

```
┌─────────────────────────────────────────────────────────┐
│                  COMPONENT IDENTITY                      │
│  - Name, version, role in stack                         │
│  - Position (upstream/downstream)                        │
│  - Integration points (what calls it, what it calls)    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              ARCHITECTURE ANALYSIS                       │
│  - Technology stack                                      │
│  - Infrastructure (GKE, serverless, hybrid)             │
│  - Scalability patterns                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              PERFORMANCE METRICS                         │
│  - Component-specific KPIs                               │
│  - Quality gates (accuracy, latency, throughput)        │
│  - Cost model ($X/operation or $X/month)                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              QUALITY & COMPLIANCE                        │
│  - Data quality (relevance, completeness, timeliness)   │
│  - Ethical compliance (rate limits, transparency)       │
│  - Security posture (encryption, auth, audit)           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│            OPTIMIZATION OPPORTUNITIES                    │
│  - Performance bottlenecks                               │
│  - Cost reduction strategies                             │
│  - Architectural improvements                            │
└─────────────────────────────────────────────────────────┘
```

---

## Template: Gemini Analysis Prompt

Use this structure for any SHADOWTAGAI component:

```markdown
# Component Analysis: [Component Name]

**Analyst:** Gemini 2.0 Pro (or Claude Sonnet 4.5)
**Target:** [Component Name] v[Version]
**Analysis Date:** [Date]
**Confidence Target:** ≥[X]% (adjust based on data availability)

---

## 1. Component Identity

**Name:** [Full component name]
**Role:** [Collection / Transformation / Validation / Enforcement / Delivery]
**Version:** [Current version]
**Stack Position:** [Upstream / Midstream / Downstream]

**Integration Points:**
- **Called By:** [List of services that invoke this component]
- **Calls:** [List of services this component invokes]
- **Data Flow:** [Input sources → Processing → Output destinations]

---

## 2. Architecture Analysis

**Technology Stack:**
- Primary Language: [e.g., Python 3.11, TypeScript 5.0]
- Framework: [e.g., FastAPI, Express, TensorFlow]
- Infrastructure: [e.g., GKE CronJob, Cloud Run, Hybrid]
- Storage: [e.g., PostgreSQL, Cloud Storage, Redis]

**Deployment Model:**
- Platform: [Google Kubernetes Engine, Cloud Functions, etc.]
- Orchestration: [CronJob, Event-driven, Always-on]
- Containers: [Multi-container pod, single container, serverless]
- Scaling: [Horizontal, vertical, manual]

**Key Design Patterns:**
- [Pattern 1: e.g., Producer-Consumer]
- [Pattern 2: e.g., Circuit Breaker for API calls]
- [Pattern 3: e.g., Tiered prioritization]

---

## 3. Performance Metrics

### Component-Specific KPIs

**For Collection/Ingestion:**
- Daily items ingested: [Target: X items/day]
- Source diversity: [Target: Y distinct sources]
- Cost per item: [Target: $Z/item]
- Runtime efficiency: [Target: <X minutes/night]

**For Validation/Enforcement:**
- Latency: [p99 ≤ Xms]
- Throughput: [X requests/sec]
- Block rate: [X% of violations caught]
- False positive rate: [≤X%]

**For Transformation:**
- Processing time: [X records/sec]
- Data completeness: [≥X%]
- Schema compliance: [≥X%]

### Quality Gates

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| [Metric 1] | [Value] | [Actual] | ✅/⚠️/❌ |
| [Metric 2] | [Value] | [Actual] | ✅/⚠️/❌ |
| [Metric 3] | [Value] | [Actual] | ✅/⚠️/❌ |

### Cost Model

**Monthly Operational Cost:**
- Infrastructure: $[X] (GKE, storage, networking)
- API Calls: $[Y] (external services)
- AI Compute: $[Z] (if applicable)
- **Total:** $[X+Y+Z]/month

**Cost Efficiency:**
- Cost per operation: $[X]
- Cost per user: $[Y]
- Scaling costs: [Linear / Sublinear / Superlinear]

---

## 4. Quality & Compliance

### Data Quality (for data-centric components)

**Relevance:**
- Scoring mechanism: [How relevance is measured]
- Current score: [X/10 average]
- Improvement opportunities: [List]

**Timeliness:**
- Data freshness: [Updated every X hours]
- Staleness threshold: [Alert if >X hours old]

**Completeness:**
- Field coverage: [X% of required fields populated]
- Missing data handling: [Strategy]

**Tier Classification (if applicable):**
- Tier 1 (high-value): [X%]
- Tier 2 (medium-value): [Y%]
- Tier 3 (low-value): [Z%]

### Ethical Compliance (for ingestion/crawling)

**Robots.txt Adherence:**
- Compliance rate: [X%]
- Violations: [List any exceptions]

**Rate Limiting:**
- Max requests/second: [X rps]
- Backoff strategy: [Exponential, linear]
- Respectful crawling: [Y second delay between requests]

**Transparency:**
- User-agent identification: [Clear, descriptive]
- Contact information: [Provided in UA string]
- Opt-out mechanism: [How sites can request exclusion]

### Security Posture

**Encryption:**
- Data at rest: [AES-256-GCM ✅]
- Data in transit: [TLS 1.3 ✅]

**Authentication:**
- Service-to-service: [Method]
- External APIs: [API key management]

**Audit Trail:**
- Logging: [What's logged, retention period]
- Monitoring: [Metrics exported to where]

---

## 5. Integration Analysis

**Upstream Dependencies:**
| Service | Trigger | Failure Mode | Mitigation |
|---------|---------|--------------|------------|
| [Service 1] | [How it calls this] | [What breaks] | [Retry, fallback] |

**Downstream Consumers:**
| Service | Data Consumed | SLA Impact | Mitigation |
|---------|---------------|------------|------------|
| [Service 1] | [What it uses] | [If this fails] | [Cache, graceful degradation] |

**Cross-Namespace Communication:**
- Namespaces involved: [List]
- Communication method: [gRPC, REST, PubSub]
- Network policies: [Firewall rules, service mesh]

---

## 6. Optimization Opportunities

### Performance Bottlenecks

**Identified Issues:**
1. [Bottleneck 1]: [Description]
   - Impact: [Latency +Xms, cost +$Y]
   - Fix: [Proposed solution]
   - Effort: [Low/Medium/High]

2. [Bottleneck 2]: [Description]
   - Impact: [...]
   - Fix: [...]
   - Effort: [...]

### Cost Reduction Strategies

**Quick Wins (<1 week implementation):**
- [Strategy 1]: Save $X/month
- [Strategy 2]: Save $Y/month

**Medium-term (1-4 weeks):**
- [Strategy 3]: Save $Z/month

**Long-term (>1 month):**
- [Strategy 4]: Save $W/month

### Architectural Improvements

**Scalability:**
- Current limit: [X operations/day]
- Scaling bottleneck: [What prevents 10× growth]
- Recommended approach: [Horizontal pods, caching, etc.]

**Reliability:**
- Current uptime: [X%]
- SPOF (Single Points of Failure): [List]
- Redundancy recommendations: [Multi-region, failover]

**Maintainability:**
- Code complexity: [Cyclomatic complexity score]
- Test coverage: [X%]
- Documentation quality: [Good/Fair/Poor]

---

## 7. Delivery Effectiveness (if applicable)

**For components that produce user-facing outputs (e.g., AM Briefing):**

**Format Quality:**
- Readability: [Markdown, HTML, plain text - which works best]
- Structure: [Sections, bullet points, tables]
- Length: [Target: X words, Current: Y words]

**Timeliness:**
- Target delivery time: [e.g., 6:00 AM daily]
- Actual delivery: [Success rate: X%]
- Late deliveries: [Root causes]

**Actionability:**
- User feedback: [Qualitative insights]
- Click-through rate: [X% if links included]
- Follow-up actions: [How often users act on insights]

---

## 8. Confidence & Recommendations

**Analysis Confidence:** [X]% (≥60% for pre-prod specs, ≥70% for prod data)

**Confidence Factors:**
- Documentation quality: [High/Medium/Low]
- Metric availability: [Full/Partial/Limited]
- Production data: [Available/Specs-only]

**Top 3 Recommendations:**
1. **[Recommendation 1]**
   - Priority: [High/Medium/Low]
   - Impact: [Cost savings, performance gain, risk reduction]
   - Effort: [X person-weeks]
   - ROI: [X× in Y months]

2. **[Recommendation 2]**
   - Priority: [...]
   - Impact: [...]
   - Effort: [...]
   - ROI: [...]

3. **[Recommendation 3]**
   - Priority: [...]
   - Impact: [...]
   - Effort: [...]
   - ROI: [...]

**Risk Assessment:**
- High-risk items: [List issues that could cause outages]
- Mitigation timeline: [X weeks to address]

---

## 9. Next Steps

**Immediate Actions (This Sprint):**
- [ ] [Action 1]
- [ ] [Action 2]

**Short-term (Next 4 weeks):**
- [ ] [Action 3]
- [ ] [Action 4]

**Long-term (Backlog):**
- [ ] [Action 5]
- [ ] [Action 6]

**Follow-up Analysis:**
- Re-analyze after: [Date or milestone]
- Focus areas for next review: [What to deep-dive]

---

**Analyzed By:** [Gemini 2.0 Pro / Claude Sonnet 4.5]
**Review Date:** [Date]
**Next Review:** [Date + 3 months]
```

---

## Example 1: Judge #6 (Enforcement/Validation)

### Component Profile

**Name:** Judge #6 (JR Validation System)
**Role:** Enforcement (validates requests against ATP 5-19 doctrine)
**Version:** 3.2.1
**Stack Position:** Midstream (called by 4 services, calls compliance DB)

### Key Metrics (Production)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Latency (p99) | ≤90ms | 78ms | ✅ |
| Throughput | ≥500 rps | 620 rps | ✅ |
| Block Rate | ≥98% violations | 99.2% | ✅ |
| False Positives | ≤2% | 1.3% | ✅ |
| Test Coverage | ≥98% | 99.1% | ✅ |

### Architecture

**Stack:**
- Python 3.11 + FastAPI 0.104
- Hybrid Gemini 2.0 Flash + PyTorch (rule engine)
- Deployed: GKE (3 replicas, horizontal autoscaling)
- Storage: Redis cache + PostgreSQL (compliance rules)

**Integration:**
- Called by: auth-service, shadowtag-service, workflow-engine, activeshield-api
- Calls: compliance-db, audit-log-service
- Namespaces: 4 (production, staging, dev, audit)

### Cost Model

**Per-Operation:**
- Gemini API call: $0.0005/request
- Redis lookup: $0.0001/request
- **Total:** $0.0006/validation

**Monthly (at 10M validations):**
- API costs: $5,000
- Infrastructure: $800 (GKE)
- **Total:** $5,800/month

### Optimization Opportunities

1. **Cache Gemini responses for common patterns** → Save $2,000/month
2. **Upgrade to Gemini 2.0 Flash-8B** → Save $1,500/month (20% faster)
3. **Implement request batching** → Reduce latency by 15ms

**ROI:** $3,500/month savings with 2 weeks implementation

### Confidence: 85% (production metrics available)

---

## Example 2: Gemini Ingestion Layer (Collection/Preprocessing)

### Component Profile

**Name:** Gemini Ingestion Layer
**Role:** Collection (gathers intelligence from multiple sources)
**Version:** 2.1.0 (Pre-Production)
**Stack Position:** Upstream (provides data to 4 downstream services)

### Key Metrics (Target - Specs Only)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Daily Items Ingested | ≥5,000 items | TBD | ⚠️ Pre-prod |
| Source Diversity | ≥10 sources | 12 configured | ✅ |
| Cost per Item | ≤$0.02/item | $0.018 (estimated) | ✅ |
| Runtime Efficiency | ≤45 min/night | 38 min (test run) | ✅ |
| Data Completeness | ≥95% fields | TBD | ⚠️ Pre-prod |

### Architecture

**Stack:**
- Python 3.11 + AsyncIO
- Multi-source crawlers (YouTube, Twitter/X, News APIs, RSS)
- Deployed: GKE CronJob (runs daily at 2:00 AM UTC)
- Storage: Cloud Storage (raw data) → BigQuery (processed)

**Multi-Container Pod:**
- Container 1: Web scraper (Playwright + BeautifulSoup)
- Container 2: API aggregator (Twitter, YouTube Data API)
- Container 3: Data normalizer (Gemini 2.0 Pro for entity extraction)
- Container 4: Quality scorer (assigns Tier 1/2/3)

**Integration:**
- Called by: scheduler-service (cron trigger)
- Calls: None (writes to Cloud Storage, publishes PubSub event)
- Downstream consumers: AM Briefing Service, Analytics Pipeline, Search Index, Cognitive Stack

### Cost Model

**Monthly Operational:**
- GKE (CronJob): $25/month (ephemeral pods)
- Cloud Storage: $12/month (30-day retention)
- BigQuery: $15/month (query costs)
- API costs: $20/month (YouTube, Twitter)
- Gemini 2.0 Pro: $5/month (entity extraction)
- **Total:** $77/month

**Cost Efficiency:**
- Cost per item: $0.018 (5K items/day × 30 days = 150K items)
- Scaling: Linear (double volume → ~$154/month)

### Quality & Compliance

**Ethical Crawling:**
- Robots.txt adherence: 100% (respects all directives)
- Rate limiting: 1 request/2 seconds per domain
- User-agent: `SHADOWTAGAIBot/2.1 (+https://shadowtagai.ai/bot-info)`
- Transparency: Contact email in UA, opt-out form on website

**Tier Classification:**
- Tier 1 (high-value, exclusive sources): Target 20% → Current 18% ✅
- Tier 2 (medium-value, mainstream): Target 50% → Current 52% ✅
- Tier 3 (low-value, commodity): Target 30% → Current 30% ✅

**Data Quality (Estimated from Specs):**
- Relevance: 8.2/10 (scored by Gemini entity extraction)
- Timeliness: 6-hour average lag (news published → ingested)
- Completeness: 95% of required fields (title, source, timestamp, content)

### AM Briefing Delivery Effectiveness

**Downstream Impact:**
- Briefing format: Markdown → HTML (rendered in email)
- Delivery time: 6:00 AM daily (4 hours after ingestion completes)
- User feedback: 4.2/5 average rating (beta testers)
- Actionability: 65% of briefings lead to follow-up research

### Optimization Opportunities

1. **Parallelize API calls across containers** → Reduce runtime from 38min to 25min
   - Effort: 3 days
   - Impact: 34% faster, same cost

2. **Implement tiered crawling schedule** → Tier 1 sources checked 2×/day, Tier 3 weekly
   - Effort: 1 week
   - Impact: Improve relevance to 8.8/10, reduce API costs by 20%

3. **Cache Gemini entity extraction for similar articles** → Reduce Gemini API calls by 40%
   - Effort: 2 weeks
   - Impact: Save $2/month (small now, scales with volume)

**ROI:** 13 minutes/night saved + $24/month at 10× scale

### Confidence: 62% (specs + test runs, no production metrics yet)

**Confidence Factors:**
- Documentation: High (detailed architecture diagrams, API specs)
- Metrics: Limited (test environment only, 1 week of data)
- Production data: Not available (pre-prod)

**Recommendation:** Deploy to production for 30 days, then re-analyze with real metrics to achieve ≥75% confidence.

---

## Adaptation Guide: Customizing the Template

### Step 1: Identify Component Type

| Type | Characteristics | Metrics Focus |
|------|-----------------|---------------|
| **Collection** | Gathers data from external sources | Items/day, sources, cost/item, runtime |
| **Transformation** | Processes/enriches data | Throughput, schema compliance, data quality |
| **Validation** | Enforces rules/policies | Latency, block rate, FP/FN rates |
| **Enforcement** | Executes actions based on rules | Latency, success rate, audit coverage |
| **Delivery** | Presents data to users/systems | Timeliness, format quality, actionability |

### Step 2: Map Template Sections

**Direct Replacements:**
- Component name: [Old Name] → [New Name]
- File references: [Old docs] → [New architecture specs]
- Performance metrics: [Old KPIs] → [Component-specific KPIs]

**Context Adaptations:**
- Architecture: Match deployment model (GKE, Cloud Run, hybrid)
- Key Metrics: Align with component role (see table above)
- Integration: Caller vs. callee (upstream vs. downstream)
- Unique Features: Highlight differentiators (ethical crawling, ATP 5-19, etc.)

**New Sections (if applicable):**
- Ethical compliance (for crawlers)
- Multi-source coverage (for aggregators)
- Tier classification (for prioritization systems)
- Delivery effectiveness (for user-facing outputs)

### Step 3: Set Confidence Targets

**Pre-Production (Specs Only):**
- Target: ≥60% confidence
- Rationale: Limited to architecture review, no real metrics

**Production (With Metrics):**
- Target: ≥70% confidence
- Rationale: Real data available, can validate performance

**Mature System (>6 months in prod):**
- Target: ≥85% confidence
- Rationale: Historical trends, seasonal patterns understood

### Step 4: Customize Quality Gates

**For Collection Components:**
- Daily volume thresholds
- Source diversity minimums
- Cost per item ceilings
- Runtime efficiency targets

**For Validation Components:**
- Latency percentiles (p50, p95, p99)
- Throughput minimums (rps)
- Accuracy metrics (FP/FN rates)
- Test coverage floors

**For Transformation Components:**
- Processing speed (records/sec)
- Schema compliance rates
- Data completeness percentages

---

## Integration with ShadowTag-v2JR Gates

When analyzing components as part of feature planning, integrate with strategic gates:

### Purpose Gate Integration

**Question:** Does this component serve strategic goals?

Use component analysis to validate:
- Alignment with SHADOWTAGAI roadmap (see Strategy Diamond in MBA frameworks)
- Value chain position (see Integration Analysis section)
- Competitive differentiation (see Unique Features)

### Reasons Gate Integration

**Question:** Will this component deliver ROI?

Use component analysis to calculate:
- Cost model (monthly operational costs)
- Value created (downstream impact on other services)
- ROI calculation (see Optimization Opportunities)

### Brakes Gate Integration

**Question:** Can we reverse this if it fails?

Use component analysis to assess:
- SPOF identification (see Reliability section)
- Rollback procedures (see Failure Modes in Integration)
- Blast radius (how many services depend on this)

**Example Combined Analysis:**

```markdown
Feature: Add Gemini Ingestion Layer to SHADOWTAGAI stack

PURPOSE GATE: ✅ PASS
- Strategic alignment: Core intelligence collection (upstream foundation)
- Cor.X Reference: Cor.17 (SHADOWTAGAI Core Stack)
- Classification: Mission-critical

REASONS GATE: ✅ PASS
- Investment: $77/month operational + $15k dev (4 weeks)
- Value created: Enables AM Briefing ($2k/month revenue potential)
- ROI: ($2k × 18mo - $77 × 18mo - $15k) / $15k = 1.8× (CONDITIONAL)
- Improvement needed: Increase pricing or add 2nd revenue stream

BRAKES GATE: ✅ PASS
- Rollback: Disable CronJob, downstream services use cached data
- Blast radius: Medium (4 services affected, but graceful degradation)
- Kill-switch: Disable if cost >$100/month or quality score <7/10

COMPONENT ANALYSIS: 62% confidence (pre-prod)
- Architecture: Sound (multi-container, ethical crawling)
- Optimization opportunities: +34% speed, -20% cost
- Recommendation: Deploy to prod, re-analyze in 30 days

DECISION: CONDITIONAL GO
- Deploy to production
- Monitor metrics for 30 days
- Re-run gates with real data
- Kill if ROI <2× after optimizations
```

---

## Resources

**Internal:**
- [resources/component-templates.md](resources/component-templates.md) - Copy-paste ready templates for common component types
- [resources/gemini-prompts.md](resources/gemini-prompts.md) - Optimized prompts for Gemini 2.0 Pro analysis
- [resources/metrics-catalog.md](resources/metrics-catalog.md) - Standard KPIs for each component type

**Integration:**
- See `ShadowTag-v2jr-judge` skill for strategic gate validation
- See `security-enforcement` skill for security analysis requirements
- See `universal-copilot-patterns` for KERNEL prompt engineering (effective AI analysis prompts)

**External:**
- Gemini 2.0 Pro Docs: https://ai.google.dev/gemini-api/docs
- GKE Best Practices: https://cloud.google.com/kubernetes-engine/docs/best-practices
- System Design Primer: https://github.com/donnemartin/system-design-primer

---

## Best Practices

1. **Start with specs, iterate with metrics**
   - Pre-prod: 60% confidence (specs-only analysis)
   - Production: 70%+ confidence (add real metrics)
   - Mature: 85%+ confidence (historical trends)

2. **Customize, don't copy-paste**
   - Each component type has unique KPIs
   - Adjust confidence targets based on data availability
   - Add/remove sections based on component role

3. **Integrate with strategic gates**
   - Run component analysis before ShadowTag-v2JR gates
   - Use cost models and optimization opportunities for Reasons gate
   - Use SPOF/blast radius for Brakes gate

4. **Automate where possible**
   - Use Gemini 2.0 Pro for initial analysis
   - Export metrics to BigQuery for trend analysis
   - Schedule quarterly re-analysis for mature components

5. **Focus on actionability**
   - Every analysis should produce 3-5 concrete recommendations
   - Prioritize by ROI and effort
   - Track implementation success rate

---

**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi Engineering (Erik)
**Framework:** Component Analysis (Identity → Architecture → Metrics → Quality → Optimization)
**Model:** Gemini 2.0 Pro / Claude Sonnet 4.5
