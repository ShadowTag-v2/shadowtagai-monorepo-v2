# Judge 6 - Analysis Prompt Template

> Comprehensive analysis prompt for Gemini 2.0 Pro to evaluate the PNKLN Judge 6 validation component

## Prompt Structure

This prompt is designed for use with **Gemini 2.0 Pro** to conduct deep technical analysis of the Judge 6 enforcement and validation component within the PNKLN Core Stack™.

---

## Analysis Prompt

```markdown
You are a senior infrastructure architect and AI systems expert conducting a comprehensive production analysis of **Judge 6** for the PNKLN Core Stack™.

### Context

Judge 6 is an enforcement and validation system that provides real-time compliance checking for Compliance Framework standards and JR (Junction/Routing) validation. It operates as a hybrid Gemini + PyTorch architecture to deliver low-latency decisions on data validity before it progresses through the PNKLN pipeline.

**Target Performance**:

- Latency: p99 ≤90ms

- Coverage: 98% of validation cases

- Quality Gates: Low FP/FN rates, high throughput

**Integration**:

- Calls services across 4 namespaces

- Downstream validation layer

- Filters data before analytics/delivery

### Available Documentation

You have access to:

1. `Claude_Code_6.py` - main implementation file

2. Architecture specifications

3. Compliance Framework compliance documentation

4. JR validation rules

5. Production telemetry (logs, metrics, traces)

6. API cost breakdowns

### Analysis Objectives

Conduct a thorough evaluation covering:

#### 1. Architecture Analysis

Evaluate the Hybrid Gemini + PyTorch design:

- Model architecture and interaction patterns

- Gemini API usage patterns (prompts, contexts)

- PyTorch model characteristics (size, inference time)

- Hybrid decision logic (when to use which model)

- Scalability for concurrent requests

- Resource requirements (GPU, memory, CPU)

**Key Questions**:

- Why hybrid vs. single model approach?

- How are decisions routed between Gemini and PyTorch?

- What's the fallback if Gemini API is unavailable?

- Are models versioned and A/B tested?

#### 2. Latency Analysis

Assess the p99 ≤90ms target:

- Current p50, p95, p99, p999 latencies

- Latency breakdown (network, model inference, business logic)

- Outlier analysis (what causes slow requests?)

- Optimization opportunities

- Cache hit rates and effectiveness

**Key Questions**:

- What's the distribution of latencies?

- Which component contributes most to latency?

- Are there patterns in slow requests (time, input type)?

- How close are we to the 90ms target?

#### 3. Compliance Framework Compliance Validation

Evaluate enforcement of Compliance Framework standards:

- Coverage of Compliance Framework requirements

- Validation logic correctness

- Edge case handling

- Compliance reporting

- Audit trail generation

**Key Questions**:

- What % of Compliance Framework requirements are automated?

- How are compliance rules updated?

- Are there manual review escalations?

- How is compliance tracked over time?

#### 4. JR Validation Logic

Analyze Junction/Routing validation:

- JR rule definitions and structure

- Validation thoroughness

- Error messaging quality

- Performance impact of JR checks

- Rule versioning and updates

**Key Questions**:

- What does JR validation check specifically?

- How complex are JR rules (computational cost)?

- How often do JR rules change?

- Are JR failures logged for analysis?

#### 5. Accuracy & Error Rates

Evaluate False Positive and False Negative rates:

- Current FP rate (blocking valid data)

- Current FN rate (allowing invalid data)

- Error distribution by validation type

- Trends over time (improving/degrading?)

- Root cause analysis of errors

**Key Questions**:

- What's the acceptable FP/FN threshold?

- Which validation checks are most error-prone?

- How are errors detected (ground truth)?

- What's the feedback loop for improving accuracy?

#### 6. Throughput & Concurrency

Analyze request handling capacity:

- Current requests per second (RPS)

- Maximum observed throughput

- Concurrency limits

- Queue depth and wait times

- Rate limiting mechanisms

**Key Questions**:

- What's peak vs. average RPS?

- Are there throughput bottlenecks?

- How does latency degrade under load?

- What's the scaling strategy (horizontal/vertical)?

#### 7. Cost Model & Economics

Analyze API call costs and operational expenses:

- Cost per validation request

- Gemini API costs (calls, tokens)

- PyTorch inference costs (compute)

- Total monthly operational cost

- Cost optimization strategies

**Key Questions**:

- What drives the majority of cost?

- Gemini vs. PyTorch cost breakdown

- How does cost scale with volume?

- Are there wasteful API calls?

#### 8. Integration Patterns

Analyze interactions with PNKLN stack:

- Services called across 4 namespaces

- API contracts and protocols

- Dependency health monitoring

- Circuit breaker patterns

- Retry logic and idempotency

**Key Questions**:

- Which namespaces are called most frequently?

- What's the impact of downstream service failures?

- Are there timeout configurations?

- How are distributed traces correlated?

#### 9. Coverage Analysis

Evaluate the 98% validation coverage target:

- Current coverage % by validation type

- Uncovered edge cases

- Coverage gaps and why they exist

- Plan for reaching 100% coverage

- Coverage regression prevention

**Key Questions**:

- What's in the uncovered 2%?

- Are gaps intentional (manual review) or limitations?

- How is coverage measured and tracked?

- Are new validation cases added regularly?

#### 10. Resilience & Failure Modes

Identify and evaluate failure scenarios:

- Gemini API outages

- PyTorch model failures

- Downstream service unavailability

- High latency/timeout scenarios

- Data quality degradation

- Resource exhaustion (memory, CPU)

**Key Questions**:

- How are failures detected and alerted?

- What's the degraded mode strategy?

- Can the system fail open (allow) or closed (block)?

- How long can outages be tolerated?

- Are there cascading failure risks?

### Analysis Requirements


1. **Confidence Scoring**: Assign confidence ≥70% to each finding (production data available)

2. **Evidence-Based**: Reference specific telemetry, code, or documentation

3. **Actionable**: Provide concrete recommendations with ROI estimates

4. **Prioritized**: Rank issues by severity and impact

5. **Quantitative**: Use production metrics extensively

### Output Format

Structure your analysis as follows:

#### Executive Summary


- Overall health assessment (1-5 scale)

- Top 3 strengths

- Top 3 risks/concerns

- Optimization priority ranking

#### Detailed Findings by Category

For each of the 10 analysis areas above:

- **Status**: Green/Yellow/Red assessment

- **Confidence**: % confidence in assessment

- **Key Findings**: Bullet points with telemetry evidence

- **Risks Identified**: Specific issues with severity

- **Recommendations**: Prioritized actions with estimated impact

#### Metrics Summary Tables


- Latency percentiles (p50, p95, p99, p999)

- Throughput statistics (RPS, concurrency)

- Error rates (FP, FN) by validation type

- Cost breakdown by component

- Coverage % by validation category

#### Performance Trends


- Latency over time (improving/degrading?)

- Error rate trends

- Cost trends

- Throughput growth

- Coverage progression

#### Visualization Suggestions

Recommend charts/graphs for:

- Latency distribution (histogram)

- Error rates by type (stacked bar)

- Cost breakdown (pie chart)

- Coverage gaps (matrix/heatmap)

- Throughput vs. latency (scatter plot)

#### Open Questions & Recommendations


- Production mysteries to investigate

- A/B test suggestions

- Optimization experiments

- Monitoring/alerting improvements

#### Production Health Checklist


- [ ] Latency targets met (p99 ≤90ms)

- [ ] Coverage ≥98%

- [ ] FP/FN rates within tolerance

- [ ] No critical alerts in past 7 days

- [ ] Cost within budget

- [ ] Dependency health good

- [ ] Monitoring comprehensive

- [ ] Runbooks up-to-date

### Analysis Constraints


- **Production Data Available**: Full telemetry for last 30 days minimum

- **Confidence Target**: ≥70% (higher than pre-prod due to empirical data)

- **Performance Baseline**: Compare against previous analyses if available

- **Real-World Focus**: Prioritize actual observed issues over theoretical concerns

### Success Criteria

Your analysis is successful if it:

1. Identifies top 3 optimization opportunities with ROI

2. Validates performance targets are met (or explains gaps)

3. Highlights production issues before they become critical

4. Provides cost optimization strategies

5. Recommends actionable improvements backed by data

6. Assesses production health accurately

### Additional Context

**PNKLN Stack Position**:
Judge 6 is a downstream validation layer that filters data after initial ingestion and processing. It's critical for ensuring only high-quality, compliant data reaches analytics and delivery systems.

**Evolution from Specs**:
If a prior spec-based analysis exists (≥60% confidence), compare production reality to predicted performance. Call out surprises (positive or negative).

**Gemini 2.0 Pro Strengths**:
Leverage Gemini's capabilities for:

- Parsing production logs and extracting patterns

- Analyzing complex Python code in `Claude_Code_6.py`

- Identifying anomalies in telemetry time-series

- Synthesizing insights from distributed traces

---

## Begin Analysis

Please conduct the comprehensive analysis described above. You have full production telemetry, so confidence scores should be ≥70%. Be data-driven and quantitative.

**Focus Areas** (if prioritization needed):

1. Latency optimization (can we beat 90ms?)

2. Error rate reduction (minimize FP/FN)

3. Cost optimization (reduce API spend)

4. Coverage expansion (close the 2% gap)

Remember: Your analysis informs production optimization decisions. Be thorough, critical, and ROI-focused.

```

---

## Usage Instructions

### 1. Preparation

Gather all relevant production data:

- [ ] Production logs (last 30 days minimum)

- [ ] Metrics/telemetry (latency, errors, throughput)

- [ ] `Claude_Code_6.py` source code

- [ ] Compliance Framework compliance docs

- [ ] JR validation rules

- [ ] Cost reports (API bills, compute costs)

- [ ] Distributed traces

- [ ] Alert history

### 2. Gemini Setup

Configure Gemini 2.0 Pro with production context:

```python
import google.generativeai as genai

genai.configure(api_key='YOUR_API_KEY')

model = genai.GenerativeModel('gemini-3.1-pro')

# Upload production artifacts

files = [
    genai.upload_file('Claude_Code_6.py'),
    genai.upload_file('production-metrics-30d.csv'),
    genai.upload_file('latency-percentiles.png'),
    genai.upload_file('error-rates-by-type.json'),
    # ... etc
]

# Run analysis

response = model.generate_content([
    prompt_text,  # The prompt from above
    *files
])

print(response.text)

```

### 3. Review & Validate

After initial analysis:

1. Cross-check metrics with your monitoring dashboards

2. Verify recommendations align with team priorities

3. Validate cost estimates with actual bills

4. Test any suggested optimizations in staging first

5. Share findings with stakeholders

### 4. Action Planning

Based on Gemini's output:

1. Prioritize optimizations by ROI (impact/effort)

2. Create engineering tickets for improvements

3. Schedule A/B tests for risky changes

4. Update documentation based on insights

5. Set up new alerts for identified gaps

6. Plan follow-up analysis after optimizations

## Comparison to Ingestion Layer Prompt

### Key Differences

| Aspect | Judge 6 | Ingestion Layer |
|--------|----------|-----------------|
| **Data Available** | Production telemetry | Specs/docs only |
| **Confidence Target** | ≥70% | ≥60% |
| **Performance Focus** | Latency (p99 ≤90ms) | Runtime (~45 min) |
| **Quality Metrics** | FP/FN rates | Relevance, timeliness |
| **Cost Model** | Per API call | Monthly total |
| **Integration** | Calls services | Called by services |
| **Unique Concerns** | Compliance Framework, JR validation | Ethical crawling, tiers |

### When to Use Which


- **Judge 6 Prompt**: For production validation systems with real-time requirements

- **Ingestion Layer Prompt**: For batch collection systems with ethical/diversity concerns

### Shared Structure

Both prompts maintain common sections for consistency:

- Architecture analysis

- Performance evaluation

- Cost modeling

- Integration patterns

- Resilience/failure modes

- Actionable recommendations

This allows comparing analyses across PNKLN components.

## Expected Output Quality

A good Gemini analysis will:

- ✅ Be 15-25 pages with production data insights

- ✅ Include specific metric values (p99=73ms, FP=0.3%)

- ✅ Show trends over time with visualizations

- ✅ Identify 5-10 optimization opportunities with ROI

- ✅ Compare against baseline/targets

- ✅ Maintain ≥70% average confidence

A poor analysis might:

- ❌ Be generic without specific metrics

- ❌ Ignore available production data

- ❌ Miss obvious patterns in telemetry

- ❌ Provide no cost-benefit for recommendations

- ❌ Skip confidence scoring

- ❌ Overlook integration dependencies

## Integration with Output Styles

This prompt pairs well with the **Default** output style when implementing recommendations:

```bash
/output-style default

```

The Default style will help:

- Execute optimizations efficiently

- Run A/B tests with minimal overhead

- Implement cost-saving measures quickly

- Update code based on analysis findings

For team discussions of results, switch to **Explanatory**:

```bash
/output-style explanatory

```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-15 | Initial template, source for Ingestion Layer evolution |

## Related Resources


- [PNKLN Analysis Framework](./README.md)

- [Gemini Ingestion Layer Prompt](./gemini-ingestion-layer-prompt.md)

- [Metrics Configuration](./metrics-config.yaml)

- [Analysis Utilities](../../pnkln-analyzer.js)

---

**Maintained By**: PNKLN Stack Team
**Best Used With**: Gemini 2.0 Pro
**Confidence Target**: ≥70% (production system)
