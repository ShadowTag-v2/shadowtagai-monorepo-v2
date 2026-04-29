# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 Integration for End-to-End Flow Analysis.

Bridges validation (Judge 6) with intelligence gathering (Ingestion Layer):
- Analyzes data handoffs between collection → validation
- Validates ingested data quality before downstream use
- Provides unified metrics across pipeline
- Identifies bottlenecks in collection-to-validation flow
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation result status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


@dataclass
class ValidationRule:
    """Rule for validating ingested data."""

    name: str
    description: str
    severity: str  # critical, high, medium, low
    threshold: float
    comparator: str  # >=, <=, ==, !=


@dataclass
class ValidationResult:
    """Result of validation check."""

    rule_name: str
    status: ValidationStatus
    value: float
    threshold: float
    message: str
    severity: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class Cor_Claude_Code_6Integrator:
    """Integrates Ingestion Layer with Judge 6 validation framework.

    Functions:
    1. Pre-ingestion validation (source health checks)
    2. Post-ingestion validation (data quality checks)
    3. Handoff analysis (collection → validation flow)
    4. Unified metrics dashboard
    """

    def __init__(self):
        # Validation rules for ingested data
        self.validation_rules = self._init_validation_rules()

        # Statistics
        self.stats = {
            "total_validations": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
        }

        # Handoff tracking
        self.handoff_latencies: list[float] = []
        self.handoff_failures = 0

    def _init_validation_rules(self) -> list[ValidationRule]:
        """Initialize validation rules."""
        return [
            # Quality gates
            ValidationRule(
                name="tier_1_percentage",
                description="Tier 1 items should be ≥15% of total",
                severity="high",
                threshold=15.0,
                comparator=">=",
            ),
            ValidationRule(
                name="total_items_minimum",
                description="Minimum items collected per day",
                severity="critical",
                threshold=500.0,
                comparator=">=",
            ),
            ValidationRule(
                name="compliance_score",
                description="Ethical compliance score ≥95%",
                severity="critical",
                threshold=95.0,
                comparator=">=",
            ),
            ValidationRule(
                name="source_diversity",
                description="Minimum unique source types",
                severity="high",
                threshold=4.0,
                comparator=">=",
            ),
            ValidationRule(
                name="cost_per_item",
                description="Cost per item ≤$0.10",
                severity="medium",
                threshold=0.10,
                comparator="<=",
            ),
            ValidationRule(
                name="error_rate",
                description="Error rate ≤5%",
                severity="high",
                threshold=5.0,
                comparator="<=",
            ),
        ]

    async def validate_ingestion_output(
        self,
        ingestion_metrics: dict,
    ) -> list[ValidationResult]:
        """Validate ingestion pipeline output (Judge 6 style).

        Args:
            ingestion_metrics: Metrics from ingestion pipeline

        Returns:
            List of validation results

        """
        self.stats["total_validations"] += 1

        results = []

        for rule in self.validation_rules:
            result = self._apply_rule(rule, ingestion_metrics)
            results.append(result)

            # Update stats
            if result.status == ValidationStatus.PASS:
                self.stats["passed"] += 1
            elif result.status == ValidationStatus.FAIL:
                self.stats["failed"] += 1
            elif result.status == ValidationStatus.WARNING:
                self.stats["warnings"] += 1
            elif result.status == ValidationStatus.SKIP:
                self.stats["skipped"] += 1

        return results

    def _apply_rule(
        self,
        rule: ValidationRule,
        metrics: dict,
    ) -> ValidationResult:
        """Apply a validation rule."""
        # Extract value from metrics
        value = self._extract_metric_value(rule.name, metrics)

        if value is None:
            return ValidationResult(
                rule_name=rule.name,
                status=ValidationStatus.SKIP,
                value=0.0,
                threshold=rule.threshold,
                message=f"Metric '{rule.name}' not available",
                severity=rule.severity,
            )

        # Compare value to threshold
        passed = self._compare(value, rule.comparator, rule.threshold)

        if passed:
            status = ValidationStatus.PASS
            message = f"✓ {rule.description}: {value:.2f} {rule.comparator} {rule.threshold:.2f}"
        # Determine if fail or warning
        elif rule.severity == "critical" or rule.severity == "high":
            status = ValidationStatus.FAIL
            message = f"✗ {rule.description}: {value:.2f} (expected {rule.comparator} {rule.threshold:.2f})"
        else:
            status = ValidationStatus.WARNING
            message = f"⚠ {rule.description}: {value:.2f} (expected {rule.comparator} {rule.threshold:.2f})"

        return ValidationResult(
            rule_name=rule.name,
            status=status,
            value=value,
            threshold=rule.threshold,
            message=message,
            severity=rule.severity,
        )

    def _extract_metric_value(self, metric_name: str, metrics: dict) -> float | None:
        """Extract metric value from ingestion metrics."""
        # Map rule names to metric paths
        mapping = {
            "tier_1_percentage": lambda m: (
                m.get("tier_distribution", {}).get("tier_1", {}).get("percentage", 0)
            ),
            "total_items_minimum": lambda m: m.get("coverage_stats", {}).get(
                "total_items_collected",
                0,
            ),
            "compliance_score": lambda m: m.get("compliance_stats", {}).get(
                "allowed_percentage",
                0,
            ),
            "source_diversity": lambda m: m.get("coverage_stats", {}).get("enabled_sources", 0),
            "cost_per_item": lambda m: self._calculate_cost_per_item(m),
            "error_rate": lambda m: self._calculate_error_rate(m),
        }

        extractor = mapping.get(metric_name)
        if extractor:
            return extractor(metrics)

        return None

    def _calculate_cost_per_item(self, metrics: dict) -> float:
        """Calculate cost per item."""
        total_cost = 58.0  # Mock - would come from cost tracker
        total_items = metrics.get("coverage_stats", {}).get("total_items_collected", 1)

        return total_cost / total_items if total_items > 0 else 0.0

    def _calculate_error_rate(self, metrics: dict) -> float:
        """Calculate error rate percentage."""
        coverage = metrics.get("coverage_stats", {})
        errors = sum(v.get("errors", 0) for v in coverage.get("coverage_by_type", {}).values())
        total = coverage.get("total_items_collected", 1)

        return (errors / total * 100) if total > 0 else 0.0

    def _compare(self, value: float, comparator: str, threshold: float) -> bool:
        """Compare value to threshold."""
        if comparator == ">=":
            return value >= threshold
        if comparator == "<=":
            return value <= threshold
        if comparator == "==":
            return abs(value - threshold) < 0.01
        if comparator == "!=":
            return abs(value - threshold) >= 0.01
        logger.warning(f"Unknown comparator: {comparator}")
        return False

    async def analyze_handoff(
        self,
        ingestion_complete_time: datetime,
        validation_start_time: datetime,
        data_size_bytes: int,
    ) -> dict:
        """Analyze data handoff from ingestion to validation.

        Tracks:
        - Handoff latency
        - Data size and throughput
        - Failure rate
        """
        latency_seconds = (validation_start_time - ingestion_complete_time).total_seconds()
        self.handoff_latencies.append(latency_seconds)

        throughput_mbps = (
            (data_size_bytes / 1024 / 1024 / latency_seconds) if latency_seconds > 0 else 0
        )

        # Calculate stats
        avg_latency = sum(self.handoff_latencies) / len(self.handoff_latencies)
        max_latency = max(self.handoff_latencies)

        return {
            "handoff_latency_seconds": latency_seconds,
            "data_size_bytes": data_size_bytes,
            "throughput_mbps": throughput_mbps,
            "avg_latency_seconds": avg_latency,
            "max_latency_seconds": max_latency,
            "handoff_count": len(self.handoff_latencies),
            "failure_count": self.handoff_failures,
        }

    def get_unified_metrics(
        self,
        ingestion_metrics: dict,
        validation_results: list[ValidationResult],
    ) -> dict:
        """Generate unified metrics dashboard combining ingestion + validation.

        This provides end-to-end visibility from collection to validation.
        """
        # Count validation statuses
        status_counts = {
            "pass": sum(1 for r in validation_results if r.status == ValidationStatus.PASS),
            "fail": sum(1 for r in validation_results if r.status == ValidationStatus.FAIL),
            "warning": sum(1 for r in validation_results if r.status == ValidationStatus.WARNING),
            "skip": sum(1 for r in validation_results if r.status == ValidationStatus.SKIP),
        }

        # Extract key metrics
        tier_dist = ingestion_metrics.get("tier_distribution", {})
        coverage = ingestion_metrics.get("coverage_stats", {})
        compliance = ingestion_metrics.get("compliance_stats", {})

        # Overall health score (0-100)
        health_score = self._calculate_health_score(validation_results, ingestion_metrics)

        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "ingestion": {
                "total_items": coverage.get("total_items_collected", 0),
                "tier_1_count": tier_dist.get("tier_1", {}).get("count", 0),
                "tier_1_percentage": tier_dist.get("tier_1", {}).get("percentage", 0),
                "sources_covered": coverage.get("enabled_sources", 0),
                "compliance_score": compliance.get("allowed_percentage", 0),
            },
            "validation": {
                "total_checks": len(validation_results),
                "passed": status_counts["pass"],
                "failed": status_counts["fail"],
                "warnings": status_counts["warning"],
                "success_rate": (status_counts["pass"] / len(validation_results) * 100)
                if validation_results
                else 0,
            },
            "handoff": {
                "avg_latency_seconds": sum(self.handoff_latencies) / len(self.handoff_latencies)
                if self.handoff_latencies
                else 0,
                "failure_count": self.handoff_failures,
            },
            "failed_rules": [
                {
                    "rule": r.rule_name,
                    "message": r.message,
                    "severity": r.severity,
                }
                for r in validation_results
                if r.status == ValidationStatus.FAIL
            ],
        }

    def _calculate_health_score(
        self,
        validation_results: list[ValidationResult],
        metrics: dict,
    ) -> float:
        """Calculate overall health score (0-100).

        Weighted by:
        - Validation pass rate: 40%
        - Tier 1 percentage: 25%
        - Compliance score: 25%
        - Error rate: 10%
        """
        if not validation_results:
            return 0.0

        # Validation score
        pass_count = sum(1 for r in validation_results if r.status == ValidationStatus.PASS)
        validation_score = (pass_count / len(validation_results)) * 40

        # Tier 1 score
        tier1_pct = metrics.get("tier_distribution", {}).get("tier_1", {}).get("percentage", 0)
        tier1_score = min(tier1_pct / 25 * 25, 25)  # Max 25 points

        # Compliance score
        compliance_pct = metrics.get("compliance_stats", {}).get("allowed_percentage", 0)
        compliance_score = (compliance_pct / 100) * 25

        # Error rate score (inverted - lower is better)
        error_rate = self._calculate_error_rate(metrics)
        error_score = max(0, (1 - error_rate / 10) * 10)  # 10% error = 0 points

        total_score = validation_score + tier1_score + compliance_score + error_score

        return min(100.0, max(0.0, total_score))

    def generate_validation_report(self, validation_results: list[ValidationResult]) -> str:
        """Generate human-readable validation report."""
        lines = ["\n## Judge 6 Validation Report", ""]

        # Summary
        status_counts = {
            "pass": sum(1 for r in validation_results if r.status == ValidationStatus.PASS),
            "fail": sum(1 for r in validation_results if r.status == ValidationStatus.FAIL),
            "warning": sum(1 for r in validation_results if r.status == ValidationStatus.WARNING),
        }

        total = len(validation_results)
        success_rate = (status_counts["pass"] / total * 100) if total > 0 else 0

        lines.append(f"**Overall**: {status_counts['pass']}/{total} passed ({success_rate:.1f}%)")
        lines.append("")

        # Critical failures
        critical_fails = [
            r
            for r in validation_results
            if r.status == ValidationStatus.FAIL and r.severity == "critical"
        ]
        if critical_fails:
            lines.append("### ❌ Critical Failures")
            for result in critical_fails:
                lines.append(f"- {result.message}")
            lines.append("")

        # High severity issues
        high_issues = [
            r
            for r in validation_results
            if r.status != ValidationStatus.PASS and r.severity == "high"
        ]
        if high_issues:
            lines.append("### ⚠️ High Severity Issues")
            for result in high_issues:
                symbol = "✗" if result.status == ValidationStatus.FAIL else "⚠"
                lines.append(f"- {symbol} {result.message}")
            lines.append("")

        # All results
        lines.append("### Full Results")
        for result in validation_results:
            lines.append(f"- {result.message}")

        return "\n".join(lines)
