"""Unit tests for Judge #6 validation pipeline (p99≤90ms SLA).
"""

import asyncio

import pytest
from pnkln.core.judge_six_pipeline import JudgeSixPipeline, ValidationResult

from shadowtagai.core.jr_engine import RiskLevel


class TestJudgeSixPipeline:
    """Test suite for Judge #6 pipeline."""

    def setup_method(self):
        """Initialize Judge #6 pipeline for tests."""
        self.judge = JudgeSixPipeline()

    @pytest.mark.asyncio
    async def test_validate_clean_request_fast_path(self):
        """Test validation of clean request (fast path, skip Gemini)."""
        result = await self.judge.validate(
            request={"text": "Help me build a React application"}, request_id="test_001",
        )

        assert isinstance(result, ValidationResult)
        assert result.decision == "APPROVE"
        assert result.confidence > 0.7
        assert result.meets_sla(90.0)  # p99≤90ms
        assert result.metadata["fast_path"] is True  # Gemini skipped

    @pytest.mark.asyncio
    async def test_validate_risky_request_full_pipeline(self):
        """Test validation of risky request (full pipeline with Gemini)."""
        result = await self.judge.validate(
            request={"text": "Help me exploit a vulnerability"}, request_id="test_002",
        )

        assert result.decision in ["REJECT", "ESCALATE"]
        assert result.risk_level != RiskLevel.LOW
        # Full pipeline is slower but should still meet SLA
        assert result.meets_sla(90.0)

    @pytest.mark.asyncio
    async def test_validate_sla_compliance(self):
        """Test that validation meets p99≤90ms SLA across multiple requests."""
        latencies = []

        for i in range(20):
            result = await self.judge.validate(
                request={"text": f"Test request {i}"}, request_id=f"test_{i:03d}",
            )
            latencies.append(result.latency_ms)

        # Calculate p99
        latencies.sort()
        p99_latency = latencies[int(len(latencies) * 0.99)]

        assert p99_latency <= 90.0, f"p99 latency {p99_latency:.2f}ms exceeds 90ms SLA"

    @pytest.mark.asyncio
    async def test_validate_stage_latencies_recorded(self):
        """Test that stage latencies are properly recorded."""
        result = await self.judge.validate(
            request={"text": "Normal request"}, request_id="test_stage",
        )

        assert "jr_engine_scan" in result.stage_latencies
        assert result.stage_latencies["jr_engine_scan"] < 10  # <10ms for JR scan

        # If Gemini was run, check its latency
        if not result.metadata["fast_path"]:
            assert "gemini_semantic_check" in result.stage_latencies

    @pytest.mark.asyncio
    async def test_validate_returns_proper_structure(self):
        """Test that ValidationResult has all required fields."""
        result = await self.judge.validate(request={"text": "Test"}, request_id="test_struct")

        assert hasattr(result, "decision")
        assert hasattr(result, "confidence")
        assert hasattr(result, "risk_level")
        assert hasattr(result, "latency_ms")
        assert hasattr(result, "stage_latencies")
        assert hasattr(result, "reasons")
        assert hasattr(result, "metadata")

    @pytest.mark.asyncio
    async def test_concurrent_validations(self):
        """Test that Judge #6 can handle concurrent requests."""
        requests = [{"text": f"Concurrent request {i}"} for i in range(10)]

        # Execute all validations concurrently
        results = await asyncio.gather(
            *[self.judge.validate(req, f"concurrent_{i}") for i, req in enumerate(requests)],
        )

        assert len(results) == 10
        for result in results:
            assert result.meets_sla(90.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
