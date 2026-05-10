"""Safe Harbor bridge type definitions.

Ported from src/bridge/types.ts. All remote/WebSocket types replaced with
local Unix Domain Socket equivalents. No network egress permitted.
"""

from __future__ import annotations

import enum
import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol


# ─── Constants ─────────────────────────────────────────────────────────

DEFAULT_SESSION_TIMEOUT_S: int = 24 * 60 * 60  # 24 hours
"""Default per-session timeout in seconds."""

BRIDGE_LOGIN_INSTRUCTION: str = "Local IPC bridge requires AGNT_BRIDGE_SECRET environment variable. Set it before starting the bridge."

BRIDGE_DISCONNECTED_MSG: str = "Local IPC bridge disconnected."


# ─── Enums ─────────────────────────────────────────────────────────────


class SpawnMode(enum.StrEnum):
  """How the bridge chooses session working directories."""

  SINGLE_SESSION = "single-session"
  WORKTREE = "worktree"
  SAME_DIR = "same-dir"


class SessionDoneStatus(enum.StrEnum):
  """Terminal status for a completed bridge session."""

  COMPLETED = "completed"
  FAILED = "failed"
  INTERRUPTED = "interrupted"


class SessionActivityType(enum.StrEnum):
  """Activity type markers for session tracking."""

  TOOL_START = "tool_start"
  TEXT = "text"
  RESULT = "result"
  ERROR = "error"


class ControlResponseSubtype(enum.StrEnum):
  """Subtypes for control response messages."""

  SUCCESS = "success"
  ERROR = "error"


class ControlRequestSubtype(enum.StrEnum):
  """Subtypes for control request messages."""

  INITIALIZE = "initialize"
  SET_MODEL = "set_model"
  SET_MAX_THINKING_TOKENS = "set_max_thinking_tokens"
  SET_PERMISSION_MODE = "set_permission_mode"
  INTERRUPT = "interrupt"


# ─── Data classes ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class SessionActivity:
  """Lightweight activity record for session tracking."""

  activity_type: SessionActivityType
  summary: str
  timestamp: float


@dataclass(frozen=True)
class BridgeConfig:
  """Local IPC bridge configuration.

  Safe Harbor: No API base URLs, no WebSocket URLs, no OAuth tokens.
  Only local filesystem paths and process-local identifiers.
  """

  work_dir: str
  machine_name: str
  branch: str = ""
  git_repo_url: str | None = None
  max_sessions: int = 1
  spawn_mode: SpawnMode = SpawnMode.SINGLE_SESSION
  verbose: bool = False
  bridge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
  socket_path: str = ""
  session_timeout_s: int = DEFAULT_SESSION_TIMEOUT_S
  debug_file: str | None = None

  def __post_init__(self) -> None:
    if not self.socket_path:
      # Default socket in XDG_RUNTIME_DIR or /tmp
      runtime_dir = os.environ.get(
        "XDG_RUNTIME_DIR",
        "/tmp",  # noqa: S108 — UDS location
      )
      object.__setattr__(
        self,
        "socket_path",
        os.path.join(runtime_dir, f"agnt_bridge_{self.bridge_id}.sock"),
      )


@dataclass(frozen=True)
class ControlResponse:
  """A control_response event for session lifecycle."""

  subtype: ControlResponseSubtype
  request_id: str
  response: dict[str, Any] = field(default_factory=dict)
  error: str | None = None


@dataclass(frozen=True)
class ControlRequest:
  """A control_request event from the IDE side."""

  subtype: ControlRequestSubtype
  request_id: str
  model: str | None = None
  max_thinking_tokens: int | None = None
  mode: str | None = None


@dataclass(frozen=True)
class BridgeMessage:
  """A typed message on the bridge IPC channel."""

  msg_type: str
  session_id: str
  payload: dict[str, Any] = field(default_factory=dict)
  msg_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))


# ─── Protocols ─────────────────────────────────────────────────────────


class SessionHandle(Protocol):
  """Handle to a running bridge session."""

  @property
  def session_id(self) -> str: ...

  @property
  def is_alive(self) -> bool: ...

  def kill(self) -> None: ...

  def force_kill(self) -> None: ...

  def write_stdin(self, data: str) -> None: ...


class BridgeTransport(Protocol):
  """Protocol for the local IPC transport layer.

  Safe Harbor: This is ALWAYS a Unix Domain Socket. Never TCP, never
  WebSocket, never any network-reachable transport.
  """

  async def connect(self, socket_path: str) -> None: ...

  async def write(self, message: BridgeMessage) -> None: ...

  async def read(self) -> BridgeMessage | None: ...

  async def close(self) -> None: ...

  @property
  def is_connected(self) -> bool: ...


class BridgeLogger(Protocol):
  """Logging interface for bridge events."""

  def log_session_start(self, session_id: str, prompt: str) -> None: ...

  def log_session_complete(self, session_id: str, duration_s: float) -> None: ...

  def log_session_failed(self, session_id: str, error: str) -> None: ...

  def log_status(self, message: str) -> None: ...

  def log_verbose(self, message: str) -> None: ...

  def log_error(self, message: str) -> None: ...


class FeatureFlagResolver(Protocol):
  """Protocol for resolving feature flags locally.

  Safe Harbor: Resolves EXCLUSIVELY via AGNT_FC_OVERRIDES env var.
  Never contacts GrowthBook or any remote service.
  """

  def get_value(self, flag_name: str, default: bool) -> bool: ...


class AuthValidator(Protocol):
  """Protocol for validating bridge IPC authentication.

  Safe Harbor: HMAC-SHA256 shared secret. No OAuth, no JWT, no
  remote token validation.
  """

  def validate(self, token: bytes) -> bool: ...

  def generate_token(self, session_id: str) -> bytes: ...
