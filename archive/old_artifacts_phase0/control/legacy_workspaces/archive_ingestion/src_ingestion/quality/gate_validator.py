"""Quality gate validation for ingestion pipeline"""

import os
from collections import Counter

from ..models import DataSource, QualityGateResult, Scenario, ScenarioTier


class QualityGateValidator:
    """
    Validates quality gates for daily ingestion

    Gates:
    1. Volume: 5,000-10,000 scenarios/day
    2. Source Diversity: ≥6 sources active
    3. Cost Efficiency: <$0.015/scenario
    4. Relevance Score: ≥85/100 average
    5. Tier Distribution: 25-35% Tier 1
    """

    def __init__(self):
        # Targets from environment or defaults
        self.target_min_volume = int(os.getenv("DAILY_ITEM_TARGET_MIN", "5000"))
        self.target_max_volume = int(os.getenv("DAILY_ITEM_TARGET_MAX", "10000"))
        self.target_min_sources = int(os.getenv("MIN_SOURCE_DIVERSITY", "6"))
        self.target_cost_per_item = float(os.getenv("COST_PER_ITEM_TARGET", "0.015"))
        self.target_min_relevance = float(os.getenv("MIN_RELEVANCE_SCORE", "85"))
        self.target_tier1_min = 25.0
        self.target_tier1_max = 35.0

    def validate_all_gates(
        self,
        scenarios: list[Scenario],
        total_cost_usd: float,
        relevance_score: float = 85.0
    ) -> list[QualityGateResult]:
        """
        Run all quality gates

        Args:
            scenarios: All classified scenarios
            total_cost_usd: Total daily operational cost
            relevance_score: Gemini-assessed relevance (simulated for now)

        Returns:
            List of gate results
        """
        print("[Quality Gates] Validating all gates...")

        results = []

        # Gate 1: Volume Check
        results.append(self._validate_volume(scenarios))

        # Gate 2: Source Diversity
        results.append(self._validate_source_diversity(scenarios))

        # Gate 3: Cost Efficiency
        results.append(self._validate_cost_efficiency(scenarios, total_cost_usd))

        # Gate 4: Relevance Score
        results.append(self._validate_relevance(relevance_score))

        # Gate 5: Tier Distribution
        results.append(self._validate_tier_distribution(scenarios))

        # Summary
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        print(f"[Quality Gates] {passed}/{total} gates passed")

        return results

    def _validate_volume(self, scenarios: list[Scenario]) -> QualityGateResult:
        """Gate 1: Volume check"""
        count = len(scenarios)
        target = f"{self.target_min_volume}-{self.target_max_volume}"

        if self.target_min_volume <= count <= self.target_max_volume:
            return QualityGateResult(
                gate_name="Volume Check",
                passed=True,
                measured_value=count,
                target_value=target,
                status_emoji="✅",
                message=f"Volume {count} within target range"
            )
        else:
            return QualityGateResult(
                gate_name="Volume Check",
                passed=False,
                measured_value=count,
                target_value=target,
                status_emoji="❌",
                message=f"Volume {count} outside target range {target}"
            )

    def _validate_source_diversity(self, scenarios: list[Scenario]) -> QualityGateResult:
        """Gate 2: Source diversity"""
        sources = set(s.source for s in scenarios)
        num_sources = len(sources)

        if num_sources >= self.target_min_sources:
            return QualityGateResult(
                gate_name="Source Diversity",
                passed=True,
                measured_value=num_sources,
                target_value=f"≥{self.target_min_sources}",
                status_emoji="✅",
                message=f"{num_sources} sources active (target ≥{self.target_min_sources})"
            )
        else:
            return QualityGateResult(
                gate_name="Source Diversity",
                passed=False,
                measured_value=num_sources,
                target_value=f"≥{self.target_min_sources}",
                status_emoji="❌",
                message=f"Only {num_sources} sources active (target ≥{self.target_min_sources})"
            )

    def _validate_cost_efficiency(
        self,
        scenarios: list[Scenario],
        total_cost_usd: float
    ) -> QualityGateResult:
        """Gate 3: Cost efficiency"""
        count = len(scenarios)
        if count == 0:
            cost_per_item = 999.0
        else:
            cost_per_item = total_cost_usd / count

        if cost_per_item < self.target_cost_per_item:
            return QualityGateResult(
                gate_name="Cost Efficiency",
                passed=True,
                measured_value=f"${cost_per_item:.4f}",
                target_value=f"<${self.target_cost_per_item}",
                status_emoji="✅",
                message=f"Cost per item ${cost_per_item:.4f} under target"
            )
        else:
            return QualityGateResult(
                gate_name="Cost Efficiency",
                passed=False,
                measured_value=f"${cost_per_item:.4f}",
                target_value=f"<${self.target_cost_per_item}",
                status_emoji="❌",
                message=f"Cost per item ${cost_per_item:.4f} exceeds target"
            )

    def _validate_relevance(self, relevance_score: float) -> QualityGateResult:
        """Gate 4: Relevance score"""
        if relevance_score >= self.target_min_relevance:
            return QualityGateResult(
                gate_name="Relevance Score",
                passed=True,
                measured_value=relevance_score,
                target_value=f"≥{self.target_min_relevance}",
                status_emoji="✅",
                message=f"Relevance {relevance_score:.1f} meets target"
            )
        else:
            return QualityGateResult(
                gate_name="Relevance Score",
                passed=False,
                measured_value=relevance_score,
                target_value=f"≥{self.target_min_relevance}",
                status_emoji="⚠️",
                message=f"Relevance {relevance_score:.1f} below target"
            )

    def _validate_tier_distribution(self, scenarios: list[Scenario]) -> QualityGateResult:
        """Gate 5: Tier 1 distribution"""
        if not scenarios:
            return QualityGateResult(
                gate_name="Tier Distribution",
                passed=False,
                measured_value="0%",
                target_value=f"{self.target_tier1_min}-{self.target_tier1_max}%",
                status_emoji="❌",
                message="No scenarios to analyze"
            )

        tier_counts = Counter(s.tier for s in scenarios)
        tier1_count = tier_counts.get(ScenarioTier.TIER_1, 0)
        tier1_pct = 100 * tier1_count / len(scenarios)

        if self.target_tier1_min <= tier1_pct <= self.target_tier1_max:
            return QualityGateResult(
                gate_name="Tier Distribution",
                passed=True,
                measured_value=f"{tier1_pct:.1f}%",
                target_value=f"{self.target_tier1_min}-{self.target_tier1_max}%",
                status_emoji="✅",
                message=f"Tier 1 at {tier1_pct:.1f}% (target {self.target_tier1_min}-{self.target_tier1_max}%)"
            )
        else:
            return QualityGateResult(
                gate_name="Tier Distribution",
                passed=False,
                measured_value=f"{tier1_pct:.1f}%",
                target_value=f"{self.target_tier1_min}-{self.target_tier1_max}%",
                status_emoji="⚠️",
                message=f"Tier 1 at {tier1_pct:.1f}% outside target range"
            )


if __name__ == "__main__":
    from datetime import datetime

    from ..models import SensorData, TimeOfDay, WeatherCondition

    # Create test scenarios
    test_scenarios = [
        Scenario(
            scenario_id=f"test_{i}",
            source=DataSource.FLEET_TELEMETRY,
            tier=ScenarioTier.TIER_1 if i < 1500 else ScenarioTier.TIER_2,
            safety_score=80 + (i % 15),
            complexity_score=70 + (i % 20),
            duration_seconds=10.0,
            num_agents=3,
            weather_condition=WeatherCondition.CLEAR,
            time_of_day=TimeOfDay.DAY,
            sensor_data=SensorData(timestamp=datetime.utcnow()),
            consent_verified=True,
            privacy_scrubbed=True
        )
        for i in range(6000)
    ]

    validator = QualityGateValidator()
    results = validator.validate_all_gates(
        test_scenarios,
        total_cost_usd=77.0,
        relevance_score=87.5
    )

    for result in results:
        print(f"{result.status_emoji} {result.gate_name}: {result.message}")
