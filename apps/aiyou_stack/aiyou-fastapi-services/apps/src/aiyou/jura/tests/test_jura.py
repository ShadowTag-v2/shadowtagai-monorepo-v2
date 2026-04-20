"""Tests for JURA Protocol: Cost-aware agent routing.

Tests:
- JuraClassifier: Tier classification logic
- JuraLimiter: Constraint enforcement
- JuraCostTracker: Cost accounting
- JuraRouter: End-to-end routing
"""

from datetime import UTC, datetime

import pytest

from ..classifier import CostTier, JuraClassifier
from ..cost_tracker import JuraCostRecord, JuraCostTracker
from ..limiter import JuraLimiter
from ..router import JuraRouter

# ============================================================================
# JuraClassifier Tests
# ============================================================================


class TestJuraClassifier:
    """Tests for tier classification logic."""

    def setup_method(self):
        self.classifier = JuraClassifier()

    def test_user_override(self):
        """User override should always be respected."""
        result = self.classifier.classify(
            task="simple task",
            context_size=100,
            override=CostTier.PRO,
        )
        assert result.tier == CostTier.PRO
        assert "override" in result.reason.lower()

    def test_governance_always_pro(self):
        """Governance tasks should always use PRO tier."""
        result = self.classifier.classify(
            task="simple governance check",
            context_size=100,
            task_type="governance",
        )
        assert result.tier == CostTier.PRO
        assert "governance" in result.reason.lower()

    def test_large_context_uses_pro(self):
        """Large context (>8K tokens) should use PRO tier."""
        result = self.classifier.classify(
            task="analyze this",
            context_size=10000,
        )
        assert result.tier == CostTier.PRO
        assert "context" in result.reason.lower()

    def test_medium_context_uses_flash(self):
        """Medium context (1K-8K tokens) should use FLASH tier."""
        result = self.classifier.classify(
            task="analyze this",
            context_size=5000,
        )
        assert result.tier == CostTier.FLASH

    def test_simple_task_uses_free(self):
        """Simple, small context tasks should use FREE tier."""
        result = self.classifier.classify(
            task="what is 2+2",
            context_size=50,
        )
        assert result.tier == CostTier.FREE
        assert result.complexity_score < 0.5

    def test_high_complexity_keywords(self):
        """High complexity keywords should increase tier."""
        result = self.classifier.classify(
            task="comprehensive security audit of the architecture",
            context_size=100,
        )
        assert result.tier in [CostTier.FLASH, CostTier.PRO]
        assert result.complexity_score > 0.3

    def test_low_complexity_keywords(self):
        """Low complexity keywords should keep tier low."""
        result = self.classifier.classify(
            task="simple yes/no question",
            context_size=50,
        )
        assert result.tier == CostTier.FREE

    def test_complexity_score_range(self):
        """Complexity score should be between 0.0 and 1.0."""
        for task in ["hi", "complex multi-step analysis", "", "x" * 500]:
            result = self.classifier.classify(task=task, context_size=0)
            assert 0.0 <= result.complexity_score <= 1.0

    def test_token_estimation(self):
        """Token estimation should be roughly 4 chars per token."""
        text = "hello world"  # 11 chars
        tokens = self.classifier.estimate_tokens(text)
        assert tokens == 2  # 11 // 4 = 2


# ============================================================================
# JuraLimiter Tests
# ============================================================================


class TestJuraLimiter:
    """Tests for tier constraint enforcement."""

    def setup_method(self):
        self.limiter = JuraLimiter()

    def test_free_tier_limits(self):
        """FREE tier should have 1 agent, 5s timeout, Grok model."""
        limits = self.limiter.get_limits(CostTier.FREE)
        assert limits.max_agents == 1
        assert limits.max_response_time_ms == 5000
        assert "grok" in limits.models[0].lower()

    def test_flash_tier_limits(self):
        """FLASH tier should have 3 agents, 2s timeout, Gemini Flash."""
        limits = self.limiter.get_limits(CostTier.FLASH)
        assert limits.max_agents == 3
        assert limits.max_response_time_ms == 2000
        assert "flash" in limits.models[0].lower()

    def test_pro_tier_limits(self):
        """PRO tier should have 8 agents, 10s timeout, Pro/Claude models."""
        limits = self.limiter.get_limits(CostTier.PRO)
        assert limits.max_agents == 8
        assert limits.max_response_time_ms == 10000
        assert any("pro" in m.lower() or "claude" in m.lower() for m in limits.models)

    def test_auto_tier_raises(self):
        """Getting limits for AUTO tier should raise ValueError."""
        with pytest.raises(ValueError):
            self.limiter.get_limits(CostTier.AUTO)

    def test_clamp_agents_respects_limits(self):
        """Agent count should be clamped to tier limits."""
        assert self.limiter.clamp_agents(CostTier.FREE, 10) == 1
        assert self.limiter.clamp_agents(CostTier.FLASH, 10) == 3
        assert self.limiter.clamp_agents(CostTier.PRO, 10) == 8

    def test_clamp_agents_minimum_one(self):
        """Agent count should never be less than 1."""
        assert self.limiter.clamp_agents(CostTier.FREE, 0) == 1
        assert self.limiter.clamp_agents(CostTier.FREE, -5) == 1

    def test_check_availability(self):
        """Availability check should validate agent count."""
        avail, reason = self.limiter.check_availability(CostTier.FREE, 1)
        assert avail is True

        avail, reason = self.limiter.check_availability(CostTier.FREE, 5)
        assert avail is False
        assert "limit" in reason.lower()

    def test_cost_estimation(self):
        """Cost estimation should return reasonable values."""
        # FREE tier (Grok): $2/1M input, $10/1M output
        cost = self.limiter.estimate_cost(CostTier.FREE, 1000, 500)
        assert cost > 0
        assert cost < 0.1  # Reasonable for 1K/500 tokens

        # FLASH tier (Gemini Flash): Much cheaper
        flash_cost = self.limiter.estimate_cost(CostTier.FLASH, 1000, 500)
        assert flash_cost < cost  # Flash should be cheaper than Grok

    def test_cost_limit_check(self):
        """Cost limit check should enforce tier maximums."""
        within, reason = self.limiter.check_cost_limit(CostTier.FREE, 0.0005)
        assert within is True

        within, reason = self.limiter.check_cost_limit(CostTier.FREE, 0.01)
        assert within is False

    def test_get_primary_model(self):
        """Primary model should be first in the list."""
        assert self.limiter.get_primary_model(CostTier.FREE) == "grok-2"
        assert "flash" in self.limiter.get_primary_model(CostTier.FLASH).lower()


# ============================================================================
# JuraCostTracker Tests
# ============================================================================


class TestJuraCostTracker:
    """Tests for cost accounting."""

    def setup_method(self):
        self.tracker = JuraCostTracker()

    def test_record_creates_entry(self):
        """Recording should create a cost record."""
        record = self.tracker.record(
            tier=CostTier.FLASH,
            agent_ids=["agent_1", "agent_2"],
            model_used="gemini-3.1-flash-lite-preview",
            input_tokens=500,
            output_tokens=200,
            cost_usd=0.005,
            latency_ms=150,
            success=True,
        )
        assert record.tier == CostTier.FLASH
        assert len(record.agent_ids) == 2
        assert record.success is True

    def test_metrics_accumulate(self):
        """Metrics should accumulate across records."""
        for i in range(5):
            self.tracker.record(
                tier=CostTier.FLASH,
                agent_ids=[f"agent_{i}"],
                model_used="gemini-3.1-flash-lite-preview",
                input_tokens=100,
                output_tokens=50,
                cost_usd=0.001,
                latency_ms=100,
                success=True,
            )

        metrics = self.tracker.get_metrics()
        assert metrics["total_requests"] == 5
        assert metrics["total_cost_usd"] == 0.005

    def test_per_tier_metrics(self):
        """Should track metrics per tier."""
        # 3 FLASH requests
        for _ in range(3):
            self.tracker.record(
                tier=CostTier.FLASH,
                agent_ids=["a1"],
                model_used="gemini-3.1-flash-lite-preview",
                input_tokens=100,
                output_tokens=50,
                cost_usd=0.01,
                latency_ms=100,
                success=True,
            )

        # 1 PRO request
        self.tracker.record(
            tier=CostTier.PRO,
            agent_ids=["a2"],
            model_used="gemini-3.1-flash-lite-preview",
            input_tokens=500,
            output_tokens=200,
            cost_usd=0.10,
            latency_ms=500,
            success=True,
        )

        tier_metrics = self.tracker.get_tier_metrics(CostTier.FLASH)
        assert tier_metrics["request_count"] == 3

        tier_metrics = self.tracker.get_tier_metrics(CostTier.PRO)
        assert tier_metrics["request_count"] == 1

    def test_per_agent_attribution(self):
        """Cost should be split evenly among agents."""
        self.tracker.record(
            tier=CostTier.FLASH,
            agent_ids=["agent_a", "agent_b"],
            model_used="gemini-3.1-flash-lite-preview",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.10,  # $0.10 split between 2 agents
            latency_ms=100,
            success=True,
        )

        a_metrics = self.tracker.get_agent_metrics("agent_a")
        b_metrics = self.tracker.get_agent_metrics("agent_b")

        assert a_metrics["total_cost"] == 0.05
        assert b_metrics["total_cost"] == 0.05

    def test_history_limit(self):
        """Should only keep last 1000 records."""
        for i in range(1100):
            self.tracker.record(
                tier=CostTier.FREE,
                agent_ids=[f"a{i}"],
                model_used="grok-2",
                input_tokens=10,
                output_tokens=5,
                cost_usd=0.0001,
                latency_ms=50,
                success=True,
            )

        assert len(self.tracker._records) == 1000

    def test_reset(self):
        """Reset should clear all data."""
        self.tracker.record(
            tier=CostTier.FLASH,
            agent_ids=["a1"],
            model_used="gemini-3.1-flash-lite-preview",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            latency_ms=100,
            success=True,
        )

        self.tracker.reset()
        metrics = self.tracker.get_metrics()
        assert metrics["total_requests"] == 0
        assert metrics["total_cost_usd"] == 0.0

    def test_cost_projection(self):
        """Should project monthly costs from sample data."""
        # Record some sample data
        for _ in range(10):
            self.tracker.record(
                tier=CostTier.FLASH,
                agent_ids=["a1"],
                model_used="gemini-3.1-flash-lite-preview",
                input_tokens=100,
                output_tokens=50,
                cost_usd=0.01,
                latency_ms=100,
                success=True,
            )

        projection = self.tracker.get_cost_projection(daily_requests=1000)
        assert "total_monthly_cost_usd" in projection
        assert projection["monthly_requests"] == 30000

    def test_export_json(self):
        """Should export to valid JSON."""
        self.tracker.record(
            tier=CostTier.FLASH,
            agent_ids=["a1"],
            model_used="gemini-3.1-flash-lite-preview",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            latency_ms=100,
            success=True,
        )

        import json

        json_str = self.tracker.export_json()
        data = json.loads(json_str)
        assert "metrics" in data
        assert "records" in data


# ============================================================================
# JuraRouter Tests
# ============================================================================


class TestJuraRouter:
    """Tests for end-to-end routing."""

    def setup_method(self):
        self.router = JuraRouter()

    @pytest.mark.asyncio
    async def test_route_simple_task(self):
        """Simple task should route to FREE tier."""
        result = await self.router.route(
            task="what is 2+2",
            context_size=50,
        )
        assert result.success is True
        assert result.tier == CostTier.FREE
        assert result.model_used == "grok-2"

    @pytest.mark.asyncio
    async def test_route_complex_task(self):
        """Complex task should route to higher tier."""
        result = await self.router.route(
            task="comprehensive security architecture review",
            context_size=5000,
        )
        assert result.success is True
        assert result.tier in [CostTier.FLASH, CostTier.PRO]

    @pytest.mark.asyncio
    async def test_route_governance(self):
        """Governance task should always use PRO tier."""
        result = await self.router.route_governance(
            task="review compliance",
            context_size=100,
        )
        assert result.success is True
        assert result.tier == CostTier.PRO

    @pytest.mark.asyncio
    async def test_route_with_override(self):
        """User override should be respected."""
        result = await self.router.route(
            task="simple task",
            context_size=50,
            cost_tier=CostTier.PRO,
        )
        assert result.tier == CostTier.PRO

    @pytest.mark.asyncio
    async def test_route_records_cost(self):
        """Route should record cost in tracker."""
        await self.router.route(
            task="test task",
            context_size=100,
        )
        metrics = self.router.cost_tracker.get_metrics()
        assert metrics["total_requests"] == 1

    @pytest.mark.asyncio
    async def test_route_clamps_agents(self):
        """Agent count should be clamped to tier limits."""
        result = await self.router.route(
            task="simple task",
            context_size=50,
            requested_agents=100,  # Way over limit
        )
        assert len(result.agent_ids) <= 1  # FREE tier max

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Stats should include cost metrics and pool info."""
        await self.router.route(task="test", context_size=100)
        stats = self.router.get_stats()

        assert "cost_metrics" in stats
        assert "pool_stats" in stats
        assert "tier_configs" in stats

    @pytest.mark.asyncio
    async def test_tier_recommendation(self):
        """Should provide tier recommendation without routing."""
        rec = self.router.get_tier_recommendation(
            task="analyze complex architecture",
            context_size=5000,
        )
        assert "recommended_tier" in rec
        assert "reason" in rec
        assert "tier_limits" in rec


# ============================================================================
# JuraCostRecord Tests
# ============================================================================


class TestJuraCostRecord:
    """Tests for cost record serialization."""

    def test_to_dict(self):
        """Should convert to dictionary."""
        record = JuraCostRecord(
            request_id="test-123",
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            tier=CostTier.FLASH,
            agent_ids=["a1", "a2"],
            model_used="gemini-3.1-flash-lite-preview",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            latency_ms=150,
            success=True,
            task_type="execution",
            metadata={"key": "value"},
        )

        d = record.to_dict()
        assert d["request_id"] == "test-123"
        assert d["tier"] == "flash"
        assert d["metadata"]["key"] == "value"

    def test_from_dict(self):
        """Should reconstruct from dictionary."""
        data = {
            "request_id": "test-456",
            "timestamp": "2024-01-01T12:00:00+00:00",
            "tier": "pro",
            "agent_ids": ["a1"],
            "model_used": "gemini-3.1-flash-lite-preview",
            "input_tokens": 500,
            "output_tokens": 200,
            "cost_usd": 0.10,
            "latency_ms": 500,
            "success": False,
            "task_type": "governance",
            "metadata": {"error": "timeout"},
        }

        record = JuraCostRecord.from_dict(data)
        assert record.request_id == "test-456"
        assert record.tier == CostTier.PRO
        assert record.success is False


# ============================================================================
# Integration Tests
# ============================================================================


class TestJuraIntegration:
    """Integration tests for full JURA workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete routing workflow."""
        router = JuraRouter()

        # Route several tasks
        tasks = [
            ("simple question", 50, CostTier.AUTO),
            ("detailed analysis required", 3000, CostTier.AUTO),
            ("force pro tier", 50, CostTier.PRO),
        ]

        results = []
        for task, ctx, tier in tasks:
            result = await router.route(
                task=task,
                context_size=ctx,
                cost_tier=tier,
            )
            results.append(result)

        # Verify all succeeded
        assert all(r.success for r in results)

        # Check cost tracking
        metrics = router.cost_tracker.get_metrics()
        assert metrics["total_requests"] == 3
        assert metrics["total_cost_usd"] > 0

    @pytest.mark.asyncio
    async def test_tier_distribution(self):
        """Test that tiers are correctly distributed."""
        router = JuraRouter()

        # Route tasks that should hit different tiers
        await router.route(task="hi", context_size=10, cost_tier=CostTier.FREE)  # Force FREE
        await router.route(task="analyze code", context_size=2000)  # FLASH
        await router.route_governance(task="compliance check")  # PRO

        metrics = router.cost_tracker.get_metrics()
        breakdown = metrics["tier_breakdown"]

        assert breakdown["free"]["request_count"] == 1
        assert breakdown["flash"]["request_count"] == 1
        assert breakdown["pro"]["request_count"] == 1
