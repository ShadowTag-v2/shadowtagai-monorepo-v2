# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Quality gate implementation."""

import os
from dataclasses import dataclass
from enum import Enum

from src.models import IngestedItem, Tier


class Severity(Enum):
    """Gate failure severity."""

    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class GateResult:
    """Result of a quality gate check."""

    gate: str
    passed: bool
    severity: Severity
    message: str


@dataclass
class QualityGateConfig:
    """Configuration for quality gates."""

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

    # Cost gates
    target_cost_per_item: float = float(os.getenv("TARGET_COST_PER_ITEM", "0.0026"))
    daily_budget: float = float(os.getenv("DAILY_BUDGET", "2.57"))


class QualityGateChecker:
    """Check quality gates for pipeline runs."""

    def __init__(self, config: QualityGateConfig | None = None):
        """
        Initialize quality gate checker.

        Args:
            config: Quality gate configuration

        """
        self.config = config or QualityGateConfig()
        self.results: list[GateResult] = []

    def check_all(self, items: list[IngestedItem]) -> list[GateResult]:
        """
        Run all quality gates.

        Args:
            items: List of ingested items to check

        Returns:
            List of gate results

        """
        self.results = []

        # Volume & Coverage Gates
        self.results.append(self.check_minimum_items(items))
        self.results.append(self.check_source_diversity(items))
        self.results.append(self.check_source_balance(items))

        # Quality & Relevance Gates
        self.results.append(self.check_average_relevance(items))
        self.results.append(self.check_tier_distribution(items))

        # Cost Efficiency Gates
        self.results.append(self.check_cost_per_item(items))
        self.results.append(self.check_daily_budget(items))

        return self.results

    def check_minimum_items(self, items: list[IngestedItem]) -> GateResult:
        """Check Gate 1.1: Minimum daily items."""
        count = len(items)

        if count >= self.config.min_items_per_day:
            return GateResult(
                gate="1.1",
                passed=True,
                severity=Severity.OK,
                message=f"✅ Volume gate passed: {count} items",
            )
        if count >= self.config.min_items_per_day * 0.8:
            return GateResult(
                gate="1.1",
                passed=False,
                severity=Severity.WARNING,
                message=f"⚠️ Low volume: {count} items (target: {self.config.min_items_per_day})",
            )
        return GateResult(
            gate="1.1",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"❌ Critical volume failure: {count} items",
        )

    def check_source_diversity(self, items: list[IngestedItem]) -> GateResult:
        """Check Gate 1.2: Source diversity."""
        sources = {item.source for item in items}
        source_count = len(sources)

        if source_count >= self.config.min_sources:
            return GateResult(
                gate="1.2",
                passed=True,
                severity=Severity.OK,
                message=f"✅ Diversity gate passed: {source_count} sources",
            )
        if source_count >= 3:
            return GateResult(
                gate="1.2",
                passed=False,
                severity=Severity.WARNING,
                message=f"⚠️ Low source diversity: {source_count} sources",
            )
        return GateResult(
            gate="1.2",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"❌ Critical diversity failure: {source_count} sources",
        )

    def check_source_balance(self, items: list[IngestedItem]) -> GateResult:
        """Check Gate 1.3: Source balance."""
        source_counts = {}
        for item in items:
            source_counts[item.source] = source_counts.get(item.source, 0) + 1

        total = len(items)
        min_percent = self.config.min_source_percent
        unbalanced = [
            f"{source}: {count} ({count / total * 100:.1f}%)" for source, count in source_counts.items() if (count / total * 100) < min_percent
        ]

        if not unbalanced:
            return GateResult(
                gate="1.3",
                passed=True,
                severity=Severity.OK,
                message="✅ Source balance gate passed",
            )
        return GateResult(
            gate="1.3",
            passed=False,
            severity=Severity.WARNING,
            message=f"⚠️ Unbalanced sources: {', '.join(unbalanced)}",
        )

    def check_average_relevance(self, items: list[IngestedItem]) -> GateResult:
        """Check Gate 2.1: Average relevance score."""
        if not items:
            return GateResult(
                gate="2.1",
                passed=False,
                severity=Severity.CRITICAL,
                message="❌ No items to evaluate",
            )

        avg_relevance = sum(item.relevance_score for item in items) / len(items)

        if avg_relevance >= self.config.min_avg_relevance:
            return GateResult(
                gate="2.1",
                passed=True,
                severity=Severity.OK,
                message=f"✅ Relevance gate passed: {avg_relevance:.2f}",
            )
        if avg_relevance >= 0.65:
            return GateResult(
                gate="2.1",
                passed=False,
                severity=Severity.WARNING,
                message=f"⚠️ Low average relevance: {avg_relevance:.2f}",
            )
        return GateResult(
            gate="2.1",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"❌ Critical relevance failure: {avg_relevance:.2f}",
        )

    def check_tier_distribution(self, items: list[IngestedItem]) -> GateResult:
        """Check Gate 2.2: Tier distribution."""
        tier_counts = {Tier.TIER_1: 0, Tier.TIER_2: 0, Tier.TIER_3: 0}
        for item in items:
            tier_counts[item.tier] = tier_counts.get(item.tier, 0) + 1

        total = len(items)
        tier_percentages = {tier: (count / total * 100) for tier, count in tier_counts.items()}

        issues = []
        if not (self.config.tier1_min_pct <= tier_percentages[Tier.TIER_1] <= self.config.tier1_max_pct):
            issues.append(f"T1: {tier_percentages[Tier.TIER_1]:.1f}% (target: {self.config.tier1_min_pct}-{self.config.tier1_max_pct}%)")
        if not (self.config.tier2_min_pct <= tier_percentages[Tier.TIER_2] <= self.config.tier2_max_pct):
            issues.append(f"T2: {tier_percentages[Tier.TIER_2]:.1f}% (target: {self.config.tier2_min_pct}-{self.config.tier2_max_pct}%)")
        if tier_percentages[Tier.TIER_3] > self.config.tier3_max_pct:
            issues.append(f"T3: {tier_percentages[Tier.TIER_3]:.1f}% (max: {self.config.tier3_max_pct}%)")

        if not issues:
            return GateResult(
                gate="2.2",
                passed=True,
                severity=Severity.OK,
                message=f"✅ Tier distribution: T1={tier_percentages[Tier.TIER_1]:.1f}%, T2={tier_percentages[Tier.TIER_2]:.1f}%, T3={tier_percentages[Tier.TIER_3]:.1f}%",
            )
        return GateResult(
            gate="2.2",
            passed=False,
            severity=Severity.WARNING,
            message=f"⚠️ Tier distribution issues: {', '.join(issues)}",
        )

    def check_cost_per_item(self, items: list[IngestedItem]) -> GateResult:
        """Check Gate 3.1: Cost per item."""
        if not items:
            return GateResult(
                gate="3.1",
                passed=False,
                severity=Severity.CRITICAL,
                message="❌ No items to calculate cost",
            )

        total_cost = sum(item.cost for item in items)
        cost_per_item = total_cost / len(items)
        target = self.config.target_cost_per_item

        if cost_per_item <= target:
            return GateResult(
                gate="3.1",
                passed=True,
                severity=Severity.OK,
                message=f"✅ Cost efficiency: ${cost_per_item:.4f}/item (target: ${target:.4f})",
            )
        if cost_per_item <= 0.004:
            return GateResult(
                gate="3.1",
                passed=False,
                severity=Severity.WARNING,
                message=f"⚠️ Above target cost: ${cost_per_item:.4f}/item",
            )
        return GateResult(
            gate="3.1",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"❌ Critical cost overrun: ${cost_per_item:.4f}/item",
        )

    def check_daily_budget(self, items: list[IngestedItem]) -> GateResult:
        """Check Gate 3.2: Daily budget."""
        total_cost = sum(item.cost for item in items)
        daily_budget = self.config.daily_budget

        if total_cost <= daily_budget:
            return GateResult(
                gate="3.2",
                passed=True,
                severity=Severity.OK,
                message=f"✅ Daily budget: ${total_cost:.2f} (budget: ${daily_budget:.2f})",
            )
        if total_cost <= 3.00:
            return GateResult(
                gate="3.2",
                passed=False,
                severity=Severity.WARNING,
                message=f"⚠️ Over daily budget: ${total_cost:.2f}",
            )
        return GateResult(
            gate="3.2",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"❌ Significant budget overrun: ${total_cost:.2f}",
        )

    def get_summary(self) -> dict:
        """
        Get summary of all gate checks.

        Returns:
            Summary dictionary

        """
        passed = sum(1 for r in self.results if r.passed)
        warnings = sum(1 for r in self.results if r.severity == Severity.WARNING)
        critical = sum(1 for r in self.results if r.severity == Severity.CRITICAL)

        return {
            "total_gates": len(self.results),
            "passed": passed,
            "warnings": warnings,
            "critical": critical,
            "overall_status": ("critical" if critical > 0 else ("warning" if warnings > 0 else "ok")),
            "results": [
                {
                    "gate": r.gate,
                    "passed": r.passed,
                    "severity": r.severity.value,
                    "message": r.message,
                }
                for r in self.results
            ],
        }
