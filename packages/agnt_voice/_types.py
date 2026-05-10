"""Shared type definitions for agnt_voice.

Ported from src/services/voiceStreamSTT.ts type declarations.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Protocol
from collections.abc import Callable


# ─── Feature Gate Types ───────────────────────────────────────────────


class TokenProvider(Protocol):
  """Protocol for fetching an OAuth access token.

  Implementations must return the current access token string,
  or None if no valid token is available.
  """

  def __call__(self) -> str | None: ...


class AuthChecker(Protocol):
  """Protocol for checking if Anthropic auth is enabled."""

  def __call__(self) -> bool: ...


class FeatureFlagProvider(Protocol):
  """Protocol for GrowthBook-style feature flag evaluation.

  Returns the value of the named flag, falling back to the default
  if the flag is missing or stale.
  """

  def __call__(self, flag_name: str, default: bool) -> bool: ...


# ─── Recording Types ─────────────────────────────────────────────────


@dataclass(frozen=True)
class RecordingAvailability:
  """Result of probing whether audio recording is possible."""

  available: bool
  reason: str | None = None


@dataclass(frozen=True)
class VoiceDependencyCheck:
  """Result of checking voice recording dependencies."""

  available: bool
  missing: list[str] = field(default_factory=list)
  install_command: str | None = None


@dataclass(frozen=True)
class PackageManagerInfo:
  """Package manager detection result for SoX installation hints."""

  cmd: str
  args: list[str]
  display_command: str


# ─── STT Types ────────────────────────────────────────────────────────


class FinalizeSource(enum.StrEnum):
  """How finalize() resolved — diagnostic enum for debugging."""

  POST_CLOSESTREAM_ENDPOINT = "post_closestream_endpoint"
  NO_DATA_TIMEOUT = "no_data_timeout"
  SAFETY_TIMEOUT = "safety_timeout"
  WS_CLOSE = "ws_close"
  WS_ALREADY_CLOSED = "ws_already_closed"


@dataclass
class VoiceStreamCallbacks:
  """Callback bundle for the voice stream STT client."""

  on_transcript: Callable[[str, bool], None]
  """Called with (text, is_final) for each transcript segment."""

  on_error: Callable[[str, bool], None]
  """Called with (message, is_fatal) on errors."""

  on_close: Callable[[], None]
  """Called when the WebSocket connection closes."""

  on_ready: Callable[[VoiceStreamConnection], None]
  """Called when the connection is ready to accept audio."""


class VoiceStreamConnection(Protocol):
  """Protocol for a live voice stream connection."""

  def send(self, audio_chunk: bytes) -> None: ...
  async def finalize(self) -> FinalizeSource: ...
  def close(self) -> None: ...
  def is_connected(self) -> bool: ...
