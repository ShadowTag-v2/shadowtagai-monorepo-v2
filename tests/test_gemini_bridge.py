# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for the Gemini Pipeline Bridge (AGNT STATE B P4.1).

Tests GeminiPairProgrammer and GeminiResearchSweep without live API calls.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock


from speculation_engine.gemini_bridge import (
    GeminiPairProgrammer,
    GeminiResearchSweep,
    PairSession,
    PipelineMode,
    SweepResult,
)


# ---------------------------------------------------------------------------
# PipelineMode
# ---------------------------------------------------------------------------


class TestPipelineMode:
    def test_values(self):
        assert PipelineMode.PAIR_PROGRAMMING == "pair_programming"
        assert PipelineMode.RESEARCH_SWEEP == "research_sweep"
        assert PipelineMode.HYBRID == "hybrid"


# ---------------------------------------------------------------------------
# PairSession
# ---------------------------------------------------------------------------


class TestPairSession:
    def test_defaults(self):
        session = PairSession(session_id="test-1")
        assert session.session_id == "test-1"
        assert session.interaction_chain == []
        assert session.model == "gemini-3-flash-preview"
        assert session.total_tokens == 0
        assert session.turn_count == 0

    def test_duration(self):
        session = PairSession(session_id="test-2")
        time.sleep(0.01)
        assert session.duration_seconds >= 0.01

    def test_turn_count(self):
        session = PairSession(
            session_id="test-3",
            interaction_chain=["a", "b", "c"],
        )
        assert session.turn_count == 3


# ---------------------------------------------------------------------------
# SweepResult
# ---------------------------------------------------------------------------


class TestSweepResult:
    def test_defaults(self):
        result = SweepResult(query="test", report_text="Hello")
        assert result.query == "test"
        assert result.report_text == "Hello"
        assert result.images == []
        assert result.duration_seconds == 0.0
        assert result.interaction_id == ""
        assert result.agent == ""

    def test_full(self):
        result = SweepResult(
            query="EV market",
            report_text="Report...",
            duration_seconds=300.0,
            interaction_id="int-sweep",
            agent="deep-research-max-preview-04-2026",
        )
        assert result.duration_seconds == 300.0
        assert "max" in result.agent


# ---------------------------------------------------------------------------
# GeminiPairProgrammer — mocked
# ---------------------------------------------------------------------------


class TestGeminiPairProgrammer:
    def test_lazy_client_import(self):
        """Verify the client is lazily initialized."""
        programmer = GeminiPairProgrammer(api_key="fake")
        assert programmer._client is None

    def test_start_session(self):
        programmer = GeminiPairProgrammer(api_key="fake")

        mock_result = MagicMock()
        mock_result.id = "interaction-boot"
        mock_result.usage = {"total_tokens": 50}

        mock_ic = MagicMock()
        mock_ic.create.return_value = mock_result
        programmer._client = mock_ic

        session = programmer.start_session(
            system_prompt="Test system prompt",
            model="gemini-3-flash-preview",
        )

        assert session.session_id.startswith("pair-")
        assert "interaction-boot" in session.interaction_chain
        assert session.total_tokens == 50

    def test_send_appends_chain(self):
        programmer = GeminiPairProgrammer(api_key="fake")

        mock_result = MagicMock()
        mock_result.id = "resp-1"
        mock_result.usage = {"total_tokens": 30}

        mock_client = MagicMock()
        mock_client.create.return_value = mock_result
        programmer._client = mock_client

        session = PairSession(
            session_id="test",
            interaction_chain=["boot"],
            model="gemini-3-flash-preview",
        )

        programmer.send("Hello", session=session)
        assert "resp-1" in session.interaction_chain
        assert session.total_tokens == 30


# ---------------------------------------------------------------------------
# GeminiResearchSweep — mocked
# ---------------------------------------------------------------------------


class TestGeminiResearchSweep:
    def test_lazy_client_import(self):
        sweep = GeminiResearchSweep(api_key="fake")
        assert sweep._client is None

    def test_max_depth_default(self):
        sweep = GeminiResearchSweep(api_key="fake")
        assert sweep._max_depth is True

    def test_max_depth_false(self):
        sweep = GeminiResearchSweep(api_key="fake", max_depth=False)
        assert sweep._max_depth is False
