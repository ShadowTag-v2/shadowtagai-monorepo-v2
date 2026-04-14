"""Context Engineering System (Google ADK Style)
=============================================

Implements the "Context Engineering" pattern from the whitepaper:
- Session: Container for a single conversation (Events + State).
- Memory: Distilled long-term knowledge (Declarative + Procedural).
- Context Manager: Orchestrates Fetch -> Prepare -> Invoke -> Upload cycle.

Key Components:
- Events: UserInput, AgentResponse, ToolCall, ToolOutput
- Compaction: Truncation, Summarization
- Memory Manager: Extraction, Consolidation, Retrieval
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal, cast

# --- Core Data Structures ---


@dataclass
class Event:
    """An atomic unit of interaction in a Session."""

    role: Literal["user", "model", "tool"]
    content: str | dict[str, Any]
    type: Literal["message", "tool_call", "tool_output"] = "message"
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SessionState:
    """Working memory / scratchpad for the current session."""

    data: dict[str, Any] = field(default_factory=dict)

    def update(self, key: str, value: Any):
        self.data[key] = value


class Session:
    """Manages the "Now" of a conversation.
    Acts as a chronological event log + working state.
    """

    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.events: list[Event] = []
        self.state = SessionState()
        self.start_time = datetime.now()

    def add_event(
        self, role: str, content: Any, type: str = "message", metadata: dict[str, Any] | None = None,
    ):
        # Cast strings to Literals for type safety
        safe_role = cast("Literal['user', 'model', 'tool']", role)
        safe_type = cast("Literal['message', 'tool_call', 'tool_output']", type)

        event = Event(role=safe_role, content=content, type=safe_type, metadata=metadata or {})
        self.events.append(event)

    def get_history(self) -> list[Event]:
        return self.events

    def get_last_n(self, n: int) -> list[Event]:
        return self.events[-n:] if n > 0 else []


# --- Memory System ---


@dataclass
class MemoryItem:
    """A distilled piece of long-term knowledge."""

    content: str  # The fact or wisdom
    type: Literal["declarative", "procedural"]  # Fact vs Skill
    scope: Literal["user", "session", "global"]  # Who/What it applies to
    confidence: float = 1.0
    source_session_id: str | None = None
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())


class MemoryManager:
    """Handles the lifecycle of Memory:
    Extraction -> Consolidation -> Storage -> Retrieval
    """

    def __init__(self):
        # In a real impl, this would connect to a Vector DB or Agent Engine
        self.memories: list[MemoryItem] = []

    def retrieve(self, query: str, limit: int = 5) -> list[MemoryItem]:
        """Retrieves relevant memories based on semantic similarity (Simulated).
        """
        # TODO: Implement actual vector search
        _ = query
        return sorted(self.memories, key=lambda x: x.created_at, reverse=True)[:limit]

    def add_memory(self, content: str, type: str = "declarative", scope: str = "user"):
        safe_type = cast("Literal['declarative', 'procedural']", type)
        safe_scope = cast("Literal['user', 'session', 'global']", scope)
        self.memories.append(MemoryItem(content, safe_type, safe_scope))

    def consolidate(self):
        """Merges duplicate/conflicting memories."""
        # To be implemented with LLM logic


# --- Context Compiler ---


class ContextCompaction:
    """Strategies to manage context window limits."""

    @staticmethod
    def truncate(events: list[Event], max_turns: int) -> list[Event]:
        return events[-max_turns:] if max_turns > 0 else events

    @staticmethod
    def summarize(events: list[Event], llm_client: Any) -> str:
        """Uses an LLM to summarize older events."""
        # Stub for recursive summarization
        _ = events
        _ = llm_client
        return "Summary of past convolution..."


class ContextCompiler:
    """Orchestrates the blocking 'Prepare' phase of the Context Cycle.
    Assembles System Instructions, Memory, and Session History into a Prompt.
    """

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    def compile(
        self, session: Session, query: str, system_instruction: str, max_turns: int = 20,
    ) -> str:
        """Fetches Memory -> Compacts Session -> Assembles Prompt.
        """
        # 1. Fetch Relevant Memory (Proactive Retrieval)
        # We query memory using the user's latest input
        relevant_memories = self.memory.retrieve(query)

        memory_block = "[LONG TERM MEMORY]\n"
        if relevant_memories:
            # Separate Declarative vs Procedural for better reasoning
            declarative = [m.content for m in relevant_memories if m.type == "declarative"]
            procedural = [m.content for m in relevant_memories if m.type == "procedural"]

            if declarative:
                memory_block += "Facts:\n" + "\n".join([f"- {m}" for m in declarative]) + "\n"
            if procedural:
                memory_block += (
                    "Playbook (How-To):\n" + "\n".join([f"- {m}" for m in procedural]) + "\n"
                )
        else:
            memory_block += "(No relevant memories found)\n"

        # 2. Compact Session (Sliding Window)
        recent_events = ContextCompaction.truncate(session.get_history(), max_turns)

        session_block = "[CURRENT SESSION]\n"
        for event in recent_events:
            timestamp_str = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
            role_marker = event.role.upper()
            if event.type == "tool_call":
                role_marker = "TOOL_CALL"
            elif event.type == "tool_output":
                role_marker = "TOOL_RESULT"

            session_block += f"[{timestamp_str}] {role_marker}: {event.content}\n"

        # 3. Assemble Final Prompt
        # Structure: System -> Memory -> Session -> Output Invite
        final_prompt = f"""
{system_instruction}

---
{memory_block}
---
{session_block}
---
RESPOND TO THE LATEST USER INPUT. USE TOOLS IF REQUIRED.
"""
        return final_prompt
