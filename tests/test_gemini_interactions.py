# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for gemini_interactions package — Interactions API client.

Uses mock objects to test without live API calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from gemini_interactions.tools import (
    ToolDefinition,
    code_execution_tool,
    function_tool,
    google_search_tool,
    mcp_server_tool,
    url_context_tool,
)


# ---------------------------------------------------------------------------
# Tool builders
# ---------------------------------------------------------------------------


class TestGoogleSearchTool:
    def test_basic(self):
        tool = google_search_tool()
        assert tool == {"type": "google_search"}

    def test_with_search_types(self):
        tool = google_search_tool(search_types=["web_search", "image_search"])
        assert tool["type"] == "google_search"
        assert tool["search_types"] == ["web_search", "image_search"]


class TestUrlContextTool:
    def test_basic(self):
        tool = url_context_tool()
        assert tool == {"type": "url_context"}


class TestCodeExecutionTool:
    def test_basic(self):
        tool = code_execution_tool()
        assert tool == {"type": "code_execution"}


class TestMcpServerTool:
    def test_basic(self):
        tool = mcp_server_tool(
            name="my_server",
            url="https://example.com/mcp",
        )
        assert tool["type"] == "mcp_server"
        assert tool["name"] == "my_server"
        assert tool["url"] == "https://example.com/mcp"
        assert "headers" not in tool
        assert "allowed_tools" not in tool

    def test_with_headers_and_allowed(self):
        tool = mcp_server_tool(
            name="sec_server",
            url="https://example.com/mcp",
            headers={"Authorization": "Bearer token123"},
            allowed_tools=["search", "fetch"],
        )
        assert tool["headers"]["Authorization"] == "Bearer token123"
        assert tool["allowed_tools"] == ["search", "fetch"]


class TestFunctionTool:
    def test_basic(self):
        tool = function_tool(
            name="get_weather",
            description="Gets weather for a city.",
            parameters={
                "type": "object",
                "properties": {"city": {"type": "string"}},
            },
        )
        assert tool["type"] == "function"
        assert tool["name"] == "get_weather"
        assert tool["description"] == "Gets weather for a city."
        assert tool["parameters"]["type"] == "object"


class TestToolDefinition:
    def test_to_dict(self):
        td = ToolDefinition(type="google_search")
        assert td.to_dict() == {"type": "google_search"}

    def test_to_dict_with_config(self):
        td = ToolDefinition(
            type="mcp_server",
            config={"name": "s1", "url": "https://x.com"},
        )
        d = td.to_dict()
        assert d["type"] == "mcp_server"
        assert d["name"] == "s1"
        assert d["url"] == "https://x.com"

    def test_frozen(self):
        td = ToolDefinition(type="test")
        with pytest.raises(AttributeError):
            td.type = "changed"


# ---------------------------------------------------------------------------
# Client — InteractionResult
# ---------------------------------------------------------------------------


class TestInteractionResult:
    def test_from_interaction_text(self):
        from gemini_interactions.client import InteractionResult

        @dataclass
        class MockOutput:
            type: str = "text"
            text: str = "Hello world"

        @dataclass
        class MockUsage:
            total_tokens: int = 100
            prompt_tokens: int = 40
            completion_tokens: int = 60

        @dataclass
        class MockInteraction:
            id: str = "int-123"
            status: str = "completed"
            outputs: list = None
            usage: MockUsage = None

            def __post_init__(self):
                if self.outputs is None:
                    self.outputs = [MockOutput()]
                if self.usage is None:
                    self.usage = MockUsage()

        mock = MockInteraction()
        result = InteractionResult.from_interaction(mock)

        assert result.id == "int-123"
        assert result.status == "completed"
        assert result.text == "Hello world"
        assert result.usage["total_tokens"] == 100
        assert result.usage["prompt_tokens"] == 40
        assert result.usage["completion_tokens"] == 60

    def test_from_interaction_no_text(self):
        from gemini_interactions.client import InteractionResult

        @dataclass
        class MockInteraction:
            id: str = "int-456"
            status: str = "completed"
            outputs: list = None
            usage: Any = None

            def __post_init__(self):
                if self.outputs is None:
                    self.outputs = []

        result = InteractionResult.from_interaction(MockInteraction())
        assert result.text is None


# ---------------------------------------------------------------------------
# Client — StreamEvent parsing
# ---------------------------------------------------------------------------


class TestStreamEventParsing:
    def test_parse_text_delta(self):
        from gemini_interactions.client import InteractionsClient

        @dataclass
        class MockDelta:
            type: str = "text"
            text: str = "chunk"

        @dataclass
        class MockChunk:
            event_type: str = "content.delta"
            event_id: str = "ev-1"
            delta: MockDelta = None
            index: int = 0

            def __post_init__(self):
                if self.delta is None:
                    self.delta = MockDelta()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.event_type == "content.delta"
        assert event.delta_type == "text"
        assert event.text == "chunk"
        assert event.event_id == "ev-1"

    def test_parse_interaction_start(self):
        from gemini_interactions.client import InteractionsClient

        @dataclass
        class MockInteractionObj:
            id: str = "start-id-99"

        @dataclass
        class MockChunk:
            event_type: str = "interaction.start"
            event_id: str = None
            interaction: MockInteractionObj = None

            def __post_init__(self):
                if self.interaction is None:
                    self.interaction = MockInteractionObj()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.event_type == "interaction.start"
        assert event.interaction_id == "start-id-99"

    def test_parse_function_call_delta(self):
        from gemini_interactions.client import InteractionsClient

        @dataclass
        class MockDelta:
            type: str = "function_call"
            id: str = "fc-1"
            name: str = "get_weather"
            arguments: dict = None

            def __post_init__(self):
                if self.arguments is None:
                    self.arguments = {"city": "NYC"}

        @dataclass
        class MockChunk:
            event_type: str = "content.delta"
            event_id: str = "ev-fc"
            delta: MockDelta = None
            index: int = 0

            def __post_init__(self):
                if self.delta is None:
                    self.delta = MockDelta()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.delta_type == "function_call"
        assert event.function_call["name"] == "get_weather"
        assert event.function_call["arguments"]["city"] == "NYC"


# ---------------------------------------------------------------------------
# Client — build_kwargs
# ---------------------------------------------------------------------------


class TestBuildKwargs:
    def test_minimal(self):
        from gemini_interactions.client import InteractionsClient

        c = InteractionsClient.__new__(InteractionsClient)
        c._default_model = "gemini-3-flash-preview"

        kwargs = c._build_kwargs(input="Hello")
        assert kwargs["model"] == "gemini-3-flash-preview"
        assert kwargs["input"] == "Hello"
        assert kwargs["store"] is True
        assert "tools" not in kwargs
        assert "system_instruction" not in kwargs

    def test_full(self):
        from gemini_interactions.client import InteractionsClient

        c = InteractionsClient.__new__(InteractionsClient)
        c._default_model = "gemini-3-flash-preview"

        kwargs = c._build_kwargs(
            input="Hello",
            model="gemini-3-pro-preview",
            previous_interaction_id="prev-123",
            tools=[{"type": "google_search"}],
            system_instruction="Be helpful.",
            generation_config={"temperature": 0.5},
            response_format={"type": "json_object"},
            response_modalities=["text"],
            store=False,
        )
        assert kwargs["model"] == "gemini-3-pro-preview"
        assert kwargs["previous_interaction_id"] == "prev-123"
        assert kwargs["tools"] == [{"type": "google_search"}]
        assert kwargs["system_instruction"] == "Be helpful."
        assert kwargs["generation_config"]["temperature"] == 0.5
        assert kwargs["response_format"]["type"] == "json_object"
        assert kwargs["response_modalities"] == ["text"]
        assert kwargs["store"] is False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_supported_models(self):
        from gemini_interactions.client import SUPPORTED_MODELS

        assert "gemini-3-flash-preview" in SUPPORTED_MODELS
        assert "gemini-3-pro-preview" in SUPPORTED_MODELS
        assert "gemini-2.5-flash" in SUPPORTED_MODELS
        assert "gemini-2.5-pro" in SUPPORTED_MODELS
        assert "gpt-4" not in SUPPORTED_MODELS
