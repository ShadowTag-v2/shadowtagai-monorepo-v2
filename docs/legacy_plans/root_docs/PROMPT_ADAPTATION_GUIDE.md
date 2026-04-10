# Prompt Adaptation Guide for PNKLN Core Stack™

## Overview

This guide demonstrates how to adapt prompts between different use cases while maintaining analytical rigor, using the **Prompt Adaptation Specialist** agent. Based on real-world examples from the PNKLN Core Stack™, particularly the transformation from "Judge #6" (validation system) to "Gemini Ingestion Layer" (intelligence collection pipeline).

---

## Table of Contents

1. [Decision Framework](#decision-framework)
2. [Adaptation Methodology](#adaptation-methodology)
3. [Case Study: Judge #6 → Gemini Ingestion Layer](#case-study-judge-6--gemini-ingestion-layer)
4. [Direct Replacements](#direct-replacements)
5. [Context-Specific Adaptations](#context-specific-adaptations)
6. [New Sections to Add](#new-sections-to-add)
7. [Confidence Calibration](#confidence-calibration)
8. [Validation & Testing](#validation--testing)
9. [PNKLN Stack Patterns](#pnkln-stack-patterns)

---

## Decision Framework

Before adapting any prompt, understand the domain shift:

### Source vs. Target Analysis

| Dimension        | Source (Judge #6)    | Target (Ingestion Layer) |
| ---------------- | -------------------- | ------------------------ |
| **Role**         | Reactive/Enforcement | Preventive/Upstream      |
| **Function**     | Validate & Block     | Collect & Curate         |
| **Timing**       | Real-time            | Batch (nightly cron)     |
| **Metrics**      | Speed & Accuracy     | Volume & Quality         |
| **Architecture** | Hybrid AI            | Containerized GKE        |
| **Integration**  | Calls services       | Called by services       |

**Key Insight**: 95% of GenAI pilots fail to scale because they lack disciplined engineering. Prompt adaptation must preserve analytical structure while tailoring to operational reality.

---

## Adaptation Methodology

### 4-Step Process

```
1. ANALYZE DOMAINS
   ↓ What changed? What stayed the same?

2. MAP EQUIVALENTS
   ↓ Concepts, not just words

3. ADAPT STRUCTURE
   ↓ Preserve analytical rigor

4. VALIDATE & TEST
   ↓ Ensure domain relevance
```

### Adaptation Checklist

- [ ] Identified direct replacements (terminology, files, metrics)
- [ ] Mapped context-specific elements (architecture, integration)
- [ ] Added domain-specific sections (compliance, coverage)
- [ ] Calibrated confidence targets (pre-prod vs. prod)
- [ ] Preserved prompt structure and analytical depth
- [ ] Tested with sample data
- [ ] Documented assumptions and uncertainties

---

## Case Study: Judge #6 → Gemini Ingestion Layer

### Context

**Judge #6**: A hybrid Gemini+PyTorch validation system that enforces quality gates in real-time, blocking invalid requests across 4 namespaces. Optimized for p99 ≤90ms latency with 98% test coverage.

**Gemini Ingestion Layer**: A GKE-based CronJob system that ethically collects intelligence from multiple sources (YouTube, Twitter, News, Web) nightly, classifying by tier and delivering AM briefings. Runtime target: ~45 min/night, cost: ~$77/month.

### Why Adaptation Makes Sense

Both systems analyze components in the PNKLN Core Stack™, but at different pipeline stages:

- **Judge #6**: Downstream validation (defensive)
- **Ingestion Layer**: Upstream collection (acquisitive)

The analytical framework (architecture review, metrics evaluation, integration analysis) remains valuable, but the specifics must change to match operational realities.

---

## Direct Replacements

### 1. System Names & Identifiers

| Source              | Target                 | Rationale                  |
| ------------------- | ---------------------- | -------------------------- |
| Judge #6            | Gemini Ingestion Layer | Domain-specific identifier |
| ATP 5-19 validation | Ethical crawling       | Unique feature swap        |
| JR Validation       | Tier classification    | Strategic prioritization   |

**Implementation**:

```python
# Find and replace ALL occurrences
sed -i 's/Judge #6/Gemini Ingestion Layer/g' prompt.txt
sed -i 's/ATP 5-19/ethical crawling compliance/g' prompt.txt
```

### 2. File References

| Source           | Target                      | Rationale                      |
| ---------------- | --------------------------- | ------------------------------ |
| `judge_six.py`   | Pipeline architecture specs | Single file → distributed docs |
| Unit test files  | Integration diagrams        | Code → system design           |
| Coverage reports | Source diversity metrics    | Quality measure shift          |

**Why Broader?**
Ingestion layers are more distributed than single-script validators. Analyzing flowcharts, Kubernetes configs, and cron job specs provides deeper insights into dependencies and bottlenecks.

### 3. Performance Metrics

| Source            | Target                 | Rationale               |
| ----------------- | ---------------------- | ----------------------- |
| p99 latency ≤90ms | Runtime ≤45 min/night  | Real-time → batch       |
| Requests/second   | Items/day              | Throughput context      |
| Block rate %      | Source diversity count | Defensive → acquisitive |

**Critical**: Don't force inapplicable SLAs. Batch processing cares about total runtime, not per-request latency.

**Example Transformation**:

```markdown
<!-- BEFORE: Judge #6 -->

Evaluate performance:

- p99 latency ≤90ms
- Throughput ≥1000 req/sec
- Block rate ≤5%

<!-- AFTER: Ingestion Layer -->

Evaluate performance:

- Runtime efficiency ≤45 min/night
- Items ingested ≥500/day
- Source diversity ≥5 types
```

### 4. Quality Gates

| Source            | Target                                         | Rationale                        |
| ----------------- | ---------------------------------------------- | -------------------------------- |
| 98% test coverage | Quality gates on items, sources, costs, scores | Quantity → multi-faceted quality |
| FP/FN error rates | Relevance, timeliness, completeness            | Binary → dimensional             |

**Why Multi-Faceted?**
Ingestion optimizing solely for "how much" creates garbage. Measuring daily items, source diversity, per-item costs, and scoring (relevance) prevents over-optimization for quantity at the expense of downstream usability.

---

## Context-Specific Adaptations

### Architecture Pattern Shift

#### Judge #6 (Hybrid AI - Real-time)

```yaml
Architecture: Hybrid Gemini+PyTorch
Pattern: Synchronous request/response
Deployment: Always-on service
Scaling: Horizontal pod autoscaling
```

#### Ingestion Layer (Containerized Cron - Batch)

```yaml
Architecture: GKE CronJob, Multi-Container
Pattern: Scheduled batch processing
Deployment: Ephemeral containers
Scaling: Parallelization across sources
```

**Adaptation Guidance**:

- Analyze fault tolerance (what if a cron job fails?)
- Evaluate resource allocation (how to handle variable volumes?)
- Assess orchestration (Kubernetes job management)

### Key Metrics Alignment

#### Judge #6 (Defensive Metrics)

```
Focus: Speed + Blocking Effectiveness
- Latency (how fast can we decide?)
- Throughput (how many can we handle?)
- Block rate (how well do we protect?)
```

#### Ingestion Layer (Acquisitive Metrics)

```
Focus: Volume + Diversity + Efficiency
- Items/day (how much do we collect?)
- Sources (how diverse is our coverage?)
- Cost/item (how efficiently?)
- Tier distribution (how valuable?)
```

**Prompt Transformation**:

```markdown
<!-- BEFORE -->

Analyze metrics:

1. Measure p99 latency across endpoints
2. Calculate throughput under load
3. Evaluate false positive/negative rates

<!-- AFTER -->

Analyze metrics:

1. Track daily item ingestion volume
2. Assess source diversity (YouTube, Twitter, News, Web)
3. Calculate cost per item and per source
4. Evaluate tier classification distribution (Tier 1/2/3)
```

### Integration Direction Flip

#### Judge #6: Caller (Downstream)

```
Judge #6 → Calls Services in 4 Namespaces
- Makes validation requests to upstream systems
- Blocks based on responses
- Acts as gatekeeper
```

#### Ingestion Layer: Callee (Upstream)

```
Services in 4 Namespaces → Call Ingestion Layer
- Triggered by external schedulers
- Provides data to downstream consumers
- Acts as foundation layer
```

**Prompt Adaptation**:

```markdown
<!-- BEFORE -->

Integration Analysis:

- Which services does the system call?
- What are the API contracts?
- How are failures handled?

<!-- AFTER -->

Integration Analysis:

- Which services invoke the ingestion layer?
- What triggers initiate data collection?
- How is data handed off downstream?
- What integration pain points exist?
```

### Cost Model Transformation

#### Judge #6: Per-Operation

```
Cost Model: API calls × $0.002/call
Focus: Marginal cost per validation
Optimization: Reduce unnecessary calls
```

#### Ingestion Layer: Monthly Operational

```
Cost Model: ~$77/month total
Focus: Fixed operational budget
Optimization: Scale sensitivity analysis
```

**Prompt Enhancement**:

```markdown
<!-- BEFORE -->

Cost Analysis:

- Calculate cost per validation
- Identify high-cost endpoints
- Optimize API usage

<!-- AFTER -->

Cost Analysis:

- Monthly operational total: ~$77
- Cost per item ingested
- Sensitivity to volume changes (what if 2x items?)
- Budget sustainability at scale
```

---

## New Sections to Add

### 1. Ethical Compliance Model

**Why**: Crawler-based ingestion demands legal compliance.

**Template**:

```markdown
## Ethical Compliance Evaluation

### robots.txt Adherence

- ☐ Fetch and parse before crawling
- ☐ Respect all User-agent directives
- ☐ Honor Crawl-delay specifications
- ☐ Regular cache updates

### Rate Limiting & Politeness

- ☐ Per-domain rate limits (≤2 req/sec)
- ☐ Exponential backoff on errors
- ☐ Respect Retry-After headers
- ☐ Distribute load across time

### Transparency

- ☐ Clear User-Agent identification
- ☐ Contact information provided
- ☐ Opt-out mechanism available
- ☐ Purpose statement

### Risk Assessment

- High Risk: {identified issues}
- Medium Risk: {minor concerns}
- Low Risk: {compliant areas}

Compliance Score: \_\_/100
```

### 2. Multi-Source Coverage Analysis

**Why**: Diversity prevents bias and silos.

**Template**:

```markdown
## Multi-Source Coverage Analysis

### Source Distribution

| Source Type | Items/Day | % of Total | Quality Tier |
| ----------- | --------- | ---------- | ------------ |
| YouTube     | 150       | 30%        | Tier 1       |
| Twitter     | 200       | 40%        | Tier 2       |
| News Sites  | 100       | 20%        | Tier 1       |
| Web Crawl   | 50        | 10%        | Tier 3       |

### Diversity Metrics

- Source types: {count}
- Geographic coverage: {regions}
- Language distribution: {languages}
- Temporal spread: {time range}

### Bias Detection

- Over-reliance on: {source type}
- Coverage gaps: {missing sources}
- Recommendations: {expansion opportunities}
```

### 3. Tier Classification Metrics

**Why**: Quantify data value distribution.

**Template**:

```markdown
## Tier Classification Analysis

### Distribution

- Tier 1 (High Value): \_\_%
  - Characteristics: {criteria}
  - Sources: {primary sources}

- Tier 2 (Medium Value): \_\_%
  - Characteristics: {criteria}
  - Sources: {sources}

- Tier 3 (Low Value): \_\_%
  - Characteristics: {criteria}
  - Action: Consider filtering

### Value Assessment

- Is 80% low-tier junk? → Tune crawlers for Tier 1
- ROI per tier: {calculations}
- Optimization: {recommendations}
```

### 4. AM Briefing Delivery Effectiveness

**Why**: End-to-end pipeline validation.

**Template**:

```markdown
## Briefing Delivery Analysis

### Format Effectiveness

- Structure: {clear/confusing}
- Readability: {score}
- Actionability: {score}

### Timeliness

- Target delivery: 6:00 AM
- Actual delivery: {time}
- Variance: {delta}

### User Feedback

- Relevance: {score}
- Completeness: {score}
- Suggested improvements: {list}
```

---

## Confidence Calibration

### Pre-Production (Specs-Only)

**Target**: ≥60% confidence

**Rationale**:
Without production telemetry, analysis relies on documentation and architecture specs. More assumptions = lower certainty.

```markdown
## Confidence Calibration Notes

Data Available:

- ✓ Architecture diagrams
- ✓ Code repository
- ✓ Configuration files
- ✗ Production metrics
- ✗ Real user data
- ✗ Operational logs

Confidence Target: ≥60%
Justification: Pre-prod, specs-only analysis
Plan: Increase to ≥70% post-deployment
```

### Production (With Telemetry)

**Target**: ≥70% confidence

**Rationale**:
Real-world data reduces uncertainty. Logs, metrics, and user feedback enable evidence-based analysis.

```markdown
## Confidence Calibration Notes

Data Available:

- ✓ Architecture diagrams
- ✓ Code repository
- ✓ Configuration files
- ✓ Production metrics (7 days)
- ✓ User feedback
- ✓ Error logs and traces

Confidence Target: ≥70%
Justification: Production data available
Uncertainty Areas: {list}
```

---

## Validation & Testing

### Test Runs Before Deployment

1. **Dummy Specs Test**

   ```bash
   # Run analysis on sample documentation
   python test_prompt.py --mode dummy-specs
   ```

2. **Gemini Calibration**
   - Does it handle ethical sections well?
   - Are tier classifications logical?
   - Is confidence scoring reasonable?

3. **Edge Case Probing**

   ```markdown
   Test Scenarios:

   - Source outage (YouTube API down)
   - Cost spike (10x normal volume)
   - Tier distribution skew (90% Tier 3)
   - Compliance violation detection
   ```

### Visualization Requests

Enhance reports with visual outputs:

```markdown
Include in analysis:

1. **Tables**
   - Source distribution
   - Tier classification breakdown
   - Cost analysis

2. **Charts** (if possible)
   - Daily item trends
   - Source diversity over time
   - Cost per item by source

3. **Diagrams**
   - Data flow architecture
   - Integration touchpoints
   - Failure mode scenarios
```

---

## PNKLN Stack Patterns

### Component Complementarity

**Judge #6** and **Ingestion Layer** are complementary, not competitive:

```
┌─────────────────────────────────────┐
│   Intelligence Pipeline Flow        │
├─────────────────────────────────────┤
│                                     │
│  1. INGESTION LAYER (Upstream)      │
│     ↓ Collect & Curate              │
│     │ - Multi-source gathering      │
│     │ - Ethical compliance          │
│     │ - Tier classification         │
│     ↓                               │
│                                     │
│  2. JUDGE #6 (Validation)           │
│     ↓ Validate & Enforce            │
│     │ - ATP 5-19 checks             │
│     │ - JR validation               │
│     │ - Quality gates               │
│     ↓                               │
│                                     │
│  3. PROCESSING & DELIVERY           │
│     → AM Briefings                  │
│     → Analytics                     │
│     → Insights                      │
│                                     │
└─────────────────────────────────────┘
```

### Combined Analysis Prompt

For end-to-end flow analysis:

```markdown
## Cross-Component Integration Analysis

Analyze handoffs between:

1. Ingestion → Validation
   - Data format consistency
   - Quality preservation
   - Timing coordination

2. Validation → Processing
   - Pass-through rate
   - Error propagation
   - Bottleneck detection

3. End-to-End Health
   - Pipeline latency (collect → deliver)
   - Data loss checkpoints
   - Recovery mechanisms
```

---

## Best Practices Summary

### ✅ DO

1. **Map concepts, not just words**
   - "Latency" → "Runtime" (both measure speed, different contexts)
   - "Block rate" → "Source diversity" (both measure effectiveness)

2. **Preserve analytical structure**
   - Keep framework sections (Architecture, Metrics, Integration)
   - Maintain depth and rigor
   - Ensure measurable outcomes

3. **Tailor to operational reality**
   - Batch systems need runtime metrics, not latency
   - Collection systems need diversity metrics, not block rates

4. **Add domain-specific safeguards**
   - Ethical compliance for crawlers
   - Cost sensitivity for scaled systems
   - Tier classification for value optimization

5. **Test before deployment**
   - Sample data runs
   - Edge case scenarios
   - Gemini calibration checks

### ❌ DON'T

1. **Force incompatible metrics**
   - Don't apply real-time SLAs to batch jobs
   - Don't use validation metrics for collection systems

2. **Skip domain-specific sections**
   - Crawlers need ethical compliance analysis
   - Stack components need integration review

3. **Ignore confidence calibration**
   - Pre-prod needs lower targets (≥60%)
   - Production enables higher confidence (≥70%)

4. **Forget about testing**
   - Untested prompts create surprises
   - Edge cases reveal weaknesses

---

## Next Steps

1. **Deploy to Production**
   - Run adapted prompt on real specs
   - Capture Gemini outputs
   - Validate confidence scores

2. **Iterate Based on Results**
   - Refine unclear sections
   - Add missing edge cases
   - Calibrate confidence targets

3. **Expand Framework**
   - Create adaptation templates for other PNKLN components
   - Build reusable section libraries
   - Document common patterns

4. **Integration**
   - Combine Judge #6 + Ingestion Layer analysis for end-to-end view
   - Create cross-component dashboards
   - Enable holistic stack optimization

---

## Quick Reference

### Adaptation Agent Usage

```python
from agents import AgentRegistry

# Get the Prompt Adaptation agent
adapter = AgentRegistry.get_agent("prompt_adaptation")

# Execute adaptation task
result = await adapter.execute(
    task="Adapt Judge #6 prompt for Gemini Ingestion Layer analysis",
    context={
        "source_system": "Judge #6 (validation)",
        "target_system": "Gemini Ingestion Layer (collection)",
        "source_prompt": "...",  # Original prompt
        "requirements": [
            "Preserve analytical rigor",
            "Add ethical compliance section",
            "Change metrics to batch-oriented"
        ]
    }
)

print(result["prompt"])
```

### PNKLN Stack Analyzer Usage

```python
# Analyze specific component
analyzer = AgentRegistry.get_agent("pnkln_stack_analyzer")

result = await analyzer.execute(
    task="Analyze Gemini Ingestion Layer performance and integration",
    context={
        "component": "ingestion_layer",
        "specs": "...",
        "architecture_diagrams": "...",
        "current_metrics": {
            "items_per_day": 500,
            "runtime": "42 min",
            "cost_per_month": 77
        }
    }
)
```

---

## Conclusion

Prompt adaptation is not just find-and-replace—it's **domain-aware transformation** that preserves analytical value while ensuring relevance. By following this framework, you can:

- Transform prompts between PNKLN stack components
- Maintain structure and rigor
- Add domain-specific insights
- Calibrate expectations appropriately
- Deploy with confidence

**Remember**: The best adaptation maps equivalent concepts, not just swaps words. Think about _why_ each element exists in the original prompt, then find the equivalent _why_ in your target domain.

---

**Ready to adapt?** Use the agents:

- `prompt_adaptation` - Transform prompts between use cases
- `gemini_prompt_optimizer` - Optimize for Gemini 2.0 Pro
- `pnkln_stack_analyzer` - Analyze PNKLN components
- `prompt_quality_auditor` - Validate production readiness
- `ethical_crawler_auditor` - Ensure compliance

**Questions or improvements?** File an issue or contribute to the framework!
