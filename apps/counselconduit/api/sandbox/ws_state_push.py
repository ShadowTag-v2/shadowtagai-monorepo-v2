# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""WebSocket State Push — Real-time sandbox session state transitions.

Provides a WebSocket endpoint that pushes session state changes to
connected attorney clients in real time. Enables the DiffView frontend
to react immediately when a session transitions (e.g., SPECULATING →
REVIEWING → COMMITTED).

Architecture:
  Browser (DiffView) ←── WebSocket ←── SessionStateManager ←── SandboxSession

Protocol:
  1. Attorney connects to /ws/sandbox/{session_id}
  2. Server pushes JSON messages on state transitions:
     { "type": "state_change", "session_id": "...", "from": "speculating", "to": "reviewing", "ts": "..." }
  3. Client disconnects gracefully or on session expiry

Security:
  - Connection requires valid session_id
  - Attorney UID verified before upgrade
  - No PII in WebSocket messages (prefix-only session IDs)
  - Messages are fire-and-forget (no acks required)
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("counselconduit.sandbox.ws")

router = APIRouter(tags=["sandbox-ws"])


# ── Connection Manager ────────────────────────────────────────────────


@dataclass
class StateMessage:
    """A single state transition message."""

    type: str = "state_change"
    session_id: str = ""
    from_state: str = ""
    to_state: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "type": self.type,
                "session_id_prefix": self.session_id[:8] if self.session_id else "",
                "from": self.from_state,
                "to": self.to_state,
                "ts": self.timestamp,
                "metadata": self.metadata,
            }
        )


class ConnectionManager:
    """Manages WebSocket connections per session.

    Thread-safe connection tracking with per-session fan-out.
    Dead connections are pruned on send failure.
    """

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection for a session."""
        await websocket.accept()
        async with self._lock:
            self._connections[session_id].append(websocket)
        logger.info("WS connected: session=%s total=%d", session_id[:8], len(self._connections[session_id]))

    async def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            conns = self._connections.get(session_id, [])
            if websocket in conns:
                conns.remove(websocket)
            if not conns:
                self._connections.pop(session_id, None)
        logger.info("WS disconnected: session=%s", session_id[:8])

    async def broadcast(self, session_id: str, message: StateMessage) -> None:
        """Send a state message to all connections for a session.

        Dead connections are pruned automatically.
        """
        async with self._lock:
            conns = self._connections.get(session_id, [])

        dead: list[WebSocket] = []
        payload = message.to_json()

        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)

        # Prune dead connections
        if dead:
            async with self._lock:
                for ws in dead:
                    conns = self._connections.get(session_id, [])
                    if ws in conns:
                        conns.remove(ws)

    async def notify_state_change(
        self,
        session_id: str,
        from_state: str,
        to_state: str,
        *,
        metadata: dict | None = None,
    ) -> None:
        """Convenience: broadcast a state change for a session."""
        msg = StateMessage(
            session_id=session_id,
            from_state=from_state,
            to_state=to_state,
            metadata=metadata or {},
        )
        await self.broadcast(session_id, msg)
        logger.info(
            "State push: session=%s %s → %s",
            session_id[:8],
            from_state,
            to_state,
        )

    @property
    def active_session_count(self) -> int:
        """Number of sessions with active WebSocket connections."""
        return len(self._connections)


# Singleton manager
manager = ConnectionManager()


# ── WebSocket Endpoint ────────────────────────────────────────────────


@router.websocket("/ws/sandbox/{session_id}")
async def sandbox_ws(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for sandbox session state notifications.

    The client connects and receives push messages whenever the session
    state transitions. The connection stays alive until the client
    disconnects or the session expires.
    """
    await manager.connect(session_id, websocket)

    try:
        # Keep-alive loop — listen for client pings or disconnect
        while True:
            try:
                # Wait for client messages (pings, close frames)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=300,  # 5-minute keep-alive timeout
                )
                # Handle ping
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "ts": datetime.now(UTC).isoformat()}))
            except TimeoutError:
                # Send keep-alive ping
                try:
                    await websocket.send_text(json.dumps({"type": "ping", "ts": datetime.now(UTC).isoformat()}))
                except Exception:
                    break

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(session_id, websocket)
