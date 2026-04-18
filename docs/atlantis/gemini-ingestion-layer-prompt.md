# Gemini Ingestion Layer - Analysis Prompt Template

> Comprehensive analysis prompt for Gemini 2.0 Pro to evaluate the PNKLN Gemini Ingestion Layer

## Prompt Structure

This prompt is designed for use with **Gemini 2.0 Pro** to conduct deep technical analysis of the Gemini Ingestion Layer component within the PNKLN Core Stack™.

---

## Analysis Prompt

```markdown
You are a senior infrastructure architect and intelligence systems expert conducting a comprehensive pre-production analysis of the **Gemini Ingestion Layer** for the PNKLN Core Stack™.

### Context

The Gemini Ingestion Layer is an intelligence collection pipeline that runs as a nightly GKE CronJob. It gathers data from multiple sources (YouTube, Twitter, News, Web) using ethical crawling practices, classifies items into value tiers (1/2/3), and feeds downstream PNKLN components including the AM briefing system.

**Target Performance**:

- Runtime: ~45 minutes per night

- Operational Cost: ~$77/month

- Quality Gates: Daily items, source diversity, cost/item, relevance scores

**Integration**:

- Called by services across 4 namespaces

- Feeds data to processing/enrichment layer

- Ultimately contributes to AM morning briefings

### Available Documentation

You have access to:

1. Architecture specifications and diagrams

2. Pipeline configuration files

3. Flowcharts and dependency maps

4. Source configuration and tier definitions

5. Ethical compliance policies

6. Cost breakdown and budget docs

### Analysis Objectives

Conduct a thorough evaluation covering:

#### 1. Architecture Analysis

Evaluate the GKE CronJob multi-container design:

- Container orchestration patterns

- Resource allocation (CPU, memory, network)

- Fault tolerance and error handling

- Job scheduling reliability

- Scalability for variable data volumes

- Container communication patterns

**Key Questions**:

- How are containers coordinated within the CronJob?

- What happens if one container fails mid-execution?

- How does the system handle data volume spikes?

- Are there single points of failure?

#### 2. Runtime Efficiency Analysis

Assess the ~45 minute/night target:

- Current runtime breakdown by stage

- Bottlenecks in the pipeline

- Parallelization opportunities

- I/O vs. compute time distribution

- Network latency impacts

**Key Questions**:

- Which stage consumes the most time?

- Can stages be parallelized further?

- What's the critical path through the pipeline?

- How variable is runtime night-to-night?

#### 3. Ethical Compliance Model

Evaluate crawler ethics and legal compliance:

- robots.txt adherence mechanisms

- Rate limiting implementation per source

- User-agent transparency

- Attribution and source tracking

- Ban detection and recovery

**Key Questions**:

- How is robots.txt parsed and enforced?

- What are the configured rate limits by source type?

- How is the crawler identified to external servers?

- What happens when a source blocks the crawler?

- Is there monitoring for compliance violations?

#### 4. Multi-Source Coverage

Analyze data source diversity and balance:

- Source type distribution (YouTube, Twitter, News, Web)

- Temporal coverage (weekday/weekend, time-of-day)

- Geographic diversity

- Language coverage

- Topic breadth

- Source health monitoring

**Key Questions**:

- Is coverage balanced or skewed toward specific sources?

- Are there temporal gaps in collection?

- How quickly can new sources be added?

- What happens when a major source goes offline?

- How is source quality assessed?

#### 5. Tier Classification Metrics

Evaluate the tier 1/2/3 value classification:

- Tier assignment criteria and logic

- Distribution across tiers (% in each)

- Cost allocation by tier

- Processing time by tier

- Delivery rate to AM briefing by tier

- Tier re-classification mechanisms

**Key Questions**:

- What % of items are Tier 1 vs. Tier 3?

- Is cost aligned with value (avoiding expensive Tier 3)?

- Can tier criteria be tuned to improve value?

- How stable are tier assignments over time?

- Are there feedback loops from downstream consumption?

#### 6. Cost Model & Economics

Analyze the ~$77/month operational cost:

- Cost breakdown by component (API calls, compute, storage, network)

- Cost per item ingested

- Cost by source type

- Cost by tier

- Scaling sensitivity (what if 2x volume?)

- Optimization opportunities

**Key Questions**:

- What drives the majority of cost?

- Which sources are most/least cost-effective?

- How elastic is cost to data volume?

- Are there wasteful operations?

- What's the cost threshold for sustainability?

#### 7. Data Quality Assessment

Evaluate ingested data quality dimensions:

- **Relevance**: How well items match intelligence needs

- **Timeliness**: Freshness at collection and delivery

- **Completeness**: Field population, metadata richness

- **Accuracy**: Factual correctness (if verifiable)

- **Deduplication**: Handling of duplicate items

**Key Questions**:

- How is relevance scored?

- What's the typical data age at delivery?

- Are critical fields consistently populated?

- How are duplicates detected and handled?

- Is there quality monitoring/alerting?

#### 8. AM Briefing Delivery Effectiveness

Assess end-to-end delivery to morning briefings:

- Delivery timeliness (ready by work start)

- Delivery success rate

- Format quality (readability, structure)

- User engagement (if measured)

- Actionability of insights

**Key Questions**:

- Does the briefing consistently arrive on time?

- What's the failure rate and recovery process?

- How is user feedback incorporated?

- What's the signal-to-noise ratio in briefings?

- Are briefings customized per user/team?

#### 9. Integration Patterns

Analyze interactions with PNKLN stack:

- How services in 4 namespaces invoke ingestion

- Trigger mechanisms and scheduling

- Data handoff protocols (format, APIs)

- Error propagation and retry logic

- Dependency management

**Key Questions**:

- What triggers the nightly CronJob?

- How do downstream services consume ingested data?

- What happens if ingestion fails?

- Are there SLAs for data availability?

- How are schema changes coordinated?

#### 10. Resilience & Failure Modes

Identify and evaluate failure scenarios:

- Source outages (e.g., Twitter API down)

- Network failures mid-crawl

- Cost spikes (expensive source)

- Runtime overruns (>45 min)

- Data quality degradation

- Storage/quota exhaustion

**Key Questions**:

- How are failures detected and alerted?

- What's the retry strategy?

- Can ingestion partially succeed?

- How long can the system tolerate source outages?

- Are there cascading failure risks?

### Analysis Requirements


1. **Confidence Scoring**: Assign confidence ≥60% to each finding (spec-based analysis)

2. **Evidence-Based**: Reference specific docs, specs, or diagrams

3. **Actionable**: Provide concrete recommendations, not just observations

4. **Prioritized**: Rank issues by severity (critical, high, medium, low)

5. **Quantitative**: Use metrics and numbers where possible

### Output Format

Structure your analysis as follows:

#### Executive Summary


- Overall health assessment (1-5 scale)

- Top 3 strengths

- Top 3 risks/concerns

- Go/no-go recommendation for production

#### Detailed Findings by Category

For each of the 10 analysis areas above:

- **Status**: Green/Yellow/Red assessment

- **Confidence**: % confidence in assessment

- **Key Findings**: Bullet points with evidence

- **Risks Identified**: Specific issues with severity

- **Recommendations**: Prioritized actions

#### Metrics Summary Tables


- Runtime breakdown by stage

- Cost breakdown by component/source/tier

- Source coverage distribution

- Tier classification distribution

- Quality score summary

#### Visualization Suggestions

Recommend charts/graphs for:

- Tier distribution (pie chart)

- Source coverage (heatmap)

- Cost breakdown (stacked bar)

- Runtime timeline (Gantt chart)

#### Open Questions & Assumptions

List anything unclear or assumed:

- Documentation gaps

- Ambiguous specs

- Unverifiable claims

- Areas needing production data

#### Production Readiness Checklist


- [ ] Architecture review passed

- [ ] Performance targets achievable

- [ ] Ethical compliance verified

- [ ] Cost model validated

- [ ] Quality gates defined

- [ ] Failure modes addressed

- [ ] Monitoring/alerting planned

- [ ] Documentation complete

### Analysis Constraints


- **No Production Data**: Analysis based solely on specs/docs (pre-prod)

- **Confidence Target**: ≥60% (will increase to ≥70% post-production)

- **Conservative Estimates**: Err on side of caution for unknowns

- **Flag Uncertainties**: Explicitly note low-confidence areas

### Success Criteria

Your analysis is successful if it:

1. Identifies all critical risks before production

2. Validates performance targets are achievable

3. Confirms ethical compliance mechanisms

4. Highlights optimization opportunities

5. Provides clear go/no-go guidance

6. Enables informed deployment decisions

### Additional Context

**PNKLN Stack Position**:
The Ingestion Layer is the foundational upstream component. Its output quality directly impacts all downstream systems including Judge #6 validation and AM briefing delivery. Failures here cascade through the entire stack.

**Prior Art**:
This analysis template evolved from the Judge #6 analysis prompt. Key differences reflect the shift from reactive enforcement (Judge #6) to proactive collection (Ingestion Layer).

**Gemini 2.0 Pro Strengths**:
Leverage Gemini's multimodal capabilities for:

- Analyzing architecture diagrams visually

- Parsing config files and code snippets

- Identifying patterns across documents

- Synthesizing insights from disparate sources

---

## Begin Analysis

Please conduct the comprehensive analysis described above. Take your time to thoroughly examine all documentation provided. Ask clarifying questions if specs are ambiguous before proceeding with low-confidence assessments.

**Focus Areas** (if prioritization needed):

1. Runtime efficiency (can we hit 45 min?)

2. Ethical compliance (legal risks?)

3. Cost model (sustainable at scale?)

4. Tier classification (optimized for value?)

Remember: Your analysis informs a production deployment decision. Be thorough, critical, and actionable.

```

---

## Usage Instructions

### 1. Preparation

Gather all relevant documentation:

- [ ] Architecture diagrams (GKE, containers, networking)

- [ ] Pipeline configuration files

- [ ] Source definitions and tier criteria

- [ ] Ethical compliance policies

- [ ] Cost estimates and breakdowns

- [ ] Integration specifications

- [ ] Monitoring/alerting plans

### 2. Gemini Setup

Configure Gemini 2.0 Pro:

```python
import google.generativeai as genai

genai.configure(api_key='YOUR_API_KEY')

model = genai.GenerativeModel('gemini-3.1-pro')

# Upload documentation files

files = [
    genai.upload_file('architecture-diagram.png'),
    genai.upload_file('pipeline-config.yaml'),
    genai.upload_file('source-definitions.json'),
    # ... etc
]

# Run analysis

response = model.generate_content([
    prompt_text,  # The prompt from above
    *files
])

print(response.text)

```

### 3. Review & Iterate

After initial analysis:

1. Review confidence scores - are any <60%?

2. Check for documentation gaps - are questions unanswered?

3. Validate findings - do they align with team knowledge?

4. Request clarification - address low-confidence areas

5. Re-run with additional docs if needed

### 4. Action Planning

Based on Gemini's output:

1. Prioritize recommendations by severity

2. Assign owners for each action item

3. Set timelines for addressing issues

4. Document decisions (accept risk, mitigate, redesign)

5. Update specs based on analysis insights

## Customization Options

### Adjust Confidence Target

For production systems with telemetry:

```markdown
**Confidence Target**: ≥70% (production data available)

```

### Focus on Specific Areas

To deep-dive on particular concerns:

```markdown
**Priority Focus**:

1. Ethical compliance - need 90%+ confidence before launch

2. Cost model - must validate $77/mo assumption

```

### Add Custom Sections

For organization-specific needs:

```markdown

#### 11. Compliance Analysis

Evaluate adherence to [Your Company] policies:

- Data retention requirements

- Privacy regulations (GDPR, CCPA)

- Security controls (encryption, access)

```

## Expected Output Quality

A good Gemini analysis will:

- ✅ Be 10-20 pages of detailed, structured content

- ✅ Reference specific doc sections as evidence

- ✅ Provide quantitative metrics and estimates

- ✅ Identify 5-10 actionable recommendations

- ✅ Clearly flag high-risk areas

- ✅ Suggest visualization formats

- ✅ Maintain ≥60% average confidence

A poor analysis might:

- ❌ Be vague or generic (could apply to any system)

- ❌ Lack specific references to provided docs

- ❌ Miss critical failure modes

- ❌ Provide no confidence scores

- ❌ Offer no recommendations

- ❌ Ignore the PNKLN stack context

## Integration with Output Styles

This prompt pairs well with the **Explanatory** output style when discussing results with the team:

```bash
/output-style explanatory

```

The Explanatory style will help:

- Break down Gemini's analysis for different audiences

- Explain technical findings to non-technical stakeholders

- Provide context on why certain recommendations matter

- Connect ingestion layer to broader PNKLN strategy

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-15 | Initial template based on Judge #6 evolution |

## Related Resources


- [PNKLN Analysis Framework](./README.md)

- [Judge #6 Prompt Template](./judge-six-prompt.md)

- [Metrics Configuration](./metrics-config.yaml)

- [Analysis Utilities](../../pnkln-analyzer.js)

---

**Maintained By**: PNKLN Stack Team
**Best Used With**: Gemini 2.0 Pro
**Confidence Target**: ≥60% (pre-prod), ≥70% (prod)
