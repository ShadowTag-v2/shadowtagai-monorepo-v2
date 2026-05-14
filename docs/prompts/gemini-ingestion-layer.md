# Gemini Ingestion Layer Analysis Prompt

## Overview

This document defines the analysis prompt for the **Gemini Ingestion Layer** component of the PNKLN Core Stack™. The prompt is structured using the [KERNEL framework](../frameworks/KERNEL.md) to ensure reproducible, verifiable, and high-quality analysis results.

## Evolution from Judge #6

This prompt evolved from the Judge #6 validation system prompt by adapting it for an intelligence collection pipeline rather than an enforcement/validation system. Key philosophical shifts:

- **From**: Reactive validator (Judge #6)
- **To**: Proactive collector (Ingestion Layer)
- **Focus**: Defensive speed/blocking → Acquisitive volume/diversity/efficiency

## Architecture Context

### Gemini Ingestion Layer Characteristics

| Aspect | Description |
|--------|-------------|
| **Architecture** | GKE CronJob with multi-container pods |
| **Execution Pattern** | Nightly batch processing (~45 min runtime) |
| **Integration Role** | Called by services in 4 namespaces (foundational layer) |
| **Key Metrics** | Items/day, source diversity, cost/item, relevance scores |
| **Cost Model** | Monthly operational budget: ~$77 |
| **Quality Focus** | Relevance, timeliness, completeness |

### Unique Features

1. **Ethical Crawling**: robots.txt compliance, rate limiting, transparency
2. **Tier Classification**: Prioritized data classification (Tier 1/2/3)
3. **Multi-Source Coverage**: YouTube, Twitter, News, Web, RSS feeds
4. **AM Briefing Integration**: Morning intelligence summaries

---

## The Prompt (KERNEL-Structured)

### CONTEXT

```
You are analyzing the Gemini Ingestion Layer, a pre-production intelligence collection
pipeline within the PNKLN Core Stack™.

INPUT ARTIFACTS:
- Pipeline architecture documentation (GKE CronJob specs)
- Multi-source configuration files (YouTube, Twitter, News, Web)
- Ethical crawling policies (robots.txt, rate limiting)
- Tier classification schemas (Tier 1/2/3 definitions)
- Cost monitoring dashboards (~$77/month budget)

CURRENT STATE:
- Pre-production environment (no live telemetry data)
- Analysis based on specifications and design documents
- Target runtime: ~45 minutes/night for batch processing
- Integration: Serves 4 downstream namespaces

ANALYSIS MODEL:
- Gemini 2.0 Pro with natural language reasoning
- Focus on strategic intelligence quality over raw speed
```

### TASK

```
Perform a comprehensive pre-production analysis of the Gemini Ingestion Layer across
six critical dimensions:

1. ETHICAL COMPLIANCE MODEL
   - Evaluate robots.txt adherence mechanisms
   - Assess rate limiting implementation
   - Review transparency/attribution practices
   - Identify legal/compliance risks

2. MULTI-SOURCE COVERAGE ANALYSIS
   - Measure source diversity (YouTube, Twitter, News, Web, RSS)
   - Identify coverage gaps or biases
   - Evaluate source reliability tiers
   - Recommend expansion opportunities

3. TIER CLASSIFICATION METRICS
   - Analyze Tier 1/2/3 distribution
   - Assess value-to-volume ratios
   - Evaluate classification accuracy (if test data available)
   - Optimize for high-value data (Tier 1 prioritization)

4. RUNTIME EFFICIENCY
   - Project nightly runtime against 45-minute target
   - Identify parallelization opportunities in GKE
   - Assess resource allocation (CPU, memory, network)
   - Detect potential bottlenecks

5. COST OPTIMIZATION
   - Validate against $77/month budget
   - Calculate cost-per-item projections
   - Model sensitivity to scale changes (2x, 5x, 10x volume)
   - Recommend cost reduction strategies

6. AM BRIEFING DELIVERY EFFECTIVENESS
   - Evaluate briefing format and structure
   - Assess timeliness (morning delivery SLA)
   - Review relevance filtering for end users
   - Validate completeness of intelligence summaries

OUTPUT:
- Structured analysis report (see FORMAT section below)
- Confidence-weighted findings
- Actionable recommendations prioritized by impact
```

### CONSTRAINTS

```
TECHNICAL CONSTRAINTS:
- Analysis based on pre-production specs only (no live metrics)
- Must work with documentation, architecture diagrams, config files
- No access to production telemetry or logs

QUALITY CONSTRAINTS:
- Minimum confidence threshold: ≥60% for all findings
  (Rationale: Pre-prod specs have more assumptions than prod data)
- Flag uncertainties explicitly when confidence <60%
- Distinguish between spec-based analysis vs. assumption-based projections

SCOPE CONSTRAINTS:
- Focus on the 6 dimensions listed in TASK (do not expand)
- Do NOT analyze downstream services (only ingestion layer)
- Do NOT perform Judge #6 validation tasks (different component)

ETHICAL CONSTRAINTS:
- Prioritize ethical crawling compliance
- Flag any practices that violate web standards
- Recommend transparency improvements

AVOID:
- Real-time latency metrics (not applicable to batch processing)
- False positive/negative rates (Judge #6 metrics, not ingestion)
- API call-per-validation costs (wrong cost model)
- Enforcement/blocking analysis (wrong component type)
```

### OUTPUT FORMAT

```
# Gemini Ingestion Layer Analysis Report

## Executive Summary
[3-5 bullet points: key findings, critical risks, top recommendations]

## 1. Ethical Compliance Model
### Findings
- [Finding 1] (Confidence: X%)
- [Finding 2] (Confidence: X%)

### Risks
- [Risk 1: severity level]
- [Risk 2: severity level]

### Recommendations
1. [Action item with expected impact]
2. [Action item with expected impact]

## 2. Multi-Source Coverage Analysis
[Same structure as section 1]

## 3. Tier Classification Metrics
[Same structure as section 1]

## 4. Runtime Efficiency
### Projected Runtime: X minutes (Target: 45 min)
[Same structure as section 1]

## 5. Cost Optimization
### Projected Monthly Cost: $X (Budget: $77)
### Cost per Item: $X
[Same structure as section 1]

## 6. AM Briefing Delivery Effectiveness
[Same structure as section 1]

## Cross-Cutting Concerns
[Dependencies, integration risks, architectural recommendations]

## Prioritized Action Items
1. [HIGH] Action item (Impact: X, Effort: Y)
2. [MEDIUM] Action item (Impact: X, Effort: Y)
3. [LOW] Action item (Impact: X, Effort: Y)

## Confidence Assessment
- Overall analysis confidence: X%
- Sections with <60% confidence: [list]
- Recommended next steps to increase confidence: [list]

## Appendices
- A: Source diversity breakdown
- B: Tier classification distribution
- C: Cost sensitivity analysis (tables/charts)
```

### VERIFICATION CRITERIA

```
The analysis is complete and successful if:

✓ All 6 dimensions analyzed with structured findings
✓ Every finding includes confidence percentage
✓ Recommendations are actionable (not vague suggestions)
✓ Cost projections include sensitivity analysis
✓ Ethical compliance section addresses robots.txt + rate limiting + transparency
✓ Output follows the exact format specified above
✓ Overall confidence ≥60% OR uncertainties flagged with mitigation plans
✓ No Judge #6 metrics included (latency, FP/FN rates, blocking)
✓ No downstream service analysis (ingestion layer only)
✓ Prioritized action items ranked by impact/effort

REJECTION CRITERIA:
✗ Findings without confidence scores
✗ Vague recommendations ("improve performance", "optimize costs")
✗ Missing any of the 6 required dimensions
✗ Confusion between ingestion metrics and Judge #6 metrics
✗ Unsupported speculation (confidence <60% without flagging)
```

---

## Key Differences from Judge #6 Prompt

### Direct Replacements

| Judge #6 | Gemini Ingestion Layer | Rationale |
|----------|------------------------|-----------|
| Judge #6 (everywhere) | Gemini Ingestion Layer | Domain re-focus |
| `judge_six.py` | Pipeline docs, architecture specs | Broader artifact scope |
| p99 ≤90ms latency | ~45 min/night runtime | Batch vs. real-time |
| 98% test coverage | Quality gates (items, sources, costs, scores) | Holistic quality measures |

### Context-Specific Adaptations

| Dimension | Judge #6 | Gemini Ingestion Layer | Impact |
|-----------|----------|------------------------|--------|
| **Architecture** | Hybrid Gemini+PyTorch | GKE CronJob multi-container | Emphasize orchestration, fault tolerance |
| **Key Metrics** | Latency, throughput, block rate | Items/day, sources, cost/item | From defensive to acquisitive |
| **Integration** | Calls services in 4 namespaces | Called by services in 4 namespaces | Foundational layer analysis |
| **Unique Features** | ATP 5-19, JR validation | Ethical crawling, tier classification | Compliance + strategic prioritization |
| **Cost Model** | API calls per validation | Monthly operational ~$77 | Budget-based vs. per-operation |
| **Quality Focus** | FP/FN rates | Relevance, timeliness, completeness | Binary errors → holistic quality |

### New Sections Added

These enhance the ingestion-specific analysis:

1. **Ethical Compliance Model**
   - robots.txt adherence
   - Rate limiting policies
   - Transparency requirements
   - **Why**: Legal risk mitigation for web crawling

2. **Multi-Source Coverage Analysis**
   - YouTube, Twitter, News, Web, RSS
   - Source diversity metrics
   - Bias detection
   - **Why**: Prevent intelligence silos, ensure broad coverage

3. **Tier Classification Metrics**
   - Tier 1/2/3 distribution
   - Value-to-volume ratios
   - Prioritization effectiveness
   - **Why**: Strategic resource allocation to high-value data

4. **AM Briefing Delivery Effectiveness**
   - Format and structure
   - Timeliness (morning SLA)
   - Relevance filtering
   - **Why**: End-to-end validation of pipeline output

### Confidence Adjustments

- **Judge #6**: ≥70% confidence (with production data)
- **Ingestion Layer**: ≥60% confidence (specs only, pre-production)
- **Rationale**: Pre-prod analysis lacks real-world telemetry, requires lower threshold

---

## KERNEL Compliance Analysis

### K - Keep it Simple ✓
- Clear goal: "Analyze the Gemini Ingestion Layer across 6 dimensions"
- No verbose context dumps
- Direct objective statement

### E - Easy to Verify ✓
- Specific success criteria: All 6 dimensions analyzed, confidence ≥60%
- Measurable outputs: Cost projections, runtime estimates, tier distributions
- Clear rejection criteria defined

### R - Reproducible Results ✓
- No temporal references ("current trends", "latest")
- Specific versions: Gemini 2.0 Pro, PNKLN Core Stack™
- Exact specifications referenced (GKE CronJob, $77 budget, 45 min runtime)

### N - Narrow Scope ✓
- Single goal: Analyze ingestion layer (not downstream services)
- Explicitly excludes Judge #6 metrics
- Focused on 6 defined dimensions only

### E - Explicit Constraints ✓
- Technical: Pre-prod specs only, no live telemetry
- Quality: ≥60% confidence threshold
- Scope: Do NOT analyze downstream services
- Avoid: Judge #6 metrics, real-time latency, enforcement analysis

### L - Logical Structure ✓
- Context: Input artifacts, current state, analysis model
- Task: 6 dimensions with specific analysis requirements
- Constraints: Technical, quality, scope, ethical, avoidances
- Format: Structured report template with sections
- Verification: Success criteria and rejection criteria

---

## Implementation Notes

### For Gemini 2.0 Pro

**Strengths**:
- Excellent with natural language reasoning
- Strong ethical analysis capabilities
- Good at multi-dimensional analysis

**Recommendations**:
- Provide architecture diagrams if available (visual input)
- Use structured tables in input docs for better parsing
- Consider adding example findings to calibrate output tone

### For Test Runs

Before production deployment:

1. **Calibration**: Run on dummy specs to validate Gemini's handling of ethical sections
2. **Visualization**: Request tables/charts for tier distributions and cost sensitivity
3. **Edge Cases**: Include failure scenarios (source outages, cost spikes) in specs
4. **Integration**: Test handoff analysis with Judge #6 prompt for end-to-end flow

---

## Integration with PNKLN Core Stack™

### Upstream Dependencies
- None (ingestion is foundational layer)

### Downstream Consumers
- Services in 4 namespaces (not analyzed by this prompt)
- Judge #6 validation system (separate prompt)
- AM Briefing delivery system

### Cross-Prompt Synergy
- **Judge #6 Prompt**: Validates ingested data quality
- **Combined Analysis**: Could analyze handoff between ingestion → validation
- **Future**: API Service prompts for namespace integration analysis

---

## Metrics for Success

Track these metrics when deploying the prompt:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Analysis completion rate | 100% | All 6 dimensions covered |
| Average confidence score | ≥60% | Mean of all findings |
| Actionable recommendations | ≥3 per dimension | Count of specific action items |
| False uncertainty rate | <20% | Manual review of <60% confidence flags |
| Time to generate report | <5 minutes | Gemini API response time |

---

## Version History

- **v1.0** (2025-11-15): Initial prompt based on Judge #6 adaptation
- **Source**: Judge #6 v1.0 with ingestion-specific modifications
- **Framework**: KERNEL v1.0 compliant

---

## Next Steps

1. **Deploy to Test**: Run analysis on pre-prod specs
2. **Calibrate Confidence**: Adjust ≥60% threshold based on results
3. **Visualize Outputs**: Add chart/diagram generation requests
4. **Integrate with Judge #6**: Cross-analyze ingestion → validation handoff
5. **Prepare for Prod**: Update to ≥70% confidence when live telemetry available

---

## References

- [KERNEL Framework](../frameworks/KERNEL.md)
- [Judge #6 Prompt](./judge-six.md) (comparison baseline)
- PNKLN Core Stack™ Architecture Documentation
- Gemini 2.0 Pro API Documentation

---

## Appendix: Design Rationale

### Why These 6 Dimensions?

1. **Ethical Compliance**: Legal necessity for web crawling
2. **Multi-Source Coverage**: Intelligence diversity requirement
3. **Tier Classification**: Strategic value optimization
4. **Runtime Efficiency**: Operational constraint (nightly window)
5. **Cost Optimization**: Budget sustainability
6. **AM Briefing**: End-user value validation

### Why ≥60% Confidence for Pre-Prod?

Pre-production analysis relies on specs, not telemetry. Lower threshold acknowledges:
- More assumptions required
- Less empirical data available
- Design validation vs. performance validation

Once in production with real metrics, raise to ≥70% to match Judge #6 standard.

### Why Separate from Judge #6?

Different roles in pipeline:
- **Ingestion**: Preventive, upstream, collection-focused
- **Judge #6**: Reactive, downstream, enforcement-focused

Conflating them creates confused prompts optimizing for contradictory goals.
