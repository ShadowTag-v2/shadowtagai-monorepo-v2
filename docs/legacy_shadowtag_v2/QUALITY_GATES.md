# Quality Gates - Gemini Ingestion Layer

## Overview

Quality gates ensure the Gemini Ingestion Layer maintains high standards for data collection, cost efficiency, and ethical compliance. These gates are evaluated at multiple stages: collection, processing, and delivery.

## Quality Gate Categories

### 1. Volume & Coverage Gates

#### Gate 1.1: Minimum Daily Items
- **Threshold**: ≥100 items/day
- **Evaluation**: After collection stage
- **Action on failure**:
  - Warning if 80-99 items
  - Critical alert if <80 items
- **Rationale**: Ensures sufficient data volume for downstream intelligence analysis

#### Gate 1.2: Source Diversity
- **Threshold**: ≥4 active sources per day
- **Evaluation**: After collection stage
- **Action on failure**:
  - Warning if 3 sources
  - Critical alert if <3 sources
- **Rationale**: Prevents over-reliance on single source, ensures diverse perspectives

#### Gate 1.3: Source Balance
- **Threshold**: Each source contributes ≥5% of daily volume
- **Evaluation**: After collection stage
- **Action on failure**:
  - Warning if any source <5% for 2 consecutive days
- **Rationale**: Identifies degraded or failing sources early

#### Implementation Example

```python
class VolumeGate:
    """Enforce volume and coverage quality gates."""

    def __init__(self, items: List[IngestedItem], config: GateConfig):
        self.items = items
        self.config = config

    def check_minimum_items(self) -> GateResult:
        """Check Gate 1.1: Minimum daily items."""
        count = len(self.items)
        if count >= self.config.min_items_per_day:
            return GateResult(
                passed=True,
                gate="1.1",
                message=f"✅ Volume gate passed: {count} items",
            )
        elif count >= self.config.min_items_per_day * 0.8:
            return GateResult(
                passed=False,
                gate="1.1",
                severity="warning",
                message=f"⚠️ Low volume: {count} items (target: {self.config.min_items_per_day})",
            )
        else:
            return GateResult(
                passed=False,
                gate="1.1",
                severity="critical",
                message=f"❌ Critical volume failure: {count} items",
            )

    def check_source_diversity(self) -> GateResult:
        """Check Gate 1.2: Source diversity."""
        sources = set(item.source for item in self.items)
        source_count = len(sources)

        if source_count >= self.config.min_sources:
            return GateResult(
                passed=True,
                gate="1.2",
                message=f"✅ Diversity gate passed: {source_count} sources",
            )
        elif source_count >= 3:
            return GateResult(
                passed=False,
                gate="1.2",
                severity="warning",
                message=f"⚠️ Low source diversity: {source_count} sources",
            )
        else:
            return GateResult(
                passed=False,
                gate="1.2",
                severity="critical",
                message=f"❌ Critical diversity failure: {source_count} sources",
            )

    def check_source_balance(self) -> GateResult:
        """Check Gate 1.3: Source balance."""
        source_counts = {}
        for item in self.items:
            source_counts[item.source] = source_counts.get(item.source, 0) + 1

        total = len(self.items)
        min_percent = 5.0
        unbalanced = [
            f"{source}: {count} ({count/total*100:.1f}%)"
            for source, count in source_counts.items()
            if (count / total * 100) < min_percent
        ]

        if not unbalanced:
            return GateResult(
                passed=True,
                gate="1.3",
                message="✅ Source balance gate passed",
            )
        else:
            return GateResult(
                passed=False,
                gate="1.3",
                severity="warning",
                message=f"⚠️ Unbalanced sources: {', '.join(unbalanced)}",
            )
```

### 2. Quality & Relevance Gates

#### Gate 2.1: Average Relevance Score
- **Threshold**: ≥0.70 average relevance
- **Evaluation**: After Gemini scoring
- **Action on failure**:
  - Warning if 0.65-0.69
  - Critical alert if <0.65
- **Rationale**: Ensures ingested data is relevant to intelligence goals

#### Gate 2.2: Tier Distribution
- **Threshold**:
  - Tier 1: 15-25% (target: 20%)
  - Tier 2: 45-55% (target: 50%)
  - Tier 3: ≤30%
- **Evaluation**: After tier classification
- **Action on failure**:
  - Warning if outside range for 1 day
  - Alert if outside range for 3 consecutive days
- **Rationale**: Maintains balance between high-value and supplementary content

#### Gate 2.3: Low-Quality Item Threshold
- **Threshold**: <10% of items with relevance <0.60
- **Evaluation**: After Gemini scoring
- **Action on failure**:
  - Warning if 10-15% low-quality
  - Critical alert if >15% low-quality
- **Rationale**: Prevents pollution of database with irrelevant content

#### Implementation Example

```python
class QualityGate:
    """Enforce quality and relevance gates."""

    def check_average_relevance(self) -> GateResult:
        """Check Gate 2.1: Average relevance score."""
        if not self.items:
            return GateResult(
                passed=False,
                gate="2.1",
                severity="critical",
                message="❌ No items to evaluate",
            )

        avg_relevance = sum(item.relevance_score for item in self.items) / len(self.items)

        if avg_relevance >= 0.70:
            return GateResult(
                passed=True,
                gate="2.1",
                message=f"✅ Relevance gate passed: {avg_relevance:.2f}",
            )
        elif avg_relevance >= 0.65:
            return GateResult(
                passed=False,
                gate="2.1",
                severity="warning",
                message=f"⚠️ Low average relevance: {avg_relevance:.2f}",
            )
        else:
            return GateResult(
                passed=False,
                gate="2.1",
                severity="critical",
                message=f"❌ Critical relevance failure: {avg_relevance:.2f}",
            )

    def check_tier_distribution(self) -> GateResult:
        """Check Gate 2.2: Tier distribution."""
        tier_counts = {Tier.TIER_1: 0, Tier.TIER_2: 0, Tier.TIER_3: 0}
        for item in self.items:
            tier_counts[item.tier] += 1

        total = len(self.items)
        tier_percentages = {
            tier: (count / total * 100) for tier, count in tier_counts.items()
        }

        # Check each tier against targets
        issues = []
        if not (15 <= tier_percentages[Tier.TIER_1] <= 25):
            issues.append(f"T1: {tier_percentages[Tier.TIER_1]:.1f}% (target: 15-25%)")
        if not (45 <= tier_percentages[Tier.TIER_2] <= 55):
            issues.append(f"T2: {tier_percentages[Tier.TIER_2]:.1f}% (target: 45-55%)")
        if tier_percentages[Tier.TIER_3] > 30:
            issues.append(f"T3: {tier_percentages[Tier.TIER_3]:.1f}% (max: 30%)")

        if not issues:
            return GateResult(
                passed=True,
                gate="2.2",
                message=f"✅ Tier distribution: T1={tier_percentages[Tier.TIER_1]:.1f}%, T2={tier_percentages[Tier.TIER_2]:.1f}%, T3={tier_percentages[Tier.TIER_3]:.1f}%",
            )
        else:
            return GateResult(
                passed=False,
                gate="2.2",
                severity="warning",
                message=f"⚠️ Tier distribution issues: {', '.join(issues)}",
            )
```

### 3. Cost Efficiency Gates

#### Gate 3.1: Cost Per Item
- **Threshold**: ≤$0.0026 per item (target)
- **Evaluation**: After collection and cost tracking
- **Action on failure**:
  - Warning if $0.0026-$0.0035
  - Alert if $0.0035-$0.0040
  - Critical alert if >$0.0040
- **Rationale**: Maintains budget sustainability ($77/month for ~30k items)

#### Gate 3.2: Daily Budget
- **Threshold**: ≤$2.57 per day (=$77/30)
- **Evaluation**: After collection
- **Action on failure**:
  - Warning if $2.57-$3.00
  - Critical alert if >$3.00
- **Rationale**: Prevents monthly budget overrun

#### Gate 3.3: Monthly Projection
- **Threshold**: ≤$90 projected monthly cost (with 15% buffer)
- **Evaluation**: Rolling 7-day average
- **Action on failure**:
  - Warning if $77-$90
  - Critical alert if >$90
- **Rationale**: Early warning for budget overrun trends

#### Implementation Example

```python
class CostGate:
    """Enforce cost efficiency gates."""

    def check_cost_per_item(self) -> GateResult:
        """Check Gate 3.1: Cost per item."""
        total_cost = sum(item.cost for item in self.items)
        count = len(self.items)

        if count == 0:
            return GateResult(
                passed=False,
                gate="3.1",
                severity="critical",
                message="❌ No items to calculate cost",
            )

        cost_per_item = total_cost / count
        target = 0.0026

        if cost_per_item <= target:
            return GateResult(
                passed=True,
                gate="3.1",
                message=f"✅ Cost efficiency: ${cost_per_item:.4f}/item (target: ${target:.4f})",
            )
        elif cost_per_item <= 0.0035:
            return GateResult(
                passed=False,
                gate="3.1",
                severity="warning",
                message=f"⚠️ Above target cost: ${cost_per_item:.4f}/item",
            )
        elif cost_per_item <= 0.0040:
            return GateResult(
                passed=False,
                gate="3.1",
                severity="alert",
                message=f"⚠️ High cost per item: ${cost_per_item:.4f}",
            )
        else:
            return GateResult(
                passed=False,
                gate="3.1",
                severity="critical",
                message=f"❌ Critical cost overrun: ${cost_per_item:.4f}/item",
            )

    def check_daily_budget(self) -> GateResult:
        """Check Gate 3.2: Daily budget."""
        total_cost = sum(item.cost for item in self.items)
        daily_budget = 77.0 / 30  # $2.57

        if total_cost <= daily_budget:
            return GateResult(
                passed=True,
                gate="3.2",
                message=f"✅ Daily budget: ${total_cost:.2f} (budget: ${daily_budget:.2f})",
            )
        elif total_cost <= 3.00:
            return GateResult(
                passed=False,
                gate="3.2",
                severity="warning",
                message=f"⚠️ Over daily budget: ${total_cost:.2f}",
            )
        else:
            return GateResult(
                passed=False,
                gate="3.2",
                severity="critical",
                message=f"❌ Significant budget overrun: ${total_cost:.2f}",
            )
```

### 4. Timeliness Gates

#### Gate 4.1: Runtime Efficiency
- **Threshold**: ≤45 minutes total runtime
- **Evaluation**: After pipeline completion
- **Action on failure**:
  - Warning if 45-55 minutes
  - Critical alert if >60 minutes (hard timeout)
- **Rationale**: Ensures briefing delivery by 6:00 AM

#### Gate 4.2: Per-Source Timeout
- **Threshold**: ≤5 minutes per source
- **Evaluation**: Per source collector
- **Action on failure**:
  - Skip source and continue
  - Log timeout event
- **Rationale**: Prevents single source from blocking entire pipeline

#### Gate 4.3: Briefing Delivery Time
- **Threshold**: Generated and stored by 6:00 AM local time
- **Evaluation**: After delivery stage
- **Action on failure**:
  - Critical alert if late
- **Rationale**: Ensures morning briefing is available on time

### 5. Completeness Gates

#### Gate 5.1: Source Attempt Completeness
- **Threshold**: All configured sources attempted
- **Evaluation**: After collection stage
- **Action on failure**:
  - Warning if any source skipped
- **Rationale**: Ensures no source is silently ignored

#### Gate 5.2: Briefing Sections
- **Threshold**: All required sections present in briefing
- **Evaluation**: After briefing generation
- **Required sections**:
  - Summary
  - Tier 1 Items
  - Tier 2 Items
  - Tier 3 Items
  - Source Health
  - Quality Metrics
- **Action on failure**:
  - Critical alert if any section missing
- **Rationale**: Ensures briefing is complete and actionable

### 6. Ethical Compliance Gates

#### Gate 6.1: Robots.txt Compliance
- **Threshold**: 100% of crawled URLs checked against robots.txt
- **Evaluation**: During collection
- **Action on failure**:
  - Block request
  - Log violation
- **Rationale**: Legal and ethical requirement

#### Gate 6.2: Rate Limiting Compliance
- **Threshold**: No more than 1 request/second per domain
- **Evaluation**: Real-time during collection
- **Action on failure**:
  - Delay request
  - Log rate limit event
- **Rationale**: Prevents overwhelming target servers

#### Gate 6.3: User-Agent Transparency
- **Threshold**: All requests include proper bot User-Agent
- **Evaluation**: Code review and runtime checks
- **Action on failure**:
  - Critical alert if missing
- **Rationale**: Transparency and legal compliance

#### Implementation Example

```python
class EthicalGate:
    """Enforce ethical compliance gates."""

    def check_robots_compliance(self, attempts: List[CollectionAttempt]) -> GateResult:
        """Check Gate 6.1: Robots.txt compliance."""
        unchecked = [
            attempt for attempt in attempts
            if not attempt.robots_checked
        ]

        if not unchecked:
            return GateResult(
                passed=True,
                gate="6.1",
                message=f"✅ Robots.txt: {len(attempts)} URLs checked",
            )
        else:
            return GateResult(
                passed=False,
                gate="6.1",
                severity="critical",
                message=f"❌ {len(unchecked)} URLs not checked against robots.txt",
            )

    def check_rate_limiting(self, requests: List[Request]) -> GateResult:
        """Check Gate 6.2: Rate limiting compliance."""
        violations = []
        by_domain = {}

        for req in sorted(requests, key=lambda r: r.timestamp):
            domain = urlparse(req.url).netloc
            if domain in by_domain:
                time_diff = (req.timestamp - by_domain[domain]).total_seconds()
                if time_diff < 1.0:
                    violations.append(f"{domain}: {time_diff:.2f}s interval")
            by_domain[domain] = req.timestamp

        if not violations:
            return GateResult(
                passed=True,
                gate="6.2",
                message=f"✅ Rate limiting: {len(requests)} requests compliant",
            )
        else:
            return GateResult(
                passed=False,
                gate="6.2",
                severity="warning",
                message=f"⚠️ Rate limit violations: {', '.join(violations[:5])}",
            )
```

## Quality Gate Orchestration

### Gate Execution Order

1. **Collection Stage**
   - Gate 1.1: Minimum Daily Items
   - Gate 1.2: Source Diversity
   - Gate 1.3: Source Balance
   - Gate 3.2: Daily Budget
   - Gate 5.1: Source Attempt Completeness
   - Gate 6.1: Robots.txt Compliance
   - Gate 6.2: Rate Limiting Compliance

2. **Processing Stage**
   - Gate 2.1: Average Relevance Score
   - Gate 2.2: Tier Distribution
   - Gate 2.3: Low-Quality Item Threshold
   - Gate 3.1: Cost Per Item
   - Gate 3.3: Monthly Projection

3. **Delivery Stage**
   - Gate 4.1: Runtime Efficiency
   - Gate 4.3: Briefing Delivery Time
   - Gate 5.2: Briefing Sections

### Gate Evaluation Summary

```python
@dataclass
class GateEvaluationSummary:
    """Summary of all quality gate evaluations."""
    total_gates: int
    passed: int
    warnings: int
    alerts: int
    critical: int
    results: List[GateResult]

    def is_pipeline_healthy(self) -> bool:
        """Determine if pipeline is healthy enough to proceed."""
        return self.critical == 0 and self.alerts <= 1

    def generate_report(self) -> str:
        """Generate human-readable report."""
        report = [
            "# Quality Gates Evaluation Summary",
            f"- Total gates: {self.total_gates}",
            f"- Passed: {self.passed} ✅",
            f"- Warnings: {self.warnings} ⚠️",
            f"- Alerts: {self.alerts} 🔔",
            f"- Critical: {self.critical} ❌",
            "",
            "## Details",
        ]

        for result in self.results:
            status = "✅" if result.passed else "❌"
            report.append(f"- Gate {result.gate}: {status} {result.message}")

        return "\n".join(report)
```

## Monitoring & Dashboards

### Quality Gate Metrics (Prometheus)

```promql
# Gate pass rate
rate(ingestion_quality_gate_passed_total[1d])

# Gate failures by severity
sum by (severity) (ingestion_quality_gate_failed_total)

# Cost per item trend
avg_over_time(ingestion_cost_per_item[7d])

# Tier distribution
avg_over_time(ingestion_tier_distribution_percent{tier="1"}[7d])
```

### Grafana Dashboard Panels

1. **Gate Status Overview** - Heatmap of gate pass/fail over time
2. **Cost Efficiency Trend** - Line chart of cost/item vs target
3. **Tier Distribution** - Stacked area chart of T1/T2/T3 percentages
4. **Source Health** - Bar chart of items per source
5. **Runtime Performance** - Line chart of total runtime vs target

## Alerting Rules

### PagerDuty Integration

```yaml
# Critical Alerts (immediate response)
- alert: IngestionCriticalFailure
  expr: ingestion_quality_gate_failed_total{severity="critical"} > 0
  annotations:
    summary: "Gemini Ingestion Layer critical quality gate failure"

- alert: InsufficientDataVolume
  expr: sum(increase(ingestion_items_collected_total[1d])) < 80
  annotations:
    summary: "Critical: Less than 80 items collected in 24 hours"

# Warnings (investigate next business day)
- alert: HighCostPerItem
  expr: avg_over_time(ingestion_cost_per_item[3d]) > 0.004
  for: 3d
  annotations:
    summary: "Cost per item above $0.004 for 3 consecutive days"
```

## Quality Gate Configuration

All quality gate thresholds are configurable via environment variables:

```python
@dataclass
class QualityGateConfig:
    """Configuration for all quality gates."""

    # Volume gates
    min_items_per_day: int = int(os.getenv("MIN_ITEMS_PER_DAY", "100"))
    min_sources: int = int(os.getenv("MIN_SOURCES", "4"))
    min_source_percent: float = float(os.getenv("MIN_SOURCE_PERCENT", "5.0"))

    # Quality gates
    min_avg_relevance: float = float(os.getenv("MIN_AVG_RELEVANCE", "0.70"))
    tier1_min_pct: float = float(os.getenv("TIER1_MIN_PCT", "15.0"))
    tier1_max_pct: float = float(os.getenv("TIER1_MAX_PCT", "25.0"))
    tier2_min_pct: float = float(os.getenv("TIER2_MIN_PCT", "45.0"))
    tier2_max_pct: float = float(os.getenv("TIER2_MAX_PCT", "55.0"))
    tier3_max_pct: float = float(os.getenv("TIER3_MAX_PCT", "30.0"))
    max_low_quality_pct: float = float(os.getenv("MAX_LOW_QUALITY_PCT", "10.0"))

    # Cost gates
    target_cost_per_item: float = float(os.getenv("TARGET_COST_PER_ITEM", "0.0026"))
    daily_budget: float = float(os.getenv("DAILY_BUDGET", "2.57"))
    monthly_budget: float = float(os.getenv("MONTHLY_BUDGET", "77.0"))

    # Runtime gates
    target_runtime_minutes: int = int(os.getenv("TARGET_RUNTIME_MINUTES", "45"))
    hard_timeout_minutes: int = int(os.getenv("HARD_TIMEOUT_MINUTES", "60"))
    per_source_timeout_minutes: int = int(os.getenv("PER_SOURCE_TIMEOUT_MINUTES", "5"))
```

## References
- [Architecture Documentation](./ARCHITECTURE.md)
- [Cost Monitoring Guide](./COST_MONITORING.md)
- [Ethical Compliance Standards](./ETHICAL_COMPLIANCE.md)
