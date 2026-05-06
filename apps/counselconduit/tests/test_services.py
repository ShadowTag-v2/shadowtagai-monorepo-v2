# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""Unit tests for AG-UI SSE stream, Kovel attestation, LiteLLM proxy,
and Cloud Tasks handler.

Covers items 9, 10, 14, 16, 19 from the execution checklist.
"""

from __future__ import annotations

import json

import pytest

from apps.counselconduit.api.agui_stream import (
    AGUIEvent,
    AGUIEventType,
    AGUIStreamManager,
    SSESessionContext,
    sse_headers,
)
from apps.counselconduit.services.cloud_tasks_handler import (
    CloudTasksHandler,
    DeadManSwitch,
)
from apps.counselconduit.services.kovel_attestation import (
    KovelAttestationService,
)
from apps.counselconduit.services.litellm_proxy import (
    LiteLLMProxy,
    ModelProvider,
)


class TestAGUISSE:
    """Tests for AG-UI SSE transport."""

    def test_event_serialization(self) -> None:
        event = AGUIEvent(
            type=AGUIEventType.TEXT_MESSAGE_CONTENT,
            data={"text": "Hello, counsel."},
        )
        sse = event.to_sse()
        assert sse.startswith("data: ")
        assert sse.endswith("\n\n")
        payload = json.loads(sse.replace("data: ", "").strip())
        assert payload["type"] == "text_message_content"
        assert payload["data"]["text"] == "Hello, counsel."

    def test_sse_headers(self) -> None:
        headers = sse_headers()
        assert headers["Content-Type"] == "text/event-stream"
        assert "no-store" in headers["Cache-Control"]
        assert headers["X-Accel-Buffering"] == "no"

    def test_session_creation(self) -> None:
        manager = AGUIStreamManager()
        session = manager.create_session("firm-123", "user-456")
        assert session.tenant_id == "firm-123"
        assert session.user_id == "user-456"
        assert session.session_id

    def test_session_expiry(self) -> None:
        session = SSESessionContext(
            tenant_id="firm-123",
            user_id="user-456",
            created_at=0,  # epoch — definitely expired
            ttl_seconds=1,
        )
        assert session.is_expired is True

    @pytest.mark.asyncio
    async def test_stream_events(self) -> None:
        manager = AGUIStreamManager()
        session = manager.create_session("firm-123", "user-456")
        events = [
            AGUIEvent(
                type=AGUIEventType.TEXT_MESSAGE_CONTENT,
                data={"text": "Analysis complete."},
            ),
        ]
        collected = []
        async for chunk in manager.stream_events(session, events):
            collected.append(chunk)
        # Should have: run_started + 1 event + run_finished = 3
        assert len(collected) == 3


class TestKovelAttestation:
    """Tests for HMAC-SHA256 Kovel attestation."""

    def setup_method(self) -> None:
        self.service = KovelAttestationService(secret_key=b"test-signing-key")

    def test_create_attestation(self) -> None:
        att = self.service.create_attestation(
            session_id="sess-123",
            tenant_id="firm-456",
            user_id="user-789",
            transcript_content="Client discussed contract terms.",
        )
        assert att.session_id == "sess-123"
        assert att.tenant_id == "firm-456"
        assert att.content_hash
        assert att.hmac_signature
        assert att.privilege_basis.startswith("Kovel")

    def test_verify_valid_attestation(self) -> None:
        att = self.service.create_attestation(
            session_id="sess-123",
            tenant_id="firm-456",
            user_id="user-789",
            transcript_content="Privileged communication.",
        )
        assert self.service.verify_attestation(att) is True

    def test_verify_tampered_attestation(self) -> None:
        att = self.service.create_attestation(
            session_id="sess-123",
            tenant_id="firm-456",
            user_id="user-789",
            transcript_content="Original content.",
        )
        att.content_hash = "tampered_hash"
        assert self.service.verify_attestation(att) is False

    def test_content_hash_deterministic(self) -> None:
        h1 = self.service.generate_content_hash("same content")
        h2 = self.service.generate_content_hash("same content")
        assert h1 == h2

    def test_content_hash_different(self) -> None:
        h1 = self.service.generate_content_hash("content A")
        h2 = self.service.generate_content_hash("content B")
        assert h1 != h2


class TestLiteLLMProxy:
    """Tests for per-tenant sandboxed LiteLLM proxy."""

    def setup_method(self) -> None:
        self.proxy = LiteLLMProxy()

    def test_issue_token(self) -> None:
        token = self.proxy.issue_token("firm-123", "sess-456")
        assert token.tenant_id == "firm-123"
        assert token.session_id == "sess-456"
        assert token.provider == ModelProvider.GEMINI
        assert not token.is_expired
        assert not token.is_budget_exceeded

    def test_validate_valid_token(self) -> None:
        token = self.proxy.issue_token("firm-123", "sess-456")
        valid, reason = self.proxy.validate_token(token.token_id)
        assert valid is True

    def test_validate_nonexistent_token(self) -> None:
        valid, reason = self.proxy.validate_token("fake")
        assert valid is False
        assert "not found" in reason.lower()

    def test_revoke_token(self) -> None:
        token = self.proxy.issue_token("firm-123", "sess-456")
        assert self.proxy.revoke_token(token.token_id) is True
        valid, _ = self.proxy.validate_token(token.token_id)
        assert valid is False

    def test_record_usage(self) -> None:
        token = self.proxy.issue_token("firm-123", "sess-456", max_tokens=100)
        self.proxy.record_usage(token.token_id, 50)
        assert token.usage_tokens == 50
        assert not token.is_budget_exceeded
        self.proxy.record_usage(token.token_id, 50)
        assert token.is_budget_exceeded

    def test_model_map(self) -> None:
        assert "gemini" in self.proxy.get_model_id(ModelProvider.GEMINI)
        assert "claude" in self.proxy.get_model_id(ModelProvider.CLAUDE)


class TestCloudTasksHandler:
    """Tests for Cloud Tasks push notification handler."""

    def setup_method(self) -> None:
        self.handler = CloudTasksHandler()

    @pytest.mark.asyncio
    async def test_handle_valid_push(self) -> None:
        body = json.dumps(
            {
                "type": "task_completed",
                "task_id": "task-123",
                "tenant_id": "firm-456",
            }
        ).encode()
        result = await self.handler.handle_push(body)
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_handle_invalid_json(self) -> None:
        result = await self.handler.handle_push(b"not json")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_handle_session_expired(self) -> None:
        body = json.dumps(
            {
                "type": "session_expired",
                "session_id": "sess-789",
                "tenant_id": "firm-456",
            }
        ).encode()
        result = await self.handler.handle_push(body)
        assert result["status"] == "ok"


class TestDeadManSwitch:
    """Tests for Vent Mode dead-man's switch."""

    def test_ttl_value(self) -> None:
        assert DeadManSwitch.TTL_SECONDS == 2700  # 45 minutes
