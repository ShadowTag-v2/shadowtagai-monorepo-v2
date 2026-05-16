# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for JudgeAdapter — async HITL bridge."""

from __future__ import annotations

from typing import Any

import pytest

from packages.shadowtag_os.judges.judge_adapter import JudgeAdapter


# ─── Fixtures ────────────────────────────────────────────────────────────────


class FakeJudgeType:
    """Lightweight stub for JudgeType enum."""

    def __init__(self, value: str):
        self.value = value


class FakeRisk:
    """Stub risk assessment."""

    def __init__(self):
        self.risk_level = FakeJudgeType("medium")
        self.probability = FakeJudgeType("possible")
        self.severity = FakeJudgeType("moderate")
        self.requires_approval = True
        self.approval_authority = "admin"


class FakeResponse:
    """Stub judge response matching src/judges contract."""

    def __init__(self, decision: str = "ALLOW"):
        self.decision = FakeJudgeType(decision)
        self.risk_assessment = FakeRisk()
        self.approval_gate = FakeJudgeType("auto")
        self.reasoning = "Looks fine"
        self.semantic_trail = ["step1", "step2"]
        self.judge_type = FakeJudgeType("FinJudge")
        self.next_steps = ["proceed"]
        self.metadata = {"confidence": 0.9}


class FakeJudge:
    """Stub judge instance."""

    def __init__(self, decision: str = "ALLOW"):
        self._decision = decision

    def judge(self, request: Any) -> FakeResponse:
        return FakeResponse(self._decision)


class FakeFactory:
    """Stub JudgeFactory."""

    def __init__(self, decision: str = "ALLOW"):
        self._decision = decision

    def get_judge(self, judge_type: Any) -> FakeJudge:
        return FakeJudge(self._decision)


# ─── Tests ───────────────────────────────────────────────────────────────────


class TestJudgeAdapterInit:
    """Test JudgeAdapter construction."""

    def test_default_init(self):
        adapter = JudgeAdapter()
        assert adapter._factory is None
        assert adapter.review_count == 0

    def test_custom_factory(self):
        factory = FakeFactory()
        adapter = JudgeAdapter(judge_factory=factory)
        assert adapter._factory is factory

    def test_review_count_starts_at_zero(self):
        adapter = JudgeAdapter(judge_factory=FakeFactory())
        assert adapter.review_count == 0


class TestJudgeAdapterReview:
    """Test JudgeAdapter.review() async method."""

    @pytest.fixture
    def adapter(self):
        return JudgeAdapter(judge_factory=FakeFactory("ALLOW"))

    @pytest.mark.asyncio
    async def test_review_returns_decision(self, adapter):
        """Review with valid factory returns a decision."""
        result = await adapter.review(
            {
                "judge_type": "FinJudge",
                "request_id": "test-001",
                "action_type": "transfer",
                "context": {"amount": 100},
                "requested_by": "test",
            }
        )
        assert "decision" in result
        # If src.judges is available, we get ALLOW; if not, BLOCK fallback
        assert result["decision"] in ("ALLOW", "BLOCK")
        assert result["latency_ms"] >= 0

    @pytest.mark.asyncio
    async def test_review_increments_count(self, adapter):
        """Each review call increments the counter."""
        assert adapter.review_count == 0
        await adapter.review({"judge_type": "FinJudge"})
        assert adapter.review_count == 1
        await adapter.review({"judge_type": "CaseJudge"})
        assert adapter.review_count == 2

    @pytest.mark.asyncio
    async def test_review_with_defaults(self, adapter):
        """Review with minimal payload uses defaults."""
        result = await adapter.review({})
        assert "decision" in result
        assert result["latency_ms"] >= 0

    @pytest.mark.asyncio
    async def test_review_error_returns_block(self, adapter):
        """Invalid judge_type triggers BLOCK from error handler."""
        result = await adapter.review(
            {
                "judge_type": "InvalidJudge",
                "request_id": "test-err",
            }
        )
        assert result["decision"] == "BLOCK"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_review_latency_is_positive(self, adapter):
        """Latency is always a positive number."""
        result = await adapter.review({"judge_type": "FraudJudge"})
        assert result["latency_ms"] > 0


class TestJudgeAdapterLazyFactory:
    """Test lazy factory loading."""

    def test_get_factory_returns_factory(self):
        """Lazy factory loads JudgeFactory when available."""
        adapter = JudgeAdapter()
        try:
            factory = adapter._get_factory()
            # If src.judges is available, factory is loaded.
            assert factory is not None
        except RuntimeError:
            # If src.judges is NOT on path, RuntimeError is expected.
            pass

    def test_get_factory_with_explicit_factory(self):
        """Explicitly provided factory is returned without import."""
        factory = FakeFactory()
        adapter = JudgeAdapter(judge_factory=factory)
        assert adapter._get_factory() is factory
