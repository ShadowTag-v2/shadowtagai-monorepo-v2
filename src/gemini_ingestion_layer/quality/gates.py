# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Quality Gates Implementation

Multi-faceted quality checks for the Gemini Ingestion Layer.
Unlike Judge #6's 98% coverage requirement, this focuses on:
- Daily items ingested
- Source diversity
- Cost efficiency
- Data quality (relevance, timeliness, completeness)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum


class GateStatus(str, Enum):
    """Status of a quality gate"""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class GateResult:
    """Result from a single quality gate"""

    name: str
    status: GateStatus
    actual_value: Any
    expected_value: Any
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class QualityGateResult:
    """Overall result from quality gate evaluation"""

    timestamp: datetime
    overall_status: GateStatus
    gates: list[GateResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Check if all gates passed"""
        return self.overall_status == GateStatus.PASS

    @property
    def failed_gates(self) -> list[GateResult]:
        """Get list of failed gates"""
        return [g for g in self.gates if g.status == GateStatus.FAIL]

    @property
    def warning_gates(self) -> list[GateResult]:
        """Get list of warning gates"""
        return [g for g in self.gates if g.status == GateStatus.WARN]


class QualityGates:
    """
    Quality gates for Gemini Ingestion Layer.

    Gates aligned with ingestion objectives:
    1. Volume: Daily items ingested
    2. Diversity: Source coverage
    3. Cost: Per-item cost efficiency
    4. Quality: Relevance, timeliness, completeness scores
    """

    def __init__(
        self,
        # Volume targets
        daily_items_target: int = 10000,
        daily_items_min: int = 8000,
        # Diversity targets
        min_source_diversity: int = 5,
        # Cost targets
        cost_per_item_target: float = 0.001,  # $0.001
        cost_per_item_max: float = 0.002,  # $0.002 warning threshold
        # Quality targets (60% confidence for pre-prod)
        min_relevance_score: float = 0.60,
        min_timeliness_hours: int = 24,
        min_completeness_pct: float = 0.85,
        # Runtime targets
        target_runtime_minutes: int = 45,
        max_runtime_minutes: int = 60,
    ):
        """
        Initialize quality gates.

        Args:
            daily_items_target: Target number of items per day
            daily_items_min: Minimum acceptable items per day
            min_source_diversity: Minimum number of unique sources
            cost_per_item_target: Target cost per item
            cost_per_item_max: Maximum acceptable cost per item
            min_relevance_score: Minimum relevance score (60% for pre-prod)
            min_timeliness_hours: Maximum age in hours
            min_completeness_pct: Minimum field completion percentage
            target_runtime_minutes: Target runtime (~45 min/night)
            max_runtime_minutes: Maximum acceptable runtime
        """
        self.daily_items_target = daily_items_target
        self.daily_items_min = daily_items_min
        self.min_source_diversity = min_source_diversity
        self.cost_per_item_target = cost_per_item_target
        self.cost_per_item_max = cost_per_item_max
        self.min_relevance_score = min_relevance_score
        self.min_timeliness_hours = min_timeliness_hours
        self.min_completeness_pct = min_completeness_pct
        self.target_runtime_minutes = target_runtime_minutes
        self.max_runtime_minutes = max_runtime_minutes

    def evaluate(self, ingestion_stats: dict[str, Any], run_metadata: dict[str, Any] | None = None) -> QualityGateResult:
        """
        Evaluate all quality gates.

        Args:
            ingestion_stats: Statistics from ingestion run with keys:
                - items_ingested: int
                - unique_sources: int or set
                - total_cost_usd: float
                - average_relevance_score: float
                - items_by_age: list of datetime objects
                - field_completion_rates: list of floats
                - runtime_minutes: float
            run_metadata: Optional metadata about the run

        Returns:
            QualityGateResult with all gate evaluations
        """
        gates = []

        # Gate 1: Daily Items Volume
        items_ingested = ingestion_stats.get("items_ingested", 0)
        gates.append(self._check_items_volume(items_ingested))

        # Gate 2: Source Diversity
        unique_sources = ingestion_stats.get("unique_sources", 0)
        if isinstance(unique_sources, (set, list)):
            unique_sources = len(unique_sources)
        gates.append(self._check_source_diversity(unique_sources))

        # Gate 3: Cost Efficiency
        total_cost = ingestion_stats.get("total_cost_usd", 0.0)
        cost_per_item = total_cost / items_ingested if items_ingested > 0 else 0.0
        gates.append(self._check_cost_efficiency(cost_per_item))

        # Gate 4: Relevance Score
        avg_relevance = ingestion_stats.get("average_relevance_score", 0.0)
        gates.append(self._check_relevance(avg_relevance))

        # Gate 5: Timeliness
        items_by_age = ingestion_stats.get("items_by_age", [])
        gates.append(self._check_timeliness(items_by_age))

        # Gate 6: Completeness
        field_completion = ingestion_stats.get("field_completion_rates", [])
        avg_completion = sum(field_completion) / len(field_completion) if field_completion else 0.0
        gates.append(self._check_completeness(avg_completion))

        # Gate 7: Runtime Efficiency
        runtime_minutes = ingestion_stats.get("runtime_minutes", 0.0)
        gates.append(self._check_runtime(runtime_minutes))

        # Determine overall status
        failed = any(g.status == GateStatus.FAIL for g in gates)
        warnings = any(g.status == GateStatus.WARN for g in gates)

        if failed:
            overall_status = GateStatus.FAIL
        elif warnings:
            overall_status = GateStatus.WARN
        else:
            overall_status = GateStatus.PASS

        return QualityGateResult(timestamp=datetime.now(timezone.utc), overall_status=overall_status, gates=gates, metadata=run_metadata or {})

    def _check_items_volume(self, items_ingested: int) -> GateResult:
        """Check if daily items meet target"""
        if items_ingested >= self.daily_items_target:
            return GateResult(
                name="Items Volume",
                status=GateStatus.PASS,
                actual_value=items_ingested,
                expected_value=f">= {self.daily_items_target}",
                message=f"Ingested {items_ingested} items, meeting target",
            )
        elif items_ingested >= self.daily_items_min:
            return GateResult(
                name="Items Volume",
                status=GateStatus.WARN,
                actual_value=items_ingested,
                expected_value=f">= {self.daily_items_target}",
                message=f"Ingested {items_ingested} items, below target but above minimum",
                severity="warning",
            )
        else:
            return GateResult(
                name="Items Volume",
                status=GateStatus.FAIL,
                actual_value=items_ingested,
                expected_value=f">= {self.daily_items_min}",
                message=f"Only ingested {items_ingested} items, below minimum threshold",
            )

    def _check_source_diversity(self, unique_sources: int) -> GateResult:
        """Check if source diversity meets minimum"""
        if unique_sources >= self.min_source_diversity:
            return GateResult(
                name="Source Diversity",
                status=GateStatus.PASS,
                actual_value=unique_sources,
                expected_value=f">= {self.min_source_diversity}",
                message=f"Used {unique_sources} unique sources, meeting diversity requirement",
            )
        else:
            return GateResult(
                name="Source Diversity",
                status=GateStatus.FAIL,
                actual_value=unique_sources,
                expected_value=f">= {self.min_source_diversity}",
                message=f"Only {unique_sources} unique sources, below minimum diversity",
            )

    def _check_cost_efficiency(self, cost_per_item: float) -> GateResult:
        """Check if cost per item is within targets"""
        if cost_per_item <= self.cost_per_item_target:
            return GateResult(
                name="Cost Efficiency",
                status=GateStatus.PASS,
                actual_value=f"${cost_per_item:.6f}",
                expected_value=f"<= ${self.cost_per_item_target:.6f}",
                message=f"Cost per item ${cost_per_item:.6f}, meeting target",
            )
        elif cost_per_item <= self.cost_per_item_max:
            return GateResult(
                name="Cost Efficiency",
                status=GateStatus.WARN,
                actual_value=f"${cost_per_item:.6f}",
                expected_value=f"<= ${self.cost_per_item_target:.6f}",
                message=f"Cost per item ${cost_per_item:.6f}, above target but acceptable",
                severity="warning",
            )
        else:
            return GateResult(
                name="Cost Efficiency",
                status=GateStatus.FAIL,
                actual_value=f"${cost_per_item:.6f}",
                expected_value=f"<= ${self.cost_per_item_max:.6f}",
                message=f"Cost per item ${cost_per_item:.6f}, exceeds maximum threshold",
            )

    def _check_relevance(self, avg_relevance: float) -> GateResult:
        """Check if relevance scores meet minimum (60% for pre-prod)"""
        if avg_relevance >= self.min_relevance_score:
            return GateResult(
                name="Relevance Score",
                status=GateStatus.PASS,
                actual_value=f"{avg_relevance:.1%}",
                expected_value=f">= {self.min_relevance_score:.1%}",
                message=f"Average relevance {avg_relevance:.1%}, meeting threshold",
            )
        else:
            return GateResult(
                name="Relevance Score",
                status=GateStatus.FAIL,
                actual_value=f"{avg_relevance:.1%}",
                expected_value=f">= {self.min_relevance_score:.1%}",
                message=f"Average relevance {avg_relevance:.1%}, below minimum threshold",
            )

    def _check_timeliness(self, items_by_age: list[datetime]) -> GateResult:
        """Check if items are timely (< 24 hours old)"""
        if not items_by_age:
            return GateResult(
                name="Timeliness",
                status=GateStatus.SKIP,
                actual_value="N/A",
                expected_value="N/A",
                message="No timestamp data available",
                severity="info",
            )

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=self.min_timeliness_hours)

        old_items = sum(1 for item_time in items_by_age if item_time < cutoff)
        total_items = len(items_by_age)
        timely_pct = (total_items - old_items) / total_items if total_items > 0 else 0.0

        if timely_pct >= 0.90:  # 90% within 24 hours
            return GateResult(
                name="Timeliness",
                status=GateStatus.PASS,
                actual_value=f"{timely_pct:.1%} within {self.min_timeliness_hours}h",
                expected_value=">= 90% within 24h",
                message=f"{timely_pct:.1%} of items are timely",
            )
        elif timely_pct >= 0.75:  # 75-90%
            return GateResult(
                name="Timeliness",
                status=GateStatus.WARN,
                actual_value=f"{timely_pct:.1%} within {self.min_timeliness_hours}h",
                expected_value=">= 90% within 24h",
                message=f"Only {timely_pct:.1%} of items are timely",
                severity="warning",
            )
        else:
            return GateResult(
                name="Timeliness",
                status=GateStatus.FAIL,
                actual_value=f"{timely_pct:.1%} within {self.min_timeliness_hours}h",
                expected_value=">= 75% within 24h",
                message=f"Too many stale items: {timely_pct:.1%} timely",
            )

    def _check_completeness(self, avg_completion: float) -> GateResult:
        """Check if field completion meets minimum (85%)"""
        if avg_completion >= self.min_completeness_pct:
            return GateResult(
                name="Completeness",
                status=GateStatus.PASS,
                actual_value=f"{avg_completion:.1%}",
                expected_value=f">= {self.min_completeness_pct:.1%}",
                message=f"Field completion {avg_completion:.1%}, meeting requirement",
            )
        else:
            return GateResult(
                name="Completeness",
                status=GateStatus.FAIL,
                actual_value=f"{avg_completion:.1%}",
                expected_value=f">= {self.min_completeness_pct:.1%}",
                message=f"Field completion {avg_completion:.1%}, below minimum",
            )

    def _check_runtime(self, runtime_minutes: float) -> GateResult:
        """Check if runtime meets efficiency targets (~45 min/night)"""
        if runtime_minutes <= self.target_runtime_minutes:
            return GateResult(
                name="Runtime Efficiency",
                status=GateStatus.PASS,
                actual_value=f"{runtime_minutes:.1f} min",
                expected_value=f"<= {self.target_runtime_minutes} min",
                message=f"Runtime {runtime_minutes:.1f} min, meeting target",
            )
        elif runtime_minutes <= self.max_runtime_minutes:
            return GateResult(
                name="Runtime Efficiency",
                status=GateStatus.WARN,
                actual_value=f"{runtime_minutes:.1f} min",
                expected_value=f"<= {self.target_runtime_minutes} min",
                message=f"Runtime {runtime_minutes:.1f} min, above target but acceptable",
                severity="warning",
            )
        else:
            return GateResult(
                name="Runtime Efficiency",
                status=GateStatus.FAIL,
                actual_value=f"{runtime_minutes:.1f} min",
                expected_value=f"<= {self.max_runtime_minutes} min",
                message=f"Runtime {runtime_minutes:.1f} min, exceeds maximum",
            )

    def generate_report(self, result: QualityGateResult) -> str:
        """
        Generate human-readable quality gate report.

        Args:
            result: QualityGateResult to report on

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("GEMINI INGESTION LAYER - QUALITY GATE REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {result.timestamp.isoformat()}")
        report.append(f"Overall Status: {result.overall_status.value.upper()}")
        report.append("")

        # Summary
        total = len(result.gates)
        passed = sum(1 for g in result.gates if g.status == GateStatus.PASS)
        warned = sum(1 for g in result.gates if g.status == GateStatus.WARN)
        failed = sum(1 for g in result.gates if g.status == GateStatus.FAIL)

        report.append(f"Gates: {passed} passed, {warned} warnings, {failed} failed (of {total})")
        report.append("")
        report.append("-" * 70)

        # Individual gates
        for gate in result.gates:
            status_symbol = {GateStatus.PASS: "✓", GateStatus.WARN: "⚠", GateStatus.FAIL: "✗", GateStatus.SKIP: "○"}[gate.status]

            report.append(f"{status_symbol} {gate.name}")
            report.append(f"  Actual: {gate.actual_value}")
            report.append(f"  Expected: {gate.expected_value}")
            report.append(f"  {gate.message}")
            report.append("")

        report.append("-" * 70)
        return "\n".join(report)
