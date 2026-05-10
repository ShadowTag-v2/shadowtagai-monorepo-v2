# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""MCP Tool Wrappers for Gemini Interactions API.

Exposes the Gemini Interactions API (stateful, multi-turn conversations)
as callable tool wrappers that the sequential-thinking MCP server can
invoke for live pair-programming between Antigravity and Gemini.

Reference: https://ai.google.dev/gemini-api/docs/interactions

Architecture:
    sequential-thinking → InteractionsTool.send_turn() → Gemini API
                       ← structured response ←

Each session maintains server-managed conversation state, enabling:
  - Multi-turn reasoning chains without manual context replay
  - Tool-use within the Gemini session (grounding, code execution)
  - Resumable sessions via session token persistence
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class InteractionsModel(StrEnum):
  """Supported Gemini models for Interactions API."""

  FLASH = "gemini-3.1-flash-lite-preview-thinking"
  PRO = "gemini-3.1-pro"
  FLASH_LITE = "gemini-3.1-flash-lite"


class SessionState(StrEnum):
  """Lifecycle state of an interactions session."""

  CREATED = "created"
  ACTIVE = "active"
  PAUSED = "paused"
  CLOSED = "closed"
  ERROR = "error"


@dataclass
class InteractionsSession:
  """Tracks a single Gemini Interactions session.

  Attributes:
      session_id: Server-assigned session identifier.
      model: The Gemini model powering this session.
      state: Current lifecycle state.
      turn_count: Number of completed turns.
      token_usage: Cumulative token usage.
      created_at: Unix timestamp of session creation.
      last_activity: Unix timestamp of last turn.
  """

  session_id: str = ""
  model: InteractionsModel = InteractionsModel.FLASH
  state: SessionState = SessionState.CREATED
  turn_count: int = 0
  token_usage: dict[str, int] = field(default_factory=lambda: {"input": 0, "output": 0})
  created_at: float = 0.0
  last_activity: float = 0.0
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TurnResult:
  """Result of a single interaction turn.

  Attributes:
      text: The model's text response.
      tool_calls: Any tool calls the model wants to execute.
      grounding_sources: Sources used for grounding.
      tokens_used: Token count for this turn.
      latency_ms: Round-trip latency in milliseconds.
      finish_reason: Why the model stopped generating.
  """

  text: str = ""
  tool_calls: list[dict[str, Any]] = field(default_factory=list)
  grounding_sources: list[str] = field(default_factory=list)
  tokens_used: dict[str, int] = field(default_factory=lambda: {"input": 0, "output": 0})
  latency_ms: float = 0.0
  finish_reason: str = ""


class InteractionsTool:
  """MCP-compatible wrapper for Gemini Interactions API.

  Designed to be registered as a tool provider for the
  sequential-thinking MCP server, enabling multi-turn
  Gemini conversations within agentic reasoning chains.

  Usage::

      tool = InteractionsTool(api_key="...")
      session = tool.create_session(model=InteractionsModel.FLASH)
      result = tool.send_turn(session.session_id, "Analyze this code...")
      tool.close_session(session.session_id)
  """

  def __init__(
    self,
    api_key: str | None = None,
    *,
    base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    session_dir: Path | None = None,
    max_turns: int = 100,
  ) -> None:
    self._api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    self._base_url = base_url.rstrip("/")
    self._sessions: dict[str, InteractionsSession] = {}
    self._session_dir = session_dir or Path(".beads/interactions")
    self._max_turns = max_turns
    self._next_id = 0

    if not self._api_key:
      logger.warning(
        "InteractionsTool: No GEMINI_API_KEY set. "
        "Fetch via: gcloud secrets versions access latest "
        "--secret=gemini-api-key --project=shadowtag-omega-v4"
      )

  # ----- Session Lifecycle -----

  def create_session(
    self,
    model: InteractionsModel = InteractionsModel.FLASH,
    *,
    system_instruction: str = "",
    tools: list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
  ) -> InteractionsSession:
    """Create a new Interactions session.

    Args:
        model: The Gemini model to use.
        system_instruction: Optional system-level instruction.
        tools: Optional tool declarations for the model.
        metadata: Arbitrary metadata to attach to the session.

    Returns:
        A new InteractionsSession with server-assigned ID.
    """
    if not self._api_key:
      msg = "Cannot create session: GEMINI_API_KEY not configured"
      raise ValueError(msg)

    # Build request payload per Interactions API spec
    payload: dict[str, Any] = {"model": f"models/{model.value}"}

    if system_instruction:
      payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    if tools:
      payload["tools"] = tools

    # In production, this calls the Gemini API.
    # For local dev without connectivity, we create a stub session.
    session_id = f"interactions-{int(time.time() * 1000)}-{os.getpid()}-{self._next_id}"
    self._next_id += 1

    session = InteractionsSession(
      session_id=session_id,
      model=model,
      state=SessionState.ACTIVE,
      created_at=time.time(),
      last_activity=time.time(),
      metadata=metadata or {},
    )

    self._sessions[session_id] = session
    self._persist_session(session)

    logger.info("Created Interactions session %s (model=%s)", session_id, model)
    return session

  def send_turn(
    self,
    session_id: str,
    message: str,
    *,
    tool_results: list[dict[str, Any]] | None = None,
  ) -> TurnResult:
    """Send a turn to an active session.

    Args:
        session_id: The session to send to.
        message: The user's message text.
        tool_results: Results from tool calls the model requested.

    Returns:
        TurnResult with the model's response.

    Raises:
        ValueError: If session not found or not active.
    """
    session = self._sessions.get(session_id)
    if not session:
      msg = f"Session {session_id} not found"
      raise ValueError(msg)

    if session.state != SessionState.ACTIVE:
      msg = f"Session {session_id} is {session.state}, not active"
      raise ValueError(msg)

    if session.turn_count >= self._max_turns:
      msg = f"Session {session_id} exceeded max turns ({self._max_turns})"
      raise ValueError(msg)

    t0 = time.perf_counter_ns()

    # Build request
    contents = [{"parts": [{"text": message}], "role": "user"}]

    if tool_results:
      for tr in tool_results:
        contents.append(
          {
            "parts": [
              {
                "functionResponse": {
                  "name": tr.get("name", ""),
                  "response": tr.get("response", {}),
                }
              }
            ],
            "role": "function",
          }
        )

    # API call stub — replace with httpx in production
    response_text = self._call_api(session, contents)
    latency_ms = (time.perf_counter_ns() - t0) / 1_000_000

    # Update session state
    session.turn_count += 1
    session.last_activity = time.time()
    self._persist_session(session)

    result = TurnResult(
      text=response_text,
      latency_ms=round(latency_ms, 2),
      finish_reason="STOP",
    )

    logger.debug(
      "Turn %d on %s: %.1fms, %d chars response",
      session.turn_count,
      session_id,
      latency_ms,
      len(response_text),
    )

    return result

  def resume_session(self, session_id: str) -> InteractionsSession | None:
    """Resume a persisted session from disk.

    Args:
        session_id: The session ID to resume.

    Returns:
        The restored session, or None if not found.
    """
    if session_id in self._sessions:
      return self._sessions[session_id]

    session_file = self._session_dir / f"{session_id}.json"
    if not session_file.exists():
      return None

    try:
      data = json.loads(session_file.read_text())
      session = InteractionsSession(
        session_id=data["session_id"],
        model=InteractionsModel(data["model"]),
        state=SessionState(data["state"]),
        turn_count=data.get("turn_count", 0),
        token_usage=data.get("token_usage", {"input": 0, "output": 0}),
        created_at=data.get("created_at", 0.0),
        last_activity=data.get("last_activity", 0.0),
        metadata=data.get("metadata", {}),
      )
      session.state = SessionState.ACTIVE
      self._sessions[session_id] = session
      logger.info("Resumed session %s (turn %d)", session_id, session.turn_count)
      return session
    except (json.JSONDecodeError, KeyError) as e:
      logger.warning("Failed to resume session %s: %s", session_id, e)
      return None

  def close_session(self, session_id: str) -> bool:
    """Close an active session and persist final state.

    Args:
        session_id: The session to close.

    Returns:
        True if session was found and closed.
    """
    session = self._sessions.get(session_id)
    if not session:
      return False

    session.state = SessionState.CLOSED
    self._persist_session(session)
    del self._sessions[session_id]

    logger.info(
      "Closed session %s after %d turns",
      session_id,
      session.turn_count,
    )
    return True

  def list_sessions(self) -> list[InteractionsSession]:
    """Return all tracked sessions."""
    return list(self._sessions.values())

  # ----- Internal -----

  def _call_api(
    self,
    session: InteractionsSession,
    contents: list[dict[str, Any]],
  ) -> str:
    """Call the Gemini Interactions API.

    In production, this uses httpx to POST to:
        {base_url}/models/{model}:generateContent?key={api_key}

    For now returns a stub response — swap with real HTTP call
    when GEMINI_API_KEY is live-verified.
    """
    # Production path (uncomment when API is live):
    # import httpx
    # url = f"{self._base_url}/models/{session.model}:generateContent"
    # resp = httpx.post(url, json={"contents": contents},
    #                   params={"key": self._api_key}, timeout=120)
    # resp.raise_for_status()
    # return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    user_text = ""
    for content in contents:
      for part in content.get("parts", []):
        if "text" in part:
          user_text = part["text"]
          break

    return (
      f"[Interactions API stub] Received turn {session.turn_count + 1} "
      f"({len(user_text)} chars) on model {session.model}. "
      f"Replace _call_api with httpx POST to activate live inference."
    )

  def _persist_session(self, session: InteractionsSession) -> None:
    """Persist session state to disk for resumability."""
    self._session_dir.mkdir(parents=True, exist_ok=True)
    session_file = self._session_dir / f"{session.session_id}.json"

    data = {
      "session_id": session.session_id,
      "model": session.model.value,
      "state": session.state.value,
      "turn_count": session.turn_count,
      "token_usage": session.token_usage,
      "created_at": session.created_at,
      "last_activity": session.last_activity,
      "metadata": session.metadata,
    }

    session_file.write_text(json.dumps(data, indent=2))
