# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ZxRunner — Shell automation adapter for google/zx.

Provides a Python interface to execute shell scripts through
the google/zx Node.js scripting library, enabling typed shell
execution with built-in error handling and structured output.
"""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default path to the google/zx clone
_DEFAULT_ZX_ROOT = Path(__file__).resolve().parents[3] / "external_repos" / "zx"


@dataclass
class ShellResult:
    """Result from a zx shell execution."""

    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float


class ZxRunner:
    """
    Python adapter for google/zx shell scripting.

    Executes shell commands through the zx runtime, providing:
    - Structured output capture
    - Timeout enforcement
    - Error isolation
    - Audit logging
    """

    def __init__(
        self,
        zx_root: Path | None = None,
        timeout_seconds: int = 30,
        node_path: str | None = None,
    ):
        self._zx_root = zx_root or _DEFAULT_ZX_ROOT
        self._timeout = timeout_seconds
        self._node_path = node_path or shutil.which("node") or "node"
        self._npx_path = shutil.which("npx") or "npx"
        self._execution_count = 0

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a shell command or script via zx.

        Args:
            payload: Must contain 'script' (inline script string)
                     or 'command' (simple shell command).

        Returns:
            Dict with stdout, stderr, exit_code, duration_ms.
        """
        script = payload.get("script", "")
        command = payload.get("command", "")
        timeout = payload.get("timeout", self._timeout)

        if not script and not command:
            return {"error": "Either 'script' or 'command' must be provided"}

        self._execution_count += 1

        if command:
            return await self._run_command(command, timeout)
        return await self._run_script(script, timeout)

    async def _run_command(self, command: str, timeout: int) -> dict[str, Any]:
        """Execute a simple shell command directly."""
        import time

        logger.info("zx_runner.command", command=command[:100])
        start = time.perf_counter()

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            duration_ms = (time.perf_counter() - start) * 1000

            result = ShellResult(
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                exit_code=proc.returncode or 0,
                duration_ms=duration_ms,
            )

            logger.info(
                "zx_runner.command.complete",
                exit_code=result.exit_code,
                duration_ms=round(duration_ms, 2),
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "duration_ms": round(duration_ms, 2),
            }

        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - start) * 1000
            return {"error": f"Command timed out after {timeout}s", "exit_code": -1, "duration_ms": round(duration_ms, 2)}

    async def _run_script(self, script: str, timeout: int) -> dict[str, Any]:
        """Execute a zx script through the zx runtime."""
        import time

        logger.info("zx_runner.script", length=len(script))
        start = time.perf_counter()

        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mjs", delete=False) as f:
            f.write(f'import {{ $ }} from "zx";\n\n{script}\n')
            script_path = f.name

        try:
            zx_bin = self._zx_root / "build" / "cli.js"
            if not zx_bin.exists():
                # Fallback to npx zx
                cmd = f"{self._npx_path} zx {script_path}"
            else:
                cmd = f"{self._node_path} {zx_bin} {script_path}"

            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            duration_ms = (time.perf_counter() - start) * 1000

            logger.info(
                "zx_runner.script.complete",
                exit_code=proc.returncode,
                duration_ms=round(duration_ms, 2),
            )

            return {
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "exit_code": proc.returncode or 0,
                "duration_ms": round(duration_ms, 2),
            }

        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - start) * 1000
            return {"error": f"Script timed out after {timeout}s", "exit_code": -1, "duration_ms": round(duration_ms, 2)}
        finally:
            Path(script_path).unlink(missing_ok=True)

    @property
    def execution_count(self) -> int:
        """Total executions since init."""
        return self._execution_count
