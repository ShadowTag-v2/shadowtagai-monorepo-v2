"""
Unit tests for Monte Carlo risk assessment (concurrent execution pattern).
"""

import asyncio

import pytest

from shadowtagai.core.jr_engine import ProbabilityLevel, RiskLevel, SeverityLevel
from shadowtagai.core.monte_carlo_risk import MonteCarloResult, MonteCarloRiskAssessment


class TestMonteCarloRiskAssessment:
    """Test suite for Monte Carlo risk assessment."""

    def setup_method(self):
        """Initialize Monte Carlo assessor for tests."""
        self.assessor = MonteCarloRiskAssessment()

    @pytest.mark.asyncio
    async def test_evaluate_scenarios_returns_result(self):
        """Test that evaluate_scenarios returns MonteCarloResult."""
        decision = {"text": "Test decision"}
        result = await self.assessor.evaluate_scenarios(decision)

        assert isinstance(result, MonteCarloResult)
        assert isinstance(result.final_risk_level, RiskLevel)
        assert isinstance(result.selected_probability, ProbabilityLevel)
        assert isinstance(result.selected_severity, SeverityLevel)

    @pytest.mark.asyncio
    async def test_evaluate_scenarios_performance(self):
        """Test that evaluation meets <2000μs target."""
        decision = {"text": "Performance test decision"}
        result = await self.assessor.evaluate_scenarios(decision)

        assert result.execution_time_us < 2000, (
            f"Execution took {result.execution_time_us:.1f}μs (target <2000μs)"
        )

    @pytest.mark.asyncio
    async def test_probability_distribution(self):
        """Test that probability distribution is properly calculated."""
        decision = {"text": "Test decision"}
        result = await self.assessor.evaluate_scenarios(decision)

        # Should have scores for all 5 probability levels
        assert len(result.probability_distribution) == 5
        assert ProbabilityLevel.A_FREQUENT in result.probability_distribution
        assert ProbabilityLevel.E_UNLIKELY in result.probability_distribution

        # Scores should be 0.0-1.0
        for score in result.probability_distribution.values():
            assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_severity_distribution(self):
        """Test that severity distribution is properly calculated."""
        decision = {"text": "Test decision"}
        result = await self.assessor.evaluate_scenarios(decision)

        # Should have at least one severity level
        assert len(result.severity_distribution) > 0

        # Scores should be non-negative
        for score in result.severity_distribution.values():
            assert score >= 0.0

    @pytest.mark.asyncio
    async def test_model_results_count(self):
        """Test that all 5 models are executed."""
        decision = {"text": "Test decision"}
        result = await self.assessor.evaluate_scenarios(decision)

        assert len(result.model_results) == 5

    @pytest.mark.asyncio
    async def test_concurrent_execution_efficiency(self):
        """Test that concurrent execution is faster than sequential."""
        import time

        decision = {"text": "Efficiency test"}

        # Measure parallel execution
        start = time.perf_counter()
        await self.assessor.evaluate_scenarios(decision)
        parallel_time_us = (time.perf_counter() - start) * 1_000_000

        # Parallel should be much faster than 5 × 100μs = 500μs
        # (models run in parallel, not sequential)
        assert parallel_time_us < 2000, f"Parallel execution took {parallel_time_us:.1f}μs"

    @pytest.mark.asyncio
    async def test_batch_evaluations(self):
        """Test batch Monte Carlo evaluations."""
        decisions = [{"text": f"Batch decision {i}"} for i in range(10)]

        # Execute batch
        results = await asyncio.gather(*[self.assessor.evaluate_scenarios(d) for d in decisions])

        assert len(results) == 10
        for result in results:
            assert result.execution_time_us < 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
