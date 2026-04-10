# Intelligence Pipeline Analysis Skill

## Activation Criteria

Activate this skill when analyzing, optimizing, or troubleshooting intelligence collection pipelines, batch processing systems, or multi-source data ingestion systems.

**Trigger Keywords:**

- "analyze ingestion pipeline"

- "optimize intelligence collection"

- "review batch processing"

- "assess data pipeline"

- "evaluate GKE cron job"

## Skill Purpose

Provides deep expertise in analyzing and optimizing intelligence pipelines with focus on:

- Batch processing efficiency

- Multi-source data collection

- GKE/Kubernetes orchestration

- Runtime optimization

- Cost-performance tradeoffs

- Data quality and tier classification

## Core Knowledge Areas

### 1. Batch Processing Patterns


- Sequential vs. parallel execution

- Dependency management

- Failure recovery and retry logic

- State persistence across runs

- Incremental vs. full processing

### 2. GKE Optimization


- Container resource allocation

- CronJob scheduling strategies

- Multi-container coordination

- Pod disruption budgets

- Horizontal pod autoscaling

- Cost optimization techniques

### 3. Intelligence Collection Metrics


- Items/day throughput

- Source diversity and coverage

- Cost per item

- Data freshness and timeliness

- Quality scoring (relevance, completeness)

- Tier classification (1/2/3)

### 4. Performance Analysis


- Bottleneck identification

- Critical path analysis

- Parallelization opportunities

- I/O optimization

- Network efficiency

- Cache utilization

## Analysis Framework

### Phase 1: System Understanding


1. Map data sources and volumes

2. Identify collection methods

3. Document processing stages

4. Chart dependencies

5. Understand output requirements

### Phase 2: Performance Analysis


1. Measure current runtime breakdown

2. Identify bottlenecks

3. Calculate theoretical parallelization

4. Assess resource utilization

5. Evaluate I/O efficiency

### Phase 3: Quality Assessment


1. Analyze tier distribution

2. Evaluate source coverage

3. Check deduplication effectiveness

4. Assess relevance scoring

5. Measure completeness

### Phase 4: Cost Optimization


1. Break down cost components

2. Identify waste

3. Calculate optimization opportunities

4. Project scaling costs

5. Recommend efficiency improvements

### Phase 5: Recommendations


1. Prioritize by impact

2. Estimate effort

3. Calculate ROI

4. Define implementation steps

5. Identify risks

## Common Optimization Patterns

### Pattern 1: Parallelization

**When**: Sequential processing is bottleneck
**How**: Independent sources → parallel containers
**Impact**: 30-50% runtime reduction
**Cost**: Minimal (same total compute, better distribution)

### Pattern 2: Incremental Processing

**When**: Full reprocessing is wasteful
**How**: Track last-processed timestamps, process deltas
**Impact**: 50-70% runtime reduction
**Cost**: State storage overhead (minimal)

### Pattern 3: Source Prioritization

**When**: Not all sources are equally valuable
**How**: Process Tier 1 sources first, Tier 3 last
**Impact**: Faster time-to-value, graceful degradation
**Cost**: Complexity in scheduling

### Pattern 4: Resource Right-Sizing

**When**: Containers over/under-provisioned
**How**: Analyze actual usage, adjust requests/limits
**Impact**: 10-30% cost reduction
**Cost**: None (pure optimization)

### Pattern 5: Caching

**When**: Repeated API calls or computations
**How**: Redis/Memcached for API responses, computed values
**Impact**: 20-40% runtime reduction, reduced API costs
**Cost**: Cache infrastructure (~$10-20/month)

## Key Metrics to Track

### Performance Metrics


- **Total Runtime**: End-to-end execution time

- **Stage Breakdown**: Time per processing stage

- **Parallelization Factor**: Actual vs. theoretical

- **CPU Utilization**: Average and peak

- **Memory Usage**: Average and peak

- **I/O Wait Time**: Disk and network

### Quality Metrics


- **Items Collected**: Total and per source

- **Tier Distribution**: % Tier 1/2/3

- **Deduplication Rate**: % duplicates removed

- **Error Rate**: Failed items / total items

- **Freshness**: Time from source to ingestion

- **Completeness**: Required fields populated

### Cost Metrics


- **Total Monthly Cost**: All-in operational cost

- **Cost per Item**: Monthly cost / items collected

- **Cost per Source**: Breakdown by source

- **Scaling Factor**: Cost increase per 2x volume

- **Waste**: Unused resource capacity

## Common Pitfalls to Avoid


1. **Over-Parallelization**: Too many parallel tasks → resource contention

2. **Under-Monitoring**: Can't optimize what you don't measure

3. **Premature Optimization**: Optimize based on data, not assumptions

4. **Cost Blindness**: Optimizing for speed without considering cost

5. **Quality Neglect**: Maximizing volume at expense of relevance

6. **Ethical Violations**: Aggressive crawling → bans and legal issues

## Decision Framework

### When to Optimize for Speed


- Downstream systems need fresher data

- Current runtime exceeds SLA

- Blocking other workflows

- **Check**: Won't violate ethical crawling limits

### When to Optimize for Cost


- Monthly budget pressure

- Scaling significantly

- Low value-per-dollar

- **Check**: Won't degrade quality below threshold

### When to Optimize for Quality


- Downstream complaints about relevance

- Low tier 1 percentage

- High error rates

- **Check**: Won't exceed budget or time constraints

## Integration Patterns

### Upstream Integration (Data Sources)


- **API Rate Limits**: Respect, implement backoff

- **Authentication**: Secure credential management

- **Error Handling**: Retry transient, skip permanent

- **Monitoring**: Track source availability

### Downstream Integration (Consumers)


- **Data Contracts**: Version schemas

- **Delivery Guarantees**: At-least-once vs. exactly-once

- **Format Standardization**: Consistent output structure

- **Quality Signals**: Include confidence scores

## Troubleshooting Guide

### Symptom: Runtime Increasing Over Time

**Possible Causes:**

- Data volume growing

- Source response times degrading

- Inefficient queries or processing
**Diagnosis:** Compare current vs. historical metrics
**Solutions:** Incremental processing, optimization, scaling

### Symptom: High Cost per Item

**Possible Causes:**

- Over-provisioned resources

- Inefficient API usage

- Low collection volume
**Diagnosis:** Cost breakdown analysis
**Solutions:** Right-sizing, caching, volume increase

### Symptom: Low Tier 1 Percentage

**Possible Causes:**

- Poor source selection

- Weak relevance filtering

- Broad topic coverage
**Diagnosis:** Source-by-source quality analysis
**Solutions:** Prune low-value sources, tune filters

### Symptom: Integration Failures

**Possible Causes:**

- Schema changes

- Volume spikes

- Timing issues
**Diagnosis:** Error log analysis, contract review
**Solutions:** Versioning, buffering, retry logic

## References

See `references/` directory for:

- `batch-processing-patterns.md`: Detailed processing patterns

- `gke-optimization.md`: GKE-specific optimizations

- `intelligence-metrics.md`: Metric definitions and targets

- `troubleshooting-playbook.md`: Step-by-step diagnostics

## Tools

See `scripts/` directory for:

- `analyze-runtime.py`: Runtime breakdown analysis

- `calculate-costs.py`: Cost projection calculator

- `tier-distribution.py`: Quality tier analysis

---

**Skill Maturity**: Production-Ready
**Last Updated**: 2025-11-08
**Maintainer**: PNKLN Core Stack™ Team
