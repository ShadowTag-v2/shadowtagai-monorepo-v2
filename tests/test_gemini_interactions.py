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
    computer_use_tool,
    file_search_tool,
    function_tool,
    google_search_tool,
    mcp_server_tool,
    url_context_tool,
)
from gemini_interactions.client import (
    EventType,
    InteractionsClient,
    InteractionResult,
    StreamAccumulator,
    StreamEvent,
)
from gemini_interactions.telemetry import NullTelemetry


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
        assert url_context_tool() == {"type": "url_context"}


class TestCodeExecutionTool:
    def test_basic(self):
        assert code_execution_tool() == {"type": "code_execution"}


class TestMcpServerTool:
    def test_basic(self):
        tool = mcp_server_tool(name="my_server", url="https://example.com/mcp")
        assert tool["type"] == "mcp_server"
        assert tool["name"] == "my_server"
        assert "headers" not in tool

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
            parameters={"type": "object", "properties": {"city": {"type": "string"}}},
        )
        assert tool["type"] == "function"
        assert tool["name"] == "get_weather"


class TestComputerUseTool:
    def test_defaults(self):
        tool = computer_use_tool()
        assert tool["type"] == "computer_use"
        assert tool["computer_use"]["environment"] == "browser"
        assert tool["computer_use"]["display_width_px"] == 1024
        assert tool["computer_use"]["display_height_px"] == 768

    def test_custom(self):
        tool = computer_use_tool(environment="desktop", display_width_px=1920, display_height_px=1080)
        assert tool["computer_use"]["environment"] == "desktop"
        assert tool["computer_use"]["display_width_px"] == 1920
        assert tool["computer_use"]["display_height_px"] == 1080


class TestFileSearchTool:
    def test_basic(self):
        tool = file_search_tool()
        assert tool == {"type": "file_search"}

    def test_with_file_ids(self):
        tool = file_search_tool(file_ids=["files/abc123", "files/def456"])
        assert tool["file_search"]["file_ids"] == ["files/abc123", "files/def456"]

    def test_with_vector_store(self):
        tool = file_search_tool(vector_store_ids=["vs-1"])
        assert tool["file_search"]["vector_store_ids"] == ["vs-1"]


class TestToolDefinition:
    def test_to_dict(self):
        assert ToolDefinition(type="google_search").to_dict() == {"type": "google_search"}

    def test_to_dict_with_config(self):
        d = ToolDefinition(type="mcp_server", config={"name": "s1", "url": "https://x.com"}).to_dict()
        assert d["type"] == "mcp_server"
        assert d["name"] == "s1"

    def test_frozen(self):
        td = ToolDefinition(type="test")
        with pytest.raises(AttributeError):
            td.type = "changed"


# ---------------------------------------------------------------------------
# Client — InteractionResult
# ---------------------------------------------------------------------------


class TestInteractionResult:
    def test_from_interaction_text(self):
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
                self.outputs = self.outputs if self.outputs is not None else [MockOutput()]
                self.usage = self.usage if self.usage is not None else MockUsage()

        result = InteractionResult.from_interaction(MockInteraction())
        assert result.id == "int-123"
        assert result.text == "Hello world"
        assert result.usage["total_tokens"] == 100

    def test_from_interaction_no_text(self):
        @dataclass
        class MockInteraction:
            id: str = "int-456"
            status: str = "completed"
            outputs: list = None
            usage: Any = None

            def __post_init__(self):
                self.outputs = self.outputs if self.outputs is not None else []

        assert InteractionResult.from_interaction(MockInteraction()).text is None

    def test_parallel_function_calls(self):
        """Multiple function_call outputs are collected."""

        @dataclass
        class MockFC:
            type: str = "function_call"
            name: str = ""
            id: str = ""
            arguments: dict = None

            def __post_init__(self):
                self.arguments = self.arguments or {}

        @dataclass
        class MockInteraction:
            id: str = "int-parallel"
            status: str = "completed"
            outputs: list = None
            usage: Any = None

            def __post_init__(self):
                self.outputs = self.outputs or [
                    MockFC(name="fn_a", id="c1"),
                    MockFC(name="fn_b", id="c2"),
                ]

        result = InteractionResult.from_interaction(MockInteraction())
        assert len(result.function_calls) == 2
        assert result.text is None

    def test_annotation_extraction_sdk_objects(self):
        """SDK annotation objects are normalized to dicts."""

        @dataclass
        class MockAnnotation:
            type: str = "file_citation"
            file_name: str = "doc.pdf"
            document_uri: str = "gs://bucket/doc.pdf"
            source: str = None
            start_index: int = 0
            end_index: int = 10

        @dataclass
        class MockOutput:
            type: str = "text"
            text: str = "See [1]."
            annotations: list = None

            def __post_init__(self):
                self.annotations = self.annotations or [MockAnnotation()]

        @dataclass
        class MockInteraction:
            id: str = "int-ann"
            status: str = "completed"
            outputs: list = None
            usage: Any = None

            def __post_init__(self):
                self.outputs = self.outputs or [MockOutput()]

        result = InteractionResult.from_interaction(MockInteraction())
        assert len(result.annotations) == 1
        assert result.annotations[0]["type"] == "file_citation"
        assert result.annotations[0]["file_name"] == "doc.pdf"


# ---------------------------------------------------------------------------
# Client — StreamEvent parsing
# ---------------------------------------------------------------------------


class TestStreamEventParsing:
    def test_parse_text_delta(self):
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
                self.delta = self.delta or MockDelta()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.delta_type == "text"
        assert event.text == "chunk"

    def test_parse_interaction_start(self):
        @dataclass
        class MockInteractionObj:
            id: str = "start-id-99"

        @dataclass
        class MockChunk:
            event_type: str = "interaction.start"
            event_id: str = None
            interaction: MockInteractionObj = None

            def __post_init__(self):
                self.interaction = self.interaction or MockInteractionObj()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.interaction_id == "start-id-99"

    def test_parse_function_call_delta(self):
        @dataclass
        class MockDelta:
            type: str = "function_call"
            id: str = "fc-1"
            name: str = "get_weather"
            arguments: dict = None

            def __post_init__(self):
                self.arguments = self.arguments or {"city": "NYC"}

        @dataclass
        class MockChunk:
            event_type: str = "content.delta"
            event_id: str = "ev-fc"
            delta: MockDelta = None
            index: int = 0

            def __post_init__(self):
                self.delta = self.delta or MockDelta()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.function_call["name"] == "get_weather"
        assert event.function_call["arguments"]["city"] == "NYC"

    def test_parse_thought_signature(self):
        @dataclass
        class MockDelta:
            type: str = "thought_signature"
            signature: str = "sig-abc-123"

        @dataclass
        class MockChunk:
            event_type: str = "content.delta"
            event_id: str = "ev-sig"
            delta: MockDelta = None
            index: int = 0

            def __post_init__(self):
                self.delta = self.delta or MockDelta()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.delta_type == "thought_signature"
        assert event.signature == "sig-abc-123"

    def test_parse_content_start(self):
        @dataclass
        class MockContent:
            type: str = "text"

        @dataclass
        class MockChunk:
            event_type: str = "content.start"
            event_id: str = "ev-cs"
            index: int = 0
            content: MockContent = None

            def __post_init__(self):
                self.content = self.content or MockContent()

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.event_type == EventType.CONTENT_START
        assert event.content_type == "text"
        assert event.index == 0

    def test_parse_content_stop(self):
        @dataclass
        class MockChunk:
            event_type: str = "content.stop"
            event_id: str = "ev-stop"
            index: int = 1

        event = InteractionsClient._parse_chunk(MockChunk())
        assert event.event_type == EventType.CONTENT_STOP
        assert event.index == 1


# ---------------------------------------------------------------------------
# StreamAccumulator
# ---------------------------------------------------------------------------


class TestStreamAccumulator:
    def test_text_reconstruction(self):
        """Feed content.start + two deltas + stop → single text output."""
        acc = StreamAccumulator()
        acc.feed(StreamEvent(event_type=EventType.CONTENT_START, index=0, content_type="text"))
        acc.feed(StreamEvent(event_type=EventType.CONTENT_DELTA, index=0, delta_type="text", text="Hello "))
        acc.feed(StreamEvent(event_type=EventType.CONTENT_DELTA, index=0, delta_type="text", text="world"))
        acc.feed(StreamEvent(event_type=EventType.CONTENT_STOP, index=0))
        assert len(acc.outputs) == 1
        assert acc.outputs[0]["type"] == "text"
        assert acc.outputs[0]["text"] == "Hello world"

    def test_mixed_thought_and_text(self):
        """Thought at index 0, text at index 1 → two outputs sorted by index."""
        acc = StreamAccumulator()
        acc.feed(StreamEvent(event_type=EventType.CONTENT_START, index=0, content_type="thought"))
        acc.feed(StreamEvent(event_type=EventType.CONTENT_DELTA, index=0, delta_type="thought_summary", thought="Thinking..."))
        acc.feed(StreamEvent(event_type=EventType.CONTENT_DELTA, index=0, delta_type="thought_signature", signature="sig-xyz"))
        acc.feed(StreamEvent(event_type=EventType.CONTENT_START, index=1, content_type="text"))
        acc.feed(StreamEvent(event_type=EventType.CONTENT_DELTA, index=1, delta_type="text", text="Answer"))
        outputs = acc.outputs
        assert len(outputs) == 2
        assert outputs[0]["type"] == "thought"
        assert outputs[0]["summary"] == "Thinking..."
        assert outputs[0]["signature"] == "sig-xyz"
        assert outputs[1]["text"] == "Answer"

    def test_function_call_reconstruction(self):
        acc = StreamAccumulator()
        acc.feed(StreamEvent(event_type=EventType.CONTENT_START, index=0, content_type="function_call"))
        acc.feed(
            StreamEvent(
                event_type=EventType.CONTENT_DELTA,
                index=0,
                delta_type="function_call",
                function_call={"id": "c1", "name": "search", "arguments": {"q": "test"}},
            )
        )
        assert acc.outputs[0]["name"] == "search"
        assert acc.outputs[0]["id"] == "c1"

    def test_interaction_id_and_usage(self):
        acc = StreamAccumulator()
        acc.feed(StreamEvent(event_type=EventType.INTERACTION_START, interaction_id="int-abc"))
        acc.feed(
            StreamEvent(
                event_type=EventType.INTERACTION_COMPLETE,
                interaction_id="int-abc",
                usage={"total_tokens": 50, "prompt_tokens": 20, "completion_tokens": 30},
            )
        )
        assert acc.interaction_id == "int-abc"
        assert acc.usage["total_tokens"] == 50
        assert acc.status == "completed"

    def test_empty_accumulator(self):
        acc = StreamAccumulator()
        assert acc.outputs == []
        assert acc.interaction_id is None


# ---------------------------------------------------------------------------
# Client — build_kwargs
# ---------------------------------------------------------------------------


class TestBuildKwargs:
    def test_minimal(self):
        c = InteractionsClient.__new__(InteractionsClient)
        c._default_model = "gemini-3-flash-preview"
        kwargs = c._build_kwargs(input="Hello")
        assert kwargs["model"] == "gemini-3-flash-preview"
        assert kwargs["store"] is True
        assert "tools" not in kwargs

    def test_full(self):
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
        assert kwargs["store"] is False


# ---------------------------------------------------------------------------
# Constants & Exports
# ---------------------------------------------------------------------------


class TestConstants:
    def test_supported_models(self):
        from gemini_interactions.client import SUPPORTED_MODELS

        assert "gemini-3-flash-preview" in SUPPORTED_MODELS
        assert "gemini-2.5-computer-use-preview-10-2025" in SUPPORTED_MODELS
        assert "gpt-4" not in SUPPORTED_MODELS

    def test_exports(self):
        import gemini_interactions

        assert hasattr(gemini_interactions, "StreamAccumulator")
        assert hasattr(gemini_interactions, "EventType")
        assert hasattr(gemini_interactions, "computer_use_tool")
        assert hasattr(gemini_interactions, "file_search_tool")
        assert hasattr(gemini_interactions, "ConversationSession")


# ---------------------------------------------------------------------------
# ConversationSession — auto-chaining + mixed interactions
# ---------------------------------------------------------------------------


class _MockInteractionsAPI:
    """Mock for client.interactions with create/get/list."""

    def __init__(self):
        self._call_count = 0
        self._create_calls: list[dict] = []

    def create(self, **kwargs):
        self._call_count += 1
        self._create_calls.append(kwargs)

        @dataclass
        class _MockOutput:
            type: str = "text"
            text: str = f"Response {self._call_count}"

        @dataclass
        class _MockResult:
            id: str = f"int-{self._call_count}"
            status: str = "completed"
            outputs: list = None

            def __post_init__(self):
                self.outputs = self.outputs or [_MockOutput()]

        return _MockResult()

    def get(self, interaction_id, **kwargs):
        @dataclass
        class _MockResult:
            id: str = interaction_id
            status: str = "completed"
            outputs: list = None

            def __post_init__(self):
                self.outputs = self.outputs or []

        return _MockResult()

    def list(self, **kwargs):
        @dataclass
        class _MockListResult:
            interactions: list = None

            def __post_init__(self):
                self.interactions = self.interactions or []

        return _MockListResult()


def _make_mock_client():
    """Create an InteractionsClient with mocked API."""
    client = InteractionsClient.__new__(InteractionsClient)
    client._api_key = "test-key"
    client._default_model = "gemini-3-flash-preview"
    client._telemetry = NullTelemetry()
    client._client = type("MockGenAI", (), {"interactions": _MockInteractionsAPI()})()
    return client


class TestConversationSession:
    def test_auto_chain_first_turn_no_previous_id(self):
        """First turn should not have previous_interaction_id."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")
        session.send("Hello")

        api = client._client.interactions
        assert api._create_calls[0].get("previous_interaction_id") is None

    def test_auto_chain_second_turn_has_previous_id(self):
        """Second turn should auto-chain to first interaction."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")
        session.send("Hello")
        session.send("Follow up")

        api = client._client.interactions
        assert api._create_calls[1]["previous_interaction_id"] == "int-1"

    def test_three_turn_chain(self):
        """Three turns should form a chain: None → int-1 → int-2."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client)
        session.send("Turn 1")
        session.send("Turn 2")
        session.send("Turn 3")

        api = client._client.interactions
        assert api._create_calls[0].get("previous_interaction_id") is None
        assert api._create_calls[1]["previous_interaction_id"] == "int-1"
        assert api._create_calls[2]["previous_interaction_id"] == "int-2"

    def test_history_ids(self):
        """Session tracks all interaction IDs."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client)
        session.send("A")
        session.send("B")
        assert session.history_ids == ["int-1", "int-2"]
        assert session.turn_count == 2

    def test_mixed_interactions_model_switch(self):
        """Model can be switched mid-conversation for mixed interactions."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")
        session.send("Research this topic")
        session.send("Summarize in JSON", model="gemini-2.5-pro")

        api = client._client.interactions
        assert api._create_calls[0]["model"] == "gemini-3-flash-preview"
        assert api._create_calls[1]["model"] == "gemini-2.5-pro"
        # Chain is still maintained
        assert api._create_calls[1]["previous_interaction_id"] == "int-1"

    def test_fork_creates_independent_branch(self):
        """Forked session starts from same position but diverges."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")
        session.send("Setup context")

        branch = session.fork(model="gemini-3-pro-preview")
        branch.send("Explore alternative")

        # Branch has parent history + its own turn
        assert branch.history_ids == ["int-1", "int-2"]
        # Parent is unaffected
        assert session.history_ids == ["int-1"]

    def test_fork_preserves_chain_point(self):
        """Fork chains from the same previous_interaction_id as parent."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client)
        session.send("Base")

        branch = session.fork()
        branch.send("Branch turn")

        api = client._client.interactions
        # Branch's first call should chain from int-1 (same as parent's last)
        assert api._create_calls[1]["previous_interaction_id"] == "int-1"

    def test_reset_clears_history(self):
        """Reset removes all interaction history."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client)
        session.send("A")
        session.send("B")
        assert session.turn_count == 2

        session.reset()
        assert session.turn_count == 0
        assert session.last_interaction_id is None
        assert session.history_ids == []

    def test_reset_then_send_no_chain(self):
        """After reset, next send should not have previous_interaction_id."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client)
        session.send("Old context")
        session.reset()
        session.send("Fresh start")

        api = client._client.interactions
        assert api._create_calls[1].get("previous_interaction_id") is None

    def test_store_always_true_for_chaining(self):
        """Session always sets store=True for cache + chaining support."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client)
        session.send("Cache me")

        api = client._client.interactions
        assert api._create_calls[0]["store"] is True

    def test_system_instruction_propagation(self):
        """Default system instruction is passed to all turns."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client, system_instruction="You are a helpful assistant.")
        session.send("Question")

        api = client._client.interactions
        assert api._create_calls[0]["system_instruction"] == "You are a helpful assistant."

    def test_system_instruction_override(self):
        """Per-turn system_instruction overrides session default."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client, system_instruction="Default instruction")
        session.send("Q", system_instruction="Override instruction")

        api = client._client.interactions
        assert api._create_calls[0]["system_instruction"] == "Override instruction"

    def test_empty_session_properties(self):
        """Fresh session has no history."""
        from gemini_interactions.session import ConversationSession

        client = _make_mock_client()
        session = ConversationSession(client)
        assert session.last_interaction_id is None
        assert session.history_ids == []
        assert session.turn_count == 0


# ---------------------------------------------------------------------------
# Client — list() method
# ---------------------------------------------------------------------------


class TestListInteractions:
    def test_list_empty(self):
        client = _make_mock_client()
        results = client.list()
        assert results == []

    def test_list_passes_kwargs(self):
        """Verify page_size and filter are forwarded."""
        client = _make_mock_client()
        # The mock returns empty, but we verify it doesn't raise
        results = client.list(page_size=5, filter="model=gemini-3-flash-preview")
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# ConversationSession — stream_send() tests
# ---------------------------------------------------------------------------


def _make_stream_mock_client():
    """Create a client that mocks both create() and stream() at the InteractionsClient level."""

    client = InteractionsClient.__new__(InteractionsClient)
    client._api_key = "test-key"
    client._default_model = "gemini-3-flash-preview"
    client._telemetry = NullTelemetry()

    # Mock the underlying SDK client
    mock_api = _MockInteractionsAPI()
    client._client = type("MockGenAI", (), {"interactions": mock_api})()

    # Patch stream() to yield controlled StreamEvents
    _stream_call_count = {"n": 0}
    _stream_calls: list[dict] = []

    def mock_stream(*, input, model=None, previous_interaction_id=None, **kwargs):
        _stream_call_count["n"] += 1
        n = _stream_call_count["n"]
        _stream_calls.append(
            {
                "input": input,
                "model": model,
                "previous_interaction_id": previous_interaction_id,
            }
        )
        yield StreamEvent(
            event_type=EventType.INTERACTION_START,
            interaction_id=f"stream-{n}",
        )
        yield StreamEvent(
            event_type=EventType.CONTENT_START,
            index=0,
            content_type="text",
        )
        yield StreamEvent(
            event_type=EventType.CONTENT_DELTA,
            index=0,
            delta_type="text",
            text=f"Streamed response {n}",
        )
        yield StreamEvent(
            event_type=EventType.CONTENT_STOP,
            index=0,
        )
        yield StreamEvent(
            event_type=EventType.INTERACTION_COMPLETE,
            interaction_id=f"stream-{n}",
            usage={"total_tokens": 42, "prompt_tokens": 10, "completion_tokens": 32},
        )

    client.stream = mock_stream
    client._stream_calls = _stream_calls
    return client


class TestConversationSessionStreamSend:
    def test_stream_send_captures_interaction_id(self):
        """stream_send captures the interaction_id from the start event."""
        from gemini_interactions.session import ConversationSession

        client = _make_stream_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")
        list(session.stream_send("Hello streaming"))

        assert session.last_interaction_id == "stream-1"
        assert session.turn_count == 1

    def test_stream_send_chains_to_previous(self):
        """Second stream_send passes previous_interaction_id from first turn."""
        from gemini_interactions.session import ConversationSession

        client = _make_stream_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")
        list(session.stream_send("Turn 1"))
        list(session.stream_send("Turn 2"))

        assert client._stream_calls[0]["previous_interaction_id"] is None
        assert client._stream_calls[1]["previous_interaction_id"] == "stream-1"
        assert session.history_ids == ["stream-1", "stream-2"]

    def test_stream_send_yields_all_events(self):
        """All events from the stream are yielded to the caller."""
        from gemini_interactions.session import ConversationSession

        client = _make_stream_mock_client()
        session = ConversationSession(client)
        events = list(session.stream_send("Test"))

        event_types = [e.event_type for e in events]
        assert EventType.INTERACTION_START in event_types
        assert EventType.CONTENT_DELTA in event_types
        assert EventType.INTERACTION_COMPLETE in event_types

    def test_stream_send_mixed_with_send(self):
        """stream_send and send can be interleaved in the same session."""
        from gemini_interactions.session import ConversationSession

        client = _make_stream_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")

        # First turn: non-streaming
        session.send("Non-streaming turn")
        assert session.last_interaction_id == "int-1"

        # Second turn: streaming — should chain from int-1
        list(session.stream_send("Streaming turn"))
        assert client._stream_calls[0]["previous_interaction_id"] == "int-1"
        assert session.history_ids == ["int-1", "stream-1"]


# ---------------------------------------------------------------------------
# ConversationSession — function_call_loop() tests
# ---------------------------------------------------------------------------


def _make_fc_mock_client():
    """Create a client that mocks function call loop scenarios."""
    call_log: list[dict] = []
    call_count = {"n": 0}

    @dataclass
    class _MockFCOutput:
        type: str = "function_call"
        name: str = "get_weather"
        id: str = "fc-1"
        arguments: dict = None

        def __post_init__(self):
            self.arguments = self.arguments or {"city": "NYC"}

    @dataclass
    class _MockTextOutput:
        type: str = "text"
        text: str = "The weather in NYC is sunny."

    class _MockFCAPI:
        def create(self, **kwargs):
            call_count["n"] += 1
            n = call_count["n"]
            call_log.append(kwargs)

            @dataclass
            class _Result:
                id: str = f"fc-int-{n}"
                status: str = "completed"
                outputs: list = None
                usage: Any = None

                def __post_init__(self):
                    # First call returns function_call, subsequent return text
                    if n == 1:
                        self.outputs = [_MockFCOutput()]
                    else:
                        self.outputs = [_MockTextOutput()]

            return _Result()

    client = InteractionsClient.__new__(InteractionsClient)
    client._api_key = "test-key"
    client._default_model = "gemini-3-flash-preview"
    client._telemetry = NullTelemetry()
    client._client = type("MockGenAI", (), {"interactions": _MockFCAPI()})()
    client._fc_call_log = call_log
    return client


class TestConversationSessionFunctionCallLoop:
    def test_function_call_loop_auto_chains(self):
        """Session function_call_loop injects previous_interaction_id."""
        from gemini_interactions.session import ConversationSession

        client = _make_fc_mock_client()
        session = ConversationSession(client, model="gemini-3-flash-preview")

        # Seed with a regular turn first
        session._interaction_ids.append("seed-id")

        session.function_call_loop(
            input="What's the weather?",
            tools=[{"type": "function", "name": "get_weather"}],
            tool_handlers={"get_weather": lambda city: f"Sunny in {city}"},
        )

        # First create call should chain from seed-id
        assert client._fc_call_log[0]["previous_interaction_id"] == "seed-id"

    def test_function_call_loop_executes_handler(self):
        """Handlers are called with the function arguments."""
        from gemini_interactions.session import ConversationSession

        handler_calls = []

        def weather_handler(city):
            handler_calls.append(city)
            return f"72°F in {city}"

        client = _make_fc_mock_client()
        session = ConversationSession(client)
        session.function_call_loop(
            input="Weather check",
            tools=[{"type": "function", "name": "get_weather"}],
            tool_handlers={"get_weather": weather_handler},
        )

        assert handler_calls == ["NYC"]

    def test_function_call_loop_tracks_all_ids(self):
        """All interaction IDs from the loop are tracked in session history."""
        from gemini_interactions.session import ConversationSession

        client = _make_fc_mock_client()
        session = ConversationSession(client)
        session.function_call_loop(
            input="Test",
            tools=[{"type": "function", "name": "get_weather"}],
            tool_handlers={"get_weather": lambda city: "warm"},
        )

        # Should have 2 IDs: initial call + function result submission
        assert len(session.history_ids) == 2
        assert session.history_ids == ["fc-int-1", "fc-int-2"]

    def test_function_call_loop_no_function_calls(self):
        """Early return when response has no function calls."""
        from gemini_interactions.session import ConversationSession

        @dataclass
        class _MockTextOnly:
            type: str = "text"
            text: str = "Direct answer"

        class _MockNoFCAPI:
            def create(self, **kwargs):
                @dataclass
                class _R:
                    id: str = "no-fc-1"
                    status: str = "completed"
                    outputs: list = None
                    usage: Any = None

                    def __post_init__(self):
                        self.outputs = [_MockTextOnly()]

                return _R()

        client = InteractionsClient.__new__(InteractionsClient)
        client._api_key = "test-key"
        client._default_model = "gemini-3-flash-preview"
        client._telemetry = NullTelemetry()
        client._client = type("M", (), {"interactions": _MockNoFCAPI()})()

        session = ConversationSession(client)
        result = session.function_call_loop(
            input="No tools needed",
            tools=[],
            tool_handlers={},
        )

        assert session.turn_count == 1
        assert result.text == "Direct answer"

    def test_function_call_loop_handler_error(self):
        """Errored handlers produce error strings, don't crash the loop."""
        from gemini_interactions.session import ConversationSession

        def failing_handler(**kwargs):
            msg = "API down"
            raise ConnectionError(msg)

        client = _make_fc_mock_client()
        session = ConversationSession(client)
        session.function_call_loop(
            input="Test error handling",
            tools=[{"type": "function", "name": "get_weather"}],
            tool_handlers={"get_weather": failing_handler},
        )

        # Should complete without raising — error is serialized as result
        assert session.turn_count == 2

    def test_function_call_loop_missing_handler(self):
        """Missing handler produces a descriptive error string."""
        from gemini_interactions.session import ConversationSession

        client = _make_fc_mock_client()
        session = ConversationSession(client)
        session.function_call_loop(
            input="Test missing handler",
            tools=[{"type": "function", "name": "get_weather"}],
            tool_handlers={},  # No handler registered
        )

        # Second call's input should contain the error message
        second_call_input = client._fc_call_log[1]["input"]
        assert any("No handler" in str(item.get("result", "")) for item in second_call_input)
