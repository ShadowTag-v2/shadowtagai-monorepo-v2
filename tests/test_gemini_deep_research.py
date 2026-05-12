# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for gemini_deep_research package — Deep Research Max client.

Uses mock objects to test without live API calls.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import pytest

from _mock_helpers import make_mock_deep_research_client

from gemini_deep_research.client import (
    AGENT_FAST,
    AGENT_MAX,
    DEFAULT_POLL_INTERVAL_SECONDS,
    MAX_POLL_DURATION_SECONDS,
    DeepResearchClient,
    PlanResult,
    ResearchImage,
    ResearchReport,
    ResearchStatus,
    ResearchStreamEvent,
    ResearchTask,
)


# ---------------------------------------------------------------------------
# ResearchImage
# ---------------------------------------------------------------------------


class TestResearchImage:
    def test_save(self, tmp_path):
        data = base64.b64encode(b"fake-png-data").decode()
        img = ResearchImage(data=data, mime_type="image/png")

        out_path = str(tmp_path / "test.png")
        img.save(out_path)

        with open(out_path, "rb") as f:
            assert f.read() == b"fake-png-data"

    def test_default_mime(self):
        img = ResearchImage(data="AAAA")
        assert img.mime_type == "image/png"


# ---------------------------------------------------------------------------
# ResearchReport
# ---------------------------------------------------------------------------


class TestResearchReport:
    def test_defaults(self):
        report = ResearchReport(text="Hello")
        assert report.text == "Hello"
        assert report.images == []
        assert report.interaction_id == ""
        assert report.status == "completed"
        assert report.usage is None

    def test_with_images(self):
        img = ResearchImage(data="abc", mime_type="image/jpeg")
        report = ResearchReport(
            text="Research result",
            images=[img],
            interaction_id="int-789",
        )
        assert len(report.images) == 1
        assert report.images[0].mime_type == "image/jpeg"


# ---------------------------------------------------------------------------
# PlanResult
# ---------------------------------------------------------------------------


class TestPlanResult:
    def test_defaults(self):
        plan = PlanResult(
            plan_text="Step 1: Search...",
            interaction_id="plan-123",
        )
        assert plan.plan_text == "Step 1: Search..."
        assert plan.agent == AGENT_FAST

    def test_custom_agent(self):
        plan = PlanResult(
            plan_text="Deep plan",
            interaction_id="plan-456",
            agent=AGENT_MAX,
        )
        assert plan.agent == AGENT_MAX


# ---------------------------------------------------------------------------
# ResearchStreamEvent
# ---------------------------------------------------------------------------


class TestResearchStreamEvent:
    def test_text_event(self):
        event = ResearchStreamEvent(type="text", text="Hello")
        assert event.type == "text"
        assert event.text == "Hello"
        assert event.image is None

    def test_thought_event(self):
        event = ResearchStreamEvent(type="thought", text="Analyzing...")
        assert event.type == "thought"

    def test_image_event(self):
        img = ResearchImage(data="b64data")
        event = ResearchStreamEvent(type="image", image=img)
        assert event.type == "image"
        assert event.image.data == "b64data"


# ---------------------------------------------------------------------------
# ResearchTask
# ---------------------------------------------------------------------------


class TestResearchTask:
    def test_poll_without_client_raises(self):
        task = ResearchTask(interaction_id="task-1")
        with pytest.raises(ValueError, match="not bound"):
            task.poll()

    def test_wait_without_client_raises(self):
        task = ResearchTask(interaction_id="task-2")
        with pytest.raises(ValueError, match="not bound"):
            task.wait(poll_interval=1, timeout=1)


# ---------------------------------------------------------------------------
# ResearchStatus enum
# ---------------------------------------------------------------------------


class TestResearchStatus:
    def test_values(self):
        assert ResearchStatus.IN_PROGRESS == "in_progress"
        assert ResearchStatus.COMPLETED == "completed"
        assert ResearchStatus.FAILED == "failed"
        assert ResearchStatus.CANCELLED == "cancelled"


# ---------------------------------------------------------------------------
# DeepResearchClient — agent selection
# ---------------------------------------------------------------------------


class TestClientInit:
    def test_default_agent(self):
        client = make_mock_deep_research_client(agent=AGENT_FAST)
        assert client._agent == AGENT_FAST

    def test_max_depth_selects_max_agent(self):
        client = DeepResearchClient(api_key="fake", max_depth=True)
        assert client._agent == AGENT_MAX

    def test_explicit_agent(self):
        client = DeepResearchClient(api_key="fake", agent=AGENT_MAX)
        assert client._agent == AGENT_MAX


# ---------------------------------------------------------------------------
# DeepResearchClient — _extract_report
# ---------------------------------------------------------------------------


class TestExtractReport:
    def test_text_only(self):
        @dataclass
        class MockOutput:
            type: str = "text"
            text: str = "Research findings"

        @dataclass
        class MockInteraction:
            id: str = "int-report"
            status: str = "completed"
            outputs: list = None
            usage: Any = None

            def __post_init__(self):
                if self.outputs is None:
                    self.outputs = [MockOutput()]

        report = DeepResearchClient._extract_report(MockInteraction())
        assert report.text == "Research findings"
        assert report.interaction_id == "int-report"
        assert report.images == []

    def test_with_image(self):
        encoded_data = base64.b64encode(b"img").decode()

        @dataclass
        class MockTextOutput:
            type: str = "text"
            text: str = "Findings"

        @dataclass
        class MockImageOutput:
            type: str = "image"
            data: str = ""
            mime_type: str = "image/png"

        @dataclass
        class MockInteraction:
            id: str = "int-img"
            status: str = "completed"
            outputs: list = None
            usage: Any = None

        img_out = MockImageOutput(data=encoded_data)
        mock_interaction = MockInteraction(
            outputs=[MockTextOutput(), img_out],
        )

        report = DeepResearchClient._extract_report(mock_interaction)
        assert report.text == "Findings"
        assert len(report.images) == 1
        assert report.images[0].mime_type == "image/png"

    def test_with_usage(self):
        @dataclass
        class MockUsage:
            total_tokens: int = 5000

        @dataclass
        class MockOutput:
            type: str = "text"
            text: str = "Report"

        @dataclass
        class MockInteraction:
            id: str = "int-usage"
            status: str = "completed"
            outputs: list = None
            usage: MockUsage = None

            def __post_init__(self):
                if self.outputs is None:
                    self.outputs = [MockOutput()]
                if self.usage is None:
                    self.usage = MockUsage()

        report = DeepResearchClient._extract_report(MockInteraction())
        assert report.usage["total_tokens"] == 5000


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestDeepResearchConstants:
    def test_agent_names(self):
        assert "deep-research" in AGENT_FAST
        assert "max" in AGENT_MAX

    def test_poll_interval(self):
        assert DEFAULT_POLL_INTERVAL_SECONDS == 10

    def test_max_poll(self):
        assert MAX_POLL_DURATION_SECONDS == 3600
