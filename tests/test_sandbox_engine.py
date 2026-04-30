# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for orbstack_sandbox.engine module."""

from __future__ import annotations

from pathlib import Path

import pytest

from orbstack_sandbox.engine import (
    ContainerLifecycle,
    SandboxConfig,
    SandboxEngine,
    SandboxResult,
    create_sandbox,
)


class TestContainerLifecycle:
    def test_all_states(self) -> None:
        states = [s.value for s in ContainerLifecycle]
        assert "pending" in states
        assert "executing" in states
        assert "destroyed" in states

    def test_string_enum(self) -> None:
        assert ContainerLifecycle.READY == "ready"


class TestSandboxConfig:
    def test_defaults(self) -> None:
        cfg = SandboxConfig()
        assert cfg.image == "python:3.14-slim"
        assert cfg.timeout_s == 120.0
        assert "pytest" in cfg.allowed_commands

    def test_custom(self) -> None:
        cfg = SandboxConfig(image="node:22", timeout_s=60.0)
        assert cfg.image == "node:22"


class TestSandboxResult:
    def test_to_dict(self) -> None:
        result = SandboxResult(
            session_id="dr-test",
            container_id="sb-abc123def456",
            lifecycle=ContainerLifecycle.DESTROYED,
            success=True,
        )
        d = result.to_dict()
        assert d["session_id"] == "dr-test"
        assert d["success"] is True
        assert len(d["container_id"]) == 12


class TestSandboxEngine:
    @pytest.mark.asyncio
    async def test_run_echo(self, tmp_path: Path) -> None:
        engine = SandboxEngine(workspace_root=tmp_path)
        result = await engine.run(
            session_id="test-echo",
            commands=["echo hello"],
        )
        assert result.success is True
        assert len(result.commands) == 1
        assert "hello" in result.commands[0].stdout
        assert result.commands[0].exit_code == 0

    @pytest.mark.asyncio
    async def test_run_failing_command(self, tmp_path: Path) -> None:
        engine = SandboxEngine(workspace_root=tmp_path)
        result = await engine.run(
            session_id="test-fail",
            commands=["exit 1"],
        )
        assert result.success is False
        assert result.commands[0].exit_code == 1

    @pytest.mark.asyncio
    async def test_run_multiple_commands_stops_on_fail(self, tmp_path: Path) -> None:
        engine = SandboxEngine(workspace_root=tmp_path)
        result = await engine.run(
            session_id="test-multi",
            commands=["echo first", "exit 1", "echo never"],
        )
        assert result.success is False
        assert len(result.commands) == 2  # stopped after failure

    @pytest.mark.asyncio
    async def test_lifecycle_ends_destroyed(self, tmp_path: Path) -> None:
        engine = SandboxEngine(workspace_root=tmp_path)
        await engine.run(session_id="test-lc", commands=["echo ok"])
        assert engine.lifecycle == ContainerLifecycle.DESTROYED


class TestCreateSandbox:
    def test_factory(self, tmp_path: Path) -> None:
        engine = create_sandbox(workspace_root=tmp_path)
        assert isinstance(engine, SandboxEngine)
        assert engine.lifecycle == ContainerLifecycle.PENDING
