# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""Integration tests for A2A task lifecycle.

Tests the complete flow:
    submit_task -> Cor_Claude_Code_6 gate -> route_task -> complete/cancel/fail
"""

from __future__ import annotations

import pytest

from apps.counselconduit.agents.orchestrator import (
    AgentRole,
    Cor_Claude_Code_6Gate,
    Orchestrator,
    TaskContext,
    TaskState,
)


class TestCor_Claude_Code_6Gate:
    """Tests for the Judge 6 governance gate."""

    def setup_method(self) -> None:
        self.gate = Cor_Claude_Code_6Gate()

    def test_allow_valid_context(self) -> None:
        ctx = TaskContext(tenant_id="firm-123", user_id="user-456")
        allowed, reason = self.gate.evaluate(ctx, "research case law")
        assert allowed is True
        assert reason == "ALLOW"

    def test_deny_missing_tenant(self) -> None:
        ctx = TaskContext(user_id="user-456")
        allowed, reason = self.gate.evaluate(ctx, "research")
        assert allowed is False
        assert "tenant_id" in reason

    def test_deny_missing_user(self) -> None:
        ctx = TaskContext(tenant_id="firm-123")
        allowed, reason = self.gate.evaluate(ctx, "research")
        assert allowed is False
        assert "user_id" in reason

    def test_deny_regulated_domain(self) -> None:
        ctx = TaskContext(
            tenant_id="firm-123",
            user_id="user-456",
            metadata={"classified_domain": "medical_advice"},
        )
        allowed, reason = self.gate.evaluate(ctx, "diagnose patient")
        assert allowed is False
        assert "Regulated domain" in reason


class TestOrchestrator:
    """Tests for the ADK 2.0 Orchestrator."""

    def setup_method(self) -> None:
        self.orchestrator = Orchestrator()

    @pytest.mark.asyncio
    async def test_submit_task_success(self) -> None:
        ctx = await self.orchestrator.submit_task(
            "Research contract clause",
            tenant_id="firm-123",
            user_id="user-456",
        )
        assert ctx.state == TaskState.WORKING
        assert ctx.tenant_id == "firm-123"
        assert ctx.user_id == "user-456"
        assert ctx.task_id

    @pytest.mark.asyncio
    async def test_submit_task_blocked_by_judge(self) -> None:
        with pytest.raises(PermissionError, match="DENY"):
            await self.orchestrator.submit_task(
                "Diagnose me",
                tenant_id="",
                user_id="user-456",
            )

    @pytest.mark.asyncio
    async def test_route_to_oracle_default(self) -> None:
        ctx = await self.orchestrator.submit_task(
            "Analyze precedent",
            tenant_id="firm-123",
            user_id="user-456",
        )
        role = await self.orchestrator.route_task(ctx, "Analyze precedent")
        assert role == AgentRole.ORACLE

    @pytest.mark.asyncio
    async def test_route_to_vent_mode(self) -> None:
        ctx = await self.orchestrator.submit_task(
            "Exploratory research",
            tenant_id="firm-123",
            user_id="user-456",
            metadata={"mode": "vent"},
        )
        role = await self.orchestrator.route_task(ctx, "Exploratory research")
        assert role == AgentRole.VENT

    @pytest.mark.asyncio
    async def test_cancel_task(self) -> None:
        ctx = await self.orchestrator.submit_task(
            "Long running query",
            tenant_id="firm-123",
            user_id="user-456",
        )
        assert self.orchestrator.cancel_task(ctx.task_id) is True
        result = self.orchestrator.get_task(ctx.task_id)
        assert result is not None
        assert result.state == TaskState.CANCELED

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self) -> None:
        assert self.orchestrator.cancel_task("fake-id") is False

    def test_get_task_not_found(self) -> None:
        assert self.orchestrator.get_task("nonexistent") is None


class TestTaskContext:
    """Tests for TaskContext dataclass."""

    def test_default_values(self) -> None:
        ctx = TaskContext()
        assert ctx.role == AgentRole.ORCHESTRATOR
        assert ctx.state == TaskState.SUBMITTED
        assert ctx.model_preference == "gemini-3.1-flash-lite-preview-thinking"
        assert ctx.task_id
        assert ctx.created_at
