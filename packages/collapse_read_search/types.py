"""Type definitions for the collapse-read-search message grouping engine.

Defines the data structures used by the collapsing algorithm to represent
renderable messages, tool invocations, and collapsed summary groups.

Ported from: Claude Code types/message.ts + utils/collapseReadSearch.ts types
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class MessageType(Enum):
    """Discriminator for the top-level message union."""

    ASSISTANT = auto()
    USER = auto()
    SYSTEM = auto()
    ATTACHMENT = auto()
    GROUPED_TOOL_USE = auto()


class ContentType(Enum):
    """Discriminator for message content blocks."""

    TEXT = auto()
    TOOL_USE = auto()
    TOOL_RESULT = auto()
    THINKING = auto()
    REDACTED_THINKING = auto()


class CommitKind(Enum):
    """How the commit was created (amend, merge, regular)."""

    REGULAR = "regular"
    AMEND = "amend"
    MERGE = "merge"


class BranchAction(Enum):
    """What happened to a branch."""

    CREATE = "create"
    DELETE = "delete"
    CHECKOUT = "checkout"


class PrAction(Enum):
    """What happened to a pull request."""

    CREATE = "create"
    UPDATE = "update"


@dataclass
class ContentBlock:
    """A single content block inside a message.

    This is intentionally loose — the collapse engine only inspects
    ``type``, ``name``, ``input``, ``id``, ``text``, and ``tool_use_id``.
    """

    type: ContentType
    name: str = ""
    input: Any = None
    id: str = ""
    text: str = ""
    tool_use_id: str = ""


@dataclass
class NormalizedMessage:
    """Flat representation of a single API-level message."""

    content: list[ContentBlock] = field(default_factory=list)


@dataclass
class AttachmentPayload:
    """Payload for attachment messages."""

    type: str = ""
    memories: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RenderableMessage:
    """Union type for all messages the renderer processes.

    The ``type`` field discriminates the variant.  Additional fields are
    populated depending on the variant:

    * ``assistant`` / ``user`` — ``message`` holds the :class:`NormalizedMessage`.
    * ``grouped_tool_use`` — ``tool_name`` + ``messages`` (list of sub-messages).
    * ``attachment`` — ``attachment`` holds the :class:`AttachmentPayload`.
    * ``system`` — ``subtype`` / ``hook_label`` / etc.
    """

    type: MessageType
    message: NormalizedMessage = field(default_factory=NormalizedMessage)
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = 0.0

    # --- grouped_tool_use fields ---
    tool_name: str = ""
    messages: list[RenderableMessage] = field(default_factory=list)
    display_message: RenderableMessage | None = None

    # --- attachment fields ---
    attachment: AttachmentPayload = field(default_factory=AttachmentPayload)

    # --- system fields ---
    subtype: str = ""
    hook_label: str = ""
    hook_count: int = 0
    total_duration_ms: float | None = None
    hook_infos: list[StopHookInfo] = field(default_factory=list)

    # --- tool_result extras ---
    tool_use_result: dict[str, Any] | None = None


@dataclass
class StopHookInfo:
    """Timing and label info for a PreToolUse stop hook."""

    name: str = ""
    duration_ms: float | None = None


@dataclass
class SearchOrReadResult:
    """Result of checking if a tool use is a search or read operation."""

    is_collapsible: bool = False
    is_search: bool = False
    is_read: bool = False
    is_list: bool = False
    is_repl: bool = False
    is_memory_write: bool = False
    is_absorbed_silently: bool = False
    mcp_server_name: str | None = None
    is_bash: bool | None = None


@dataclass
class CollapsedReadSearchGroup:
    """Summary object produced when consecutive search/read ops are collapsed.

    This replaces the run of individual messages in the output list and
    provides pre-computed counts for the summary renderer.
    """

    type: str = "collapsed_read_search"

    search_count: int = 0
    read_count: int = 0
    list_count: int = 0
    repl_count: int = 0

    memory_search_count: int = 0
    memory_read_count: int = 0
    memory_write_count: int = 0

    read_file_paths: list[str] = field(default_factory=list)
    search_args: list[str] = field(default_factory=list)
    latest_display_hint: str | None = None

    # The original messages that were collapsed into this group.
    group_messages: list[RenderableMessage] = field(default_factory=list)
    display_message: RenderableMessage | None = None
    group_uuid: str = ""
    timestamp: float = 0.0

    # Optional MCP counts
    mcp_call_count: int | None = None
    mcp_server_names: list[str] | None = None

    # Optional bash counts (fullscreen mode)
    bash_count: int | None = None
    git_op_bash_count: int | None = None
    commits: list[dict[str, Any]] | None = None
    pushes: list[dict[str, Any]] | None = None
    branches: list[dict[str, Any]] | None = None
    prs: list[dict[str, Any]] | None = None

    # Hook timing
    hook_total_ms: float = 0.0
    hook_count: int = 0
    hook_infos: list[StopHookInfo] = field(default_factory=list)

    # Absorbed memory attachments
    relevant_memories: list[dict[str, Any]] | None = None

    # Team memory (optional)
    team_memory_search_count: int | None = None
    team_memory_read_count: int | None = None
    team_memory_write_count: int | None = None
