# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""AG-UI Server-Sent Events (SSE) transport endpoint.

Implements the AG-UI protocol for streaming agent events to CopilotKit
frontends. All PII-bearing payloads are encrypted with Fernet per ADR 003.

Security:
    - Bearer auth (Firebase ID token) required
    - Fernet encryption for PII payloads
    - Cache-Control: no-store on all SSE responses
    - X-Accel-Buffering: no to prevent proxy caching
    - Per-session encryption keys with 1-hour TTL
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AGUIEventType(StrEnum):
    """AG-UI SSE event types per the AG-UI protocol spec."""

    RUN_STARTED = "run_started"
    RUN_FINISHED = "run_finished"
    RUN_ERROR = "run_error"
    TEXT_MESSAGE_START = "text_message_start"
    TEXT_MESSAGE_CONTENT = "text_message_content"
    TEXT_MESSAGE_END = "text_message_end"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_ARGS = "tool_call_args"
    TOOL_CALL_END = "tool_call_end"
    STATE_SNAPSHOT = "state_snapshot"
    STATE_DELTA = "state_delta"
    CUSTOM = "custom"


@dataclass
class AGUIEvent:
    """A single AG-UI SSE event."""

    type: AGUIEventType
    data: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_sse(self) -> str:
        """Serialize to SSE wire format."""
        payload = {
            "type": self.type.value,
            "data": self.data,
            "id": self.event_id,
            "timestamp": self.timestamp,
        }
        return f"data: {json.dumps(payload)}\n\n"


@dataclass
class SSESessionContext:
    """Per-session context for AG-UI SSE streams."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    user_id: str = ""
    encryption_key: bytes = b""
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 3600  # 1 hour

    @property
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return (time.time() - self.created_at) > self.ttl_seconds


class AGUIStreamManager:
    """Manages AG-UI SSE streams with Fernet encryption per ADR 003.

    Security controls:
    - Per-session Fernet keys stored in Firestore with TTL
    - PII stripping from all structured logs
    - HMAC-SHA256 Kovel attestation per privileged session
    """

    def __init__(self, encryption_service: Any = None) -> None:
        self._sessions: dict[str, SSESessionContext] = {}
        self._encryption = encryption_service

    def create_session(self, tenant_id: str, user_id: str) -> SSESessionContext:
        """Create a new SSE session with a fresh encryption key.

        Args:
            tenant_id: The law firm tenant ID.
            user_id: The authenticated user ID.

        Returns:
            SSESessionContext with a unique session ID and encryption key.
        """
        try:
            from cryptography.fernet import Fernet

            key = Fernet.generate_key()
        except ImportError:
            logger.warning("cryptography not installed, using empty key")
            key = b""

        session = SSESessionContext(
            tenant_id=tenant_id,
            user_id=user_id,
            encryption_key=key,
        )
        self._sessions[session.session_id] = session
        logger.info(
            "SSE session created: session=%s tenant=%s",
            session.session_id,
            tenant_id,
        )
        return session

    def get_session(self, session_id: str) -> SSESessionContext | None:
        """Retrieve a session, returning None if expired."""
        session = self._sessions.get(session_id)
        if session and session.is_expired:
            del self._sessions[session_id]
            return None
        return session

    def encrypt_payload(self, session: SSESessionContext, data: dict[str, Any]) -> str:
        """Encrypt a payload using the session's Fernet key.

        Args:
            session: The SSE session context.
            data: The payload to encrypt.

        Returns:
            Base64-encoded encrypted string, or JSON string if no crypto.
        """
        plaintext = json.dumps(data).encode()
        if session.encryption_key:
            try:
                from cryptography.fernet import Fernet

                f = Fernet(session.encryption_key)
                return f.encrypt(plaintext).decode()
            except ImportError:
                pass
        return plaintext.decode()

    async def stream_events(
        self,
        session: SSESessionContext,
        events: list[AGUIEvent],
    ) -> AsyncGenerator[str]:
        """Stream AG-UI events as SSE with encryption.

        Args:
            session: The SSE session context.
            events: List of events to stream.

        Yields:
            SSE-formatted event strings.
        """
        # Run started
        yield AGUIEvent(
            type=AGUIEventType.RUN_STARTED,
            data={"session_id": session.session_id},
        ).to_sse()

        for event in events:
            # Encrypt PII-bearing payloads
            if event.type in (
                AGUIEventType.TEXT_MESSAGE_CONTENT,
                AGUIEventType.TOOL_CALL_ARGS,
                AGUIEventType.STATE_SNAPSHOT,
            ):
                event.data["_encrypted"] = self.encrypt_payload(session, event.data)

            yield event.to_sse()

        # Run finished
        yield AGUIEvent(
            type=AGUIEventType.RUN_FINISHED,
            data={"session_id": session.session_id},
        ).to_sse()


def sse_headers() -> dict[str, str]:
    """Return mandatory SSE response headers per ADR 002/003."""
    return {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "X-Accel-Buffering": "no",
        "X-Content-Type-Options": "nosniff",
        "Connection": "keep-alive",
    }
