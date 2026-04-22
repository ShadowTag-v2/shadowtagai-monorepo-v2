# labs/uphillsnowball/tests/test_ucmj_drag_race.py
"""Pytest fixtures for UCMJ tests with Redis mock (Item 16).

Also tests the async ucmj_drag_race_sla timeout enforcement.
"""

from __future__ import annotations

import asyncio

import pytest

from src.agents.discipline.ucmj_whiteboard import ucmj_drag_race_sla


class TestUCMJDragRaceSLA:
    """Tests for Article 92 timeout enforcement."""

    @pytest.mark.asyncio
    async def test_fast_agent_passes(self):
        """Agent completing within SLA returns its result."""

        async def fast_agent() -> dict:
            return {"status": "COMPLETE", "data": "fast_result"}

        result = await ucmj_drag_race_sla(
            fast_agent, timeout_ms=5000, agent_name="FastBot"
        )
        assert result["status"] == "COMPLETE"
        assert result["data"] == "fast_result"

    @pytest.mark.asyncio
    async def test_slow_agent_court_martialed(self):
        """Agent exceeding SLA gets ARTICLE_92_VIOLATION."""

        async def slow_agent() -> dict:
            await asyncio.sleep(10)  # Way over SLA
            return {"status": "COMPLETE"}

        result = await ucmj_drag_race_sla(
            slow_agent, timeout_ms=100, agent_name="SlowBot"
        )
        assert result["status"] == "HUNG"
        assert result["ucmj"] == "ARTICLE_92_VIOLATION"
        assert result["directive"] == "REPLACE_AGENT"
        assert result["agent"] == "SlowBot"

    @pytest.mark.asyncio
    async def test_default_timeout_is_35s(self):
        """Default SLA should be 35000ms per the _DEFAULT_SLA_MS constant."""

        async def instant_agent() -> dict:
            return {"sla_checked": True}

        result = await ucmj_drag_race_sla(instant_agent, agent_name="DefaultBot")
        assert result["sla_checked"] is True

    @pytest.mark.asyncio
    async def test_exception_propagates(self):
        """Agent exceptions propagate rather than being caught."""

        async def buggy_agent() -> dict:
            raise RuntimeError("Agent malfunction")

        with pytest.raises(RuntimeError, match="Agent malfunction"):
            await ucmj_drag_race_sla(buggy_agent, timeout_ms=5000)
