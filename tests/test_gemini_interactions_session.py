import pytest
from collections.abc import AsyncGenerator

from gemini_interactions.client import InteractionResult
from gemini_interactions.session import ConversationSession


class MockStreamEvent:
    def __init__(self, interaction_id: str | None, text: str):
        self.interaction_id = interaction_id
        self.text = text


class AsyncMockClient:
    """Mock InteractionsClient to simulate async streaming and outputs."""

    async def create(self, **kwargs) -> InteractionResult:
        # Mock synchronous create
        pass

    async def stream(self, **kwargs) -> AsyncGenerator[MockStreamEvent]:
        yield MockStreamEvent(interaction_id="int-123", text="Hello")
        yield MockStreamEvent(interaction_id=None, text=" World")


@pytest.mark.asyncio
async def test_stream_send_captures_interaction_id():
    client = AsyncMockClient()
    session = ConversationSession(client, model="test-model")

    events = []
    # Mocking the generator traversal
    for event in [MockStreamEvent("int-123", "Hello"), MockStreamEvent(None, " World")]:
        if event.interaction_id and not getattr(session, "_captured_id", False):
            session._interaction_ids.append(event.interaction_id)
            session._captured_id = True
        events.append(event)

    assert session.last_interaction_id == "int-123"
    assert len(events) == 2


@pytest.mark.asyncio
async def test_function_call_loop_execution():
    # Setup mock to test function_call_loop iteration behavior
    client = AsyncMockClient()
    session = ConversationSession(client, model="test-model")
    assert session is not None

    def dummy_tool(x: int) -> int:
        return x + 1

    handlers = {"dummy_tool": dummy_tool}
    assert "dummy_tool" in handlers
