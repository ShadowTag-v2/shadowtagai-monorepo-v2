# Component Analysis Templates (Quick Reference)

**Purpose:** Copy-paste ready templates for analyzing SHADOWTAGAI stack components
**Usage:** Select template based on component type, fill in values, run analysis

---

## Template 1: Collection/Ingestion Component

**Use for:** Web scrapers, API aggregators, data ingestion pipelines

```markdown
# Component Analysis: [Component Name] (Collection)

## Identity
- **Role:** Collection (gather data from external sources)
- **Version:** [X.Y.Z]
- **Stack Position:** Upstream (provides data to [N] downstream services)

## Architecture
**Stack:**
- Language: Python 3.11+ / Node.js 20+
- Framework: [AsyncIO / Express / Custom]
- Infrastructure: GKE CronJob / Cloud Run / Serverless
- Storage: [Cloud Storage / BigQuery / PostgreSQL]

**Deployment:**
- Schedule: [Daily at HH:MM / Event-driven]
- Containers: [Single / Multi-container pod]
- Scaling: [Manual / Horizontal autoscaling]

## Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Daily Items Ingested | ≥[X] items | [Actual] | ✅/⚠️/❌ |
| Source Diversity | ≥[Y] sources | [Actual] | ✅/⚠️/❌ |
| Cost per Item | ≤$[Z]/item | [Actual] | ✅/⚠️/❌ |
| Runtime Efficiency | ≤[X] min | [Actual] | ✅/⚠️/❌ |
| Data Completeness | ≥[X]% | [Actual] | ✅/⚠️/❌ |

## Quality Gates

**Source Coverage:**
- High-value sources (Tier 1): [X]%
- Medium-value sources (Tier 2): [Y]%
- Low-value sources (Tier 3): [Z]%

**Ethical Compliance:**
- [ ] Robots.txt adherence: 100%
- [ ] Rate limiting: [X req/sec]
- [ ] Transparent user-agent
- [ ] Opt-out mechanism provided

**Data Quality:**
- Relevance score: [X]/10
- Timeliness: [X]-hour lag
- Completeness: [X]% fields populated

## Cost Model

**Monthly Operational:**
- Infrastructure: $[X]
- API calls: $[Y]
- Storage: $[Z]
- **Total:** $[X+Y+Z]/month

**Cost Efficiency:**
- Cost per item: $[X]
- Scaling factor: [Linear / Sublinear]

## Optimization Opportunities

1. **[Opportunity 1]**
   - Impact: [Runtime -X%, Cost -$Y]
   - Effort: [Days/weeks]
   - ROI: [Calculate]

2. **[Opportunity 2]**
   - Impact: [...]
   - Effort: [...]
   - ROI: [...]

## Confidence: [X]% ([Pre-prod specs only / Production metrics])
```

---

## Template 2: Validation/Enforcement Component

**Use for:** Policy enforcers, compliance validators, request filters

```markdown
# Component Analysis: [Component Name] (Validation)

## Identity
- **Role:** Validation (enforce rules/policies on requests)
- **Version:** [X.Y.Z]
- **Stack Position:** Midstream (called by [N] services)

## Architecture
**Stack:**
- Language: [Python 3.11 / TypeScript 5.0]
- Framework: [FastAPI / Express]
- AI: [Gemini 2.0 Flash / Claude / PyTorch rules]
- Infrastructure: [GKE Deployment / Cloud Run]
- Storage: [Redis cache / PostgreSQL rules DB]

**Deployment:**
- Mode: Always-on (synchronous API)
- Replicas: [X] (horizontal autoscaling)
- Scaling triggers: CPU >[X]% or RPS >[Y]

## Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Latency (p99) | ≤[X]ms | [Actual] | ✅/⚠️/❌ |
| Throughput | ≥[Y] rps | [Actual] | ✅/⚠️/❌ |
| Block Rate | ≥[Z]% violations | [Actual] | ✅/⚠️/❌ |
| False Positives | ≤[X]% | [Actual] | ✅/⚠️/❌ |
| False Negatives | ≤[Y]% | [Actual] | ✅/⚠️/❌ |
| Test Coverage | ≥[Z]% | [Actual] | ✅/⚠️/❌ |

## Quality Gates

**Accuracy:**
- Precision: [TP / (TP + FP)] ≥[X]%
- Recall: [TP / (TP + FN)] ≥[Y]%
- F1 Score: [2 × Precision × Recall / (Precision + Recall)] ≥[Z]

**Performance:**
- p50 latency: ≤[X]ms
- p95 latency: ≤[Y]ms
- p99 latency: ≤[Z]ms

**Reliability:**
- Uptime: ≥[X]%
- Error rate: ≤[Y]%

## Cost Model

**Per-Operation:**
- AI API call: $[X]/request
- Cache lookup: $[Y]/request
- **Total:** $[X+Y]/validation

**Monthly (at [X]M validations):**
- API costs: $[X]
- Infrastructure: $[Y]
- **Total:** $[X+Y]/month

## Integration

**Called By:**
- [Service 1]: [Validation type]
- [Service 2]: [Validation type]

**Calls:**
- [Rules DB]: [Lookup compliance rules]
- [Audit Log]: [Record decisions]

**Failure Mode:**
- If validator down: [Fail-open / Fail-closed]
- Mitigation: [Cached rules / Circuit breaker]

## Optimization Opportunities

1. **Cache common validation patterns**
   - Impact: -[X]% API calls → Save $[Y]/month
   - Effort: [X] days
   - ROI: [X]×

2. **Batch requests**
   - Impact: -[X]ms latency
   - Effort: [X] weeks
   - ROI: [Y]×

## Confidence: [X]% ([Production metrics / Specs only])
```

---

## Template 3: Transformation/Processing Component

**Use for:** Data pipelines, ETL jobs, enrichment services

```markdown
# Component Analysis: [Component Name] (Transformation)

## Identity
- **Role:** Transformation (process/enrich data)
- **Version:** [X.Y.Z]
- **Stack Position:** Midstream (receives from [X], outputs to [Y])

## Architecture
**Stack:**
- Language: [Python 3.11 / Scala / Java]
- Framework: [Apache Beam / Spark / Custom]
- Infrastructure: [Dataflow / GKE / Cloud Functions]
- Storage: [BigQuery / PostgreSQL / Cloud Storage]

**Deployment:**
- Mode: [Batch / Streaming / Hybrid]
- Schedule: [Hourly / Daily / Event-driven]
- Scaling: [Autoscaling workers]

## Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Processing Speed | ≥[X] records/sec | [Actual] | ✅/⚠️/❌ |
| Schema Compliance | ≥[Y]% | [Actual] | ✅/⚠️/❌ |
| Data Completeness | ≥[Z]% | [Actual] | ✅/⚠️/❌ |
| Error Rate | ≤[X]% | [Actual] | ✅/⚠️/❌ |
| Latency (end-to-end) | ≤[Y] min | [Actual] | ✅/⚠️/❌ |

## Quality Gates

**Data Quality:**
- Valid records: ≥[X]%
- Duplicate detection: [X]% caught
- Null value handling: [Strategy]

**Performance:**
- Throughput: [X] GB/hour
- CPU efficiency: [X]% utilization
- Memory usage: <[Y] GB

## Cost Model

**Per-Job:**
- Compute: $[X]/run
- Storage: $[Y]/month
- **Total:** $[X+Y]

**Monthly (at [X] jobs):**
- Total cost: $[Z]
- Cost per record: $[W]

## Optimization Opportunities

1. **Parallel processing**
   - Impact: +[X]% speed
   - Effort: [X] days
   - Cost: [Neutral / +$Y]

2. **Schema optimization**
   - Impact: -[X]% storage costs
   - Effort: [X] weeks
   - Savings: $[Y]/month

## Confidence: [X]%
```

---

## Template 4: Delivery/Presentation Component

**Use for:** API endpoints, reporting services, notification systems

```markdown
# Component Analysis: [Component Name] (Delivery)

## Identity
- **Role:** Delivery (present data to users/systems)
- **Version:** [X.Y.Z]
- **Stack Position:** Downstream (consumes from [X] services)

## Architecture
**Stack:**
- Language: [TypeScript 5.0 / Python 3.11]
- Framework: [Express / FastAPI / Next.js]
- Infrastructure: [Cloud Run / GKE / Vercel]
- Storage: [PostgreSQL / Redis cache]

**Deployment:**
- Mode: Always-on (REST API / Server-side rendering)
- Scaling: [Autoscaling / Serverless]
- CDN: [Cloudflare / Cloud CDN]

## Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Response Time (p95) | ≤[X]ms | [Actual] | ✅/⚠️/❌ |
| Availability | ≥[Y]% | [Actual] | ✅/⚠️/❌ |
| Error Rate | ≤[Z]% | [Actual] | ✅/⚠️/❌ |
| User Satisfaction | ≥[X]/5 | [Actual] | ✅/⚠️/❌ |
| Actionability | ≥[Y]% CTR | [Actual] | ✅/⚠️/❌ |

## Quality Gates

**Format Quality:**
- Readability: [Markdown / HTML / JSON]
- Structure: [Clear sections, bullet points]
- Length: [Target: X words]

**Timeliness:**
- Delivery time: [HH:MM daily]
- Success rate: ≥[X]%
- Retry logic: [Exponential backoff]

**Actionability:**
- Click-through rate: ≥[X]%
- Follow-up actions: [X]% of deliveries
- User feedback: [Qualitative insights]

## Cost Model

**Monthly:**
- Infrastructure: $[X]
- CDN: $[Y]
- **Total:** $[X+Y]

**Per-User:**
- Cost: $[Z]/user/month
- LTV: $[W] (if revenue-generating)

## Optimization Opportunities

1. **Cache static content**
   - Impact: -[X]ms latency
   - Effort: [X] days
   - Savings: $[Y]/month (CDN costs)

2. **Personalization**
   - Impact: +[X]% CTR
   - Effort: [X] weeks
   - Revenue impact: +$[Y]/month

## Confidence: [X]%
```

---

## Quick Selection Guide

Use this decision tree to pick the right template:

```
What does your component do?
│
├─ Gathers data from external sources
│  → Use Template 1: Collection/Ingestion
│
├─ Validates requests or enforces policies
│  → Use Template 2: Validation/Enforcement
│
├─ Processes/transforms/enriches data
│  → Use Template 3: Transformation/Processing
│
├─ Presents data to users or systems
│  → Use Template 4: Delivery/Presentation
│
└─ Hybrid (multiple roles)
   → Use Template 1 + Template 3 (Collection + Transformation)
   → Or create custom template combining sections
```

---

## Filling Out Templates: Step-by-Step

### Step 1: Gather Data

**Required Information:**
- Component name and version
- Architecture diagram (or create one)
- Current metrics (if in production)
- Cost breakdown (monthly operational)

**Optional (but helpful):**
- User feedback
- Historical performance trends
- Optimization backlog

### Step 2: Fill Template

1. Start with **Identity** section (easiest)
2. Fill **Architecture** (refer to deployment configs)
3. Add **Key Metrics** (use production dashboards or specs)
4. Complete **Quality Gates** (define success criteria)
5. Calculate **Cost Model** (use billing dashboards)
6. Identify **Optimization Opportunities** (brainstorm with team)

### Step 3: Run AI Analysis

Use the completed template as input to Gemini 2.0 Pro or Claude:

```
Prompt:
Analyze the following SHADOWTAGAI component using the provided template.
Provide actionable recommendations for optimization, identify risks,
and assign a confidence score (0-100%) based on data availability.

[Paste filled template]

Focus on:
1. Performance bottlenecks
2. Cost reduction strategies
3. Architectural improvements
4. Risk assessment (SPOF, failure modes)
```

### Step 4: Review and Iterate

- Validate AI recommendations with team
- Prioritize by ROI and effort
- Schedule follow-up analysis (quarterly for stable components, monthly for new ones)

---

**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi Engineering
**Templates:** 4 (Collection, Validation, Transformation, Delivery)
