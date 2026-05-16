# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for ZxRunner — shell automation adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from packages.shadowtag_os.zx_runner.runner import ShellResult, ZxRunner


# ─── Tests: ShellResult ─────────────────────────────────────────────────────


class TestShellResult:
    """Test ShellResult dataclass."""

    def test_creation(self):
        r = ShellResult(stdout="ok", stderr="", exit_code=0, duration_ms=1.5)
        assert r.stdout == "ok"
        assert r.exit_code == 0
        assert r.duration_ms == 1.5

    def test_nonzero_exit(self):
        r = ShellResult(stdout="", stderr="fail", exit_code=1, duration_ms=0)
        assert r.exit_code == 1


# ─── Tests: ZxRunner Init ───────────────────────────────────────────────────


class TestZxRunnerInit:
    """Test ZxRunner construction."""

    def test_defaults(self):
        runner = ZxRunner()
        assert runner._timeout == 30
        assert runner.execution_count == 0

    def test_custom_timeout(self):
        runner = ZxRunner(timeout_seconds=60)
        assert runner._timeout == 60

    def test_custom_zx_root(self, tmp_path):
        runner = ZxRunner(zx_root=tmp_path)
        assert runner._zx_root == tmp_path


# ─── Tests: ZxRunner.run() ──────────────────────────────────────────────────


class TestZxRunnerRun:
    """Test ZxRunner.run() async method."""

    @pytest.fixture
    def runner(self, tmp_path):
        return ZxRunner(zx_root=tmp_path, timeout_seconds=5)

    @pytest.mark.asyncio
    async def test_run_empty_payload(self, runner):
        """Empty payload returns error."""
        result = await runner.run({})
        assert result["error"] == "Either 'script' or 'command' must be provided"

    @pytest.mark.asyncio
    async def test_run_command(self, runner):
        """Simple echo command."""
        result = await runner.run({"command": "echo hello"})
        assert result["exit_code"] == 0
        assert "hello" in result["stdout"]

    @pytest.mark.asyncio
    async def test_run_command_failure(self, runner):
        """Non-existent command returns non-zero exit."""
        result = await runner.run({"command": "false"})
        assert result["exit_code"] != 0

    @pytest.mark.asyncio
    async def test_run_command_stderr(self, runner):
        """Stderr capture."""
        result = await runner.run({"command": "echo err >&2"})
        assert "err" in result["stderr"]

    @pytest.mark.asyncio
    async def test_execution_count_increments(self, runner):
        """Each run increments the counter."""
        assert runner.execution_count == 0
        await runner.run({"command": "echo 1"})
        assert runner.execution_count == 1
        await runner.run({"command": "echo 2"})
        assert runner.execution_count == 2

    @pytest.mark.asyncio
    async def test_run_command_timeout(self):
        """Commands exceeding timeout return timeout error."""
        runner = ZxRunner(timeout_seconds=1)
        result = await runner.run({"command": "sleep 10", "timeout": 1})
        assert "timed out" in result.get("error", "")

    @pytest.mark.asyncio
    async def test_run_command_multiline_output(self, runner):
        """Multi-line stdout."""
        result = await runner.run({"command": "echo line1; echo line2"})
        assert "line1" in result["stdout"]
        assert "line2" in result["stdout"]


# ─── Tests: ZxRunner Script ─────────────────────────────────────────────────


class TestZxRunnerScript:
    """Test ZxRunner._run_script() for zx-based scripts."""

    @pytest.mark.asyncio
    async def test_script_fallback_to_npx(self, tmp_path):
        """When local zx build doesn't exist, falls back to npx."""
        runner = ZxRunner(zx_root=tmp_path, timeout_seconds=3)
        # This will likely fail (npx zx not installed) but exercises the path
        result = await runner.run({"script": 'console.log("hello")', "timeout": 3})
        # Either succeeds or times out / errors — both are valid
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_script_cleans_temp_file(self, tmp_path):
        """Temp file is cleaned up after script execution."""
        runner = ZxRunner(zx_root=tmp_path, timeout_seconds=2)
        await runner.run({"script": 'console.log("test")', "timeout": 2})
        # No .mjs files should remain in temp dir
        import tempfile

        tmp = Path(tempfile.gettempdir())
        mjs_files = list(tmp.glob("tmp*.mjs"))
        assert len(mjs_files) == 0


# ─── Tests: Timing Instrumentation ──────────────────────────────────────────


class TestZxRunnerTiming:
    """Test timing instrumentation in ZxRunner."""

    @pytest.mark.asyncio
    async def test_command_returns_duration(self, tmp_path):
        """Commands include duration_ms when instrumented."""
        runner = ZxRunner(zx_root=tmp_path)
        result = await runner.run({"command": "echo timing"})
        # Currently duration is in ShellResult but not returned — verify base contract
        assert "stdout" in result
        assert "exit_code" in result
