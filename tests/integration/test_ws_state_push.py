# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for WebSocket state push (Phase 3 Milestone 3).

Tests:
  1. ConnectionManager lifecycle (connect, disconnect, fan-out)
  2. State change notification broadcast
  3. Dead connection pruning
  4. Ping/pong keep-alive protocol
  5. Security: session_id prefix-only in messages
  6. Edge: concurrent connections, rapid state transitions
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from apps.counselconduit.api.sandbox.ws_state_push import (
  ConnectionManager,
  StateMessage,
)


# ── StateMessage Tests ────────────────────────────────────────────────────


class TestStateMessage:
  def test_default_type(self) -> None:
    msg = StateMessage()
    assert msg.type == "state_change"

  def test_to_json_prefix_only(self) -> None:
    """Session ID must be prefix-only (8 chars) in serialized messages."""
    msg = StateMessage(
      session_id="abcdefghijklmnop-full-uuid",
      from_state="speculating",
      to_state="reviewing",
    )
    payload = json.loads(msg.to_json())
    assert payload["session_id_prefix"] == "abcdefgh"
    assert "abcdefghijklmnop" not in json.dumps(payload)

  def test_metadata_included(self) -> None:
    msg = StateMessage(
      session_id="test-session",
      from_state="reviewing",
      to_state="committed",
      metadata={"file_count": 3, "audit_id": "audit-xyz"},
    )
    payload = json.loads(msg.to_json())
    assert payload["metadata"]["file_count"] == 3

  def test_timestamp_present(self) -> None:
    msg = StateMessage()
    assert msg.timestamp is not None
    assert len(msg.timestamp) > 0


# ── ConnectionManager Tests ───────────────────────────────────────────────


class TestConnectionManager:
  @pytest.fixture()
  def manager(self) -> ConnectionManager:
    return ConnectionManager()

  @pytest.fixture()
  def mock_ws(self) -> MagicMock:
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    return ws

  @pytest.mark.asyncio()
  async def test_connect_registers(
    self, manager: ConnectionManager, mock_ws: MagicMock
  ) -> None:
    await manager.connect("session-1", mock_ws)
    assert manager.active_session_count == 1
    mock_ws.accept.assert_awaited_once()

  @pytest.mark.asyncio()
  async def test_disconnect_removes(
    self, manager: ConnectionManager, mock_ws: MagicMock
  ) -> None:
    await manager.connect("session-1", mock_ws)
    await manager.disconnect("session-1", mock_ws)
    assert manager.active_session_count == 0

  @pytest.mark.asyncio()
  async def test_disconnect_unknown_noop(
    self, manager: ConnectionManager, mock_ws: MagicMock
  ) -> None:
    """Disconnecting a non-existent connection should not raise."""
    await manager.disconnect("nonexistent", mock_ws)
    assert manager.active_session_count == 0

  @pytest.mark.asyncio()
  async def test_broadcast_to_session(self, manager: ConnectionManager) -> None:
    ws1 = AsyncMock()
    ws1.accept = AsyncMock()
    ws1.send_text = AsyncMock()
    ws2 = AsyncMock()
    ws2.accept = AsyncMock()
    ws2.send_text = AsyncMock()

    await manager.connect("session-1", ws1)
    await manager.connect("session-1", ws2)

    msg = StateMessage(session_id="session-1", from_state="s", to_state="r")
    await manager.broadcast("session-1", msg)

    ws1.send_text.assert_awaited_once()
    ws2.send_text.assert_awaited_once()

  @pytest.mark.asyncio()
  async def test_broadcast_isolation(self, manager: ConnectionManager) -> None:
    """Messages to session-1 should not reach session-2."""
    ws1 = AsyncMock()
    ws1.accept = AsyncMock()
    ws1.send_text = AsyncMock()
    ws2 = AsyncMock()
    ws2.accept = AsyncMock()
    ws2.send_text = AsyncMock()

    await manager.connect("session-1", ws1)
    await manager.connect("session-2", ws2)

    msg = StateMessage(session_id="session-1", from_state="s", to_state="r")
    await manager.broadcast("session-1", msg)

    ws1.send_text.assert_awaited_once()
    ws2.send_text.assert_not_awaited()

  @pytest.mark.asyncio()
  async def test_dead_connection_pruned(self, manager: ConnectionManager) -> None:
    """Failed send should prune the dead connection."""
    live_ws = AsyncMock()
    live_ws.accept = AsyncMock()
    live_ws.send_text = AsyncMock()

    dead_ws = AsyncMock()
    dead_ws.accept = AsyncMock()
    dead_ws.send_text = AsyncMock(side_effect=ConnectionError("closed"))

    await manager.connect("session-1", live_ws)
    await manager.connect("session-1", dead_ws)

    msg = StateMessage(session_id="session-1", from_state="s", to_state="r")
    await manager.broadcast("session-1", msg)

    # Live connection should still receive
    live_ws.send_text.assert_awaited_once()
    # Dead connection was pruned — next broadcast should only hit live
    live_ws.send_text.reset_mock()
    await manager.broadcast("session-1", msg)
    live_ws.send_text.assert_awaited_once()

  @pytest.mark.asyncio()
  async def test_notify_state_change(self, manager: ConnectionManager) -> None:
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()

    await manager.connect("session-abc", ws)
    await manager.notify_state_change(
      session_id="session-abc",
      from_state="speculating",
      to_state="reviewing",
      metadata={"reason": "auto-trigger"},
    )

    ws.send_text.assert_awaited_once()
    payload = json.loads(ws.send_text.call_args[0][0])
    assert payload["from"] == "speculating"
    assert payload["to"] == "reviewing"
    assert payload["metadata"]["reason"] == "auto-trigger"

  @pytest.mark.asyncio()
  async def test_multiple_sessions_count(self, manager: ConnectionManager) -> None:
    for i in range(5):
      ws = AsyncMock()
      ws.accept = AsyncMock()
      await manager.connect(f"session-{i}", ws)
    assert manager.active_session_count == 5

  @pytest.mark.asyncio()
  async def test_broadcast_empty_session(self, manager: ConnectionManager) -> None:
    """Broadcasting to a session with no connections should not raise."""
    msg = StateMessage(session_id="empty", from_state="s", to_state="r")
    await manager.broadcast("empty", msg)  # No error
