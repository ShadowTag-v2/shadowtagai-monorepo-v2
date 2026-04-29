# Judge #6 Analysis Prompt

## Purpose
This prompt is designed for Gemini 2.0 Pro to analyze the Judge #6 system architecture, performance, and operational readiness. Judge #6 is the real-time governance validation and enforcement layer within the PNKLN Core Stack™.

## Target Confidence
- **Pre-Production** (specs-only): ≥60%
- **Production** (with telemetry): ≥70%

---

## Prompt Template

```
You are an expert systems architect analyzing **Judge #6**,
a real-time governance validation and enforcement system within the PNKLN Core Stack™.

## System Context

Judge #6 is responsible for:
- Real-time validation of content and decisions (<90ms p99 latency)
- ATP 5-19 risk assessment framework integration
- JR (Purpose-Reasons-Brakes) decision validation
- Synchronous enforcement across 4 GKE namespaces
- High-accuracy blocking decisions (minimizing false positives/negatives)

## Architecture Overview

**Deployment**: Hybrid Gemini+PyTorch+rules engine
**Integration**: Calls services in 4 namespaces (governance, orchestration, cognitive, shadowtag)
**Validation Type**: Synchronous with real-time response

## Analysis Framework

Please analyze the following aspects of Judge #6:

### 1. Architecture Analysis
- **Hybrid AI Design**: Gemini LLM + PyTorch models + rules engine coordination
- **Resource Allocation**: GPU/CPU balance for sub-90ms latency
- **Deployment Strategy**: Service mesh integration, load balancing
- **Fault Tolerance**: Failover mechanisms for high availability
- **Scalability**: Concurrent validation capacity

### 2. Performance Metrics
Evaluate against these targets:
- **Latency**: p99 ≤90ms (critical SLA)
- **Throughput**: Validations per second capacity
- **Availability**: 99.9% uptime requirement
- **Block Rate**: Percentage of enforced vs. allowed decisions
- **Coverage**: ≥98% of all validation scenarios

### 3. ATP 5-19 Risk Assessment Integration
Analyze:
- **Risk Levels**: Extremely High, High, Medium, Low classification
- **Probability Assessment**: A-E scale implementation (A: Frequent, E: Improbable)
- **Severity Scoring**: I-IV scale (I: Catastrophic, IV: Negligible)
- **Decision Matrix**: Prob × Severity → Level mapping accuracy
- **Army Doctrine Compliance**: Alignment with ATP 5-19 standards

### 4. JR Engine Validation
Evaluate the Purpose-Reasons-Brakes framework:
- **Purpose**: Does action advance mission? (PNKLN goals, revenue, user value)
- **Reasons**: Is judgment defensible and well-reasoned?
- **Brakes**: Are p99 risks survivable? Safety checks in place?
- **Latency Target**: <500μs for JR engine execution
- **Integration**: How JR feeds into overall validation decision

### 5. Quality Assurance
Assess accuracy metrics:
- **False Positive Rate**: Incorrectly blocked valid content/decisions
- **False Negative Rate**: Missed violations that should be blocked
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: Harmonic mean of precision and recall

### 6. Coverage Analysis
Evaluate scenario coverage:
- **Governance Scenarios**: Content moderation, policy enforcement
- **Orchestration Scenarios**: Workflow validation, agent coordination
- **Cognitive Scenarios**: AI output validation, hallucination detection
- **ShadowTag Scenarios**: Watermark integrity, audit trail validation
- **Target**: ≥98% coverage across all namespaces

### 7. Cost Model Analysis
Review:
- **Per-Validation Cost**: API calls to Gemini, PyTorch inference
- **Optimization Strategy**: Rule engine pre-filtering before AI invocation
- **Cache Hit Rate**: Frequently validated patterns cached
- **Monthly Burn**: Total cost at expected validation volume

### 8. Integration Points
Analyze cross-namespace calls:
- **ShadowTag-v2jr-governance**: Policy enforcement triggers
- **autogen-orchestration**: Workflow validation hooks
- **cognitive-stack-v5**: AI output validation
- **shadowtag-v2**: Watermark verification
- **Latency Budget**: How integration calls impact 90ms SLA

### 9. Decision Audit Trail
Evaluate logging and traceability:
- **Audit Completeness**: Every decision logged with rationale
- **Semantic Compression**: 487 bytes vs 50KB via ATP scan + binary decision + zstd
- **Retention Policy**: Long-term storage strategy
- **Queryability**: Audit trail search and analysis capability

### 10. Edge Cases & Resilience
Probe for:
- **Ambiguous Content**: Borderline cases requiring human review
- **Latency Spikes**: Handling of >90ms scenarios (fallback logic)
- **AI Service Outages**: Degraded mode operation (rules-only)
- **Volume Surges**: 10x validation request handling
- **Adversarial Attacks**: Evasion attempts detection

## Deliverables

Please provide:

1. **Executive Summary** (2-3 paragraphs)
   - Overall system health assessment
   - Critical strengths and weaknesses
   - Production readiness status

2. **Detailed Analysis** (by section)
   - Findings for each of the 10 analysis areas
   - Confidence level per finding (with rationale)
   - Supporting evidence from code/specs

3. **Optimization Recommendations** (prioritized)
   - Latency reduction opportunities
   - Accuracy improvement strategies
   - Cost optimization tactics

4. **Risk Assessment**
   - Critical risks to SLA compliance
   - Mitigation strategies
   - Monitoring and alerting recommendations

5. **Metrics Dashboard Recommendations**
   - Real-time latency percentiles (p50, p90, p95, p99)
   - FP/FN rate tracking
   - Throughput and block rate visualization
   - Alert thresholds for SLA violations

6. **Production Readiness Checklist**
   - Go/No-Go criteria for launch
   - Outstanding items before deployment
   - Load testing results required

## Input Materials

[Attach the following to this prompt:]
- `Claude_Code_6.py` source code
- ATP 5-19 risk assessment configuration
- JR engine implementation
- Deployment manifests (Kubernetes YAML)
- Integration API documentation
- Performance benchmark results
- Test coverage reports

## Analysis Style

- Be specific and evidence-based
- Call out assumptions explicitly
- Highlight latency-critical code paths
- Flag uncertainties requiring production telemetry
- Focus on SLA compliance
- Suggest specific code improvements

## Confidence Calibration

For pre-production analysis (specs-only):
- Target ≥60% overall confidence
- Identify which metrics need production data
- Flag assumptions about real-world latency

For production analysis (with telemetry):
- Target ≥70% overall confidence
- Validate p99 latency against SLA
- Compare predicted vs. actual FP/FN rates
```

---

## Usage Instructions

### Pre-Production Analysis
1. Gather `Claude_Code_6.py`, configs, deployment specs
2. Run unit tests and capture coverage reports
3. Attach all materials to prompt
4. Submit to Gemini 2.0 Pro
5. Address findings with confidence ≥60%

### Production Analysis
1. Collect 2 weeks of production metrics
2. Include latency percentiles, FP/FN rates, logs
3. Attach to prompt above
4. Submit to Gemini 2.0 Pro
5. Validate ≥70% confidence findings
6. Implement optimization recommendations

### Continuous Monitoring
- **Real-time**: p99 latency alerts if >90ms
- **Daily**: FP/FN rate review
- **Weekly**: Coverage gap analysis
- **Monthly**: Full system analysis with prompt

---

## Comparison with Gemini Ingestion Layer

| Aspect | Judge #6 | Gemini Ingestion Layer |
|--------|----------|------------------------|
| **Role** | Reactive Validator | Proactive Collector |
| **Timing** | Real-time (synchronous) | Batch (nightly cron) |
| **Architecture** | Hybrid Gemini+PyTorch+rules | GKE CronJob multi-container |
| **Key Metric** | Latency (p99 ≤90ms) | Runtime (~45 min/night) |
| **Quality Focus** | FP/FN rates | Relevance, timeliness, completeness |
| **Integration** | Calls services in 4 namespaces | Called by services in 4 namespaces |
| **Cost Model** | Per API call | Monthly operational (~$77) |
| **Unique Features** | ATP 5-19, JR Validation | Ethical crawling, Tier classification |
| **Coverage Gate** | 98% minimum | Multi-source diversity |
| **Confidence Target** | ≥70% (prod) | ≥60% (pre-prod), ≥70% (prod) |

---

## Key Decision Frameworks

### ATP 5-19 Risk Matrix

| Probability | Severity I | Severity II | Severity III | Severity IV |
|-------------|-----------|-------------|--------------|-------------|
| A (Frequent) | EH | EH | H | M |
| B (Likely) | EH | H | M | L |
| C (Occasional) | H | M | M | L |
| D (Seldom) | M | M | L | L |
| E (Unlikely) | M | L | L | L |

**Levels**: EH = Extremely High, H = High, M = Medium, L = Low

### JR Engine Logic

```python
def validate_jr(action):
    # Purpose: Does it advance mission?
    purpose_score = check_alignment(action, PNKLN_GOALS)

    # Reasons: Is judgment defensible?
    reasons_score = assess_reasoning(action)

    # Brakes: Is p99 survivable?
    risk_score = calculate_risk(action, p99_threshold=True)

    # Combined decision (< 500μs)
    return (purpose_score > 0.7 and
            reasons_score > 0.6 and
            risk_score < 0.3)
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Owner**: CTO / Platform Architecture Team
**Related**: `.claude/pnkln-core-stack.md`, Gemini Ingestion Layer analysis prompt
