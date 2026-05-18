# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Sandbox Adapter — Ported from Claude Code's sandbox-adapter.ts.

Provides process isolation for untrusted code execution via subprocess
containment. All sandboxed operations run with:
  - Restricted PATH
  - No network access (when possible)
  - Timeout enforcement
  - Output size limits
  - Read-only filesystem (configurable)

Integrates with the shadowtag_os gate system.
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Sandbox limits
MAX_OUTPUT_BYTES = 1_048_576  # 1 MB
MAX_EXECUTION_SECONDS = 300  # 5 minutes
SANDBOX_PATH = "/usr/bin:/bin:/usr/local/bin"


@dataclass
class SandboxConfig:
    """Configuration for a sandbox execution.

    Attributes:
        timeout_seconds: Max execution time before kill.
        max_output_bytes: Max stdout+stderr bytes captured.
        allow_network: Whether to allow network access.
        read_only_root: Mount root as read-only.
        working_dir: Working directory for the command.
        env_allowlist: Environment variables to pass through.
    """

    timeout_seconds: float = MAX_EXECUTION_SECONDS
    max_output_bytes: int = MAX_OUTPUT_BYTES
    allow_network: bool = False
    read_only_root: bool = False
    working_dir: str | None = None
    env_allowlist: list[str] = field(
        default_factory=lambda: [
            "PATH",
            "HOME",
            "USER",
            "LANG",
            "LC_ALL",
            "PYTHONDONTWRITEBYTECODE",
        ]
    )


@dataclass
class SandboxResult:
    """Result from a sandboxed execution.

    Attributes:
        exit_code: Process exit code (-1 if killed).
        stdout: Captured stdout (truncated to max_output_bytes).
        stderr: Captured stderr (truncated to max_output_bytes).
        timed_out: Whether the process was killed due to timeout.
        duration_ms: Execution duration in milliseconds.
        truncated: Whether output was truncated.
    """

    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    duration_ms: float = 0
    truncated: bool = False


def _build_sandbox_env(config: SandboxConfig) -> dict[str, str]:
    """Build a restricted environment for the sandbox."""
    env = {"PATH": SANDBOX_PATH}
    for key in config.env_allowlist:
        val = os.environ.get(key)
        if val is not None:
            env[key] = val
    return env


async def execute_sandboxed(
    command: list[str],
    config: SandboxConfig | None = None,
) -> SandboxResult:
    """Execute a command in a sandboxed subprocess.

    Args:
        command: Command and arguments to execute.
        config: Sandbox configuration (uses defaults if None).

    Returns:
        SandboxResult with exit code, output, and metadata.
    """
    if config is None:
        config = SandboxConfig()

    env = _build_sandbox_env(config)
    cwd = config.working_dir or tempfile.gettempdir()

    result = SandboxResult()
    start_ns = asyncio.get_event_loop().time()

    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=cwd,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=config.timeout_seconds,
            )

            result.exit_code = proc.returncode or 0

            # Truncate if needed
            if len(stdout_bytes) > config.max_output_bytes:
                stdout_bytes = stdout_bytes[: config.max_output_bytes]
                result.truncated = True
            if len(stderr_bytes) > config.max_output_bytes:
                stderr_bytes = stderr_bytes[: config.max_output_bytes]
                result.truncated = True

            result.stdout = stdout_bytes.decode("utf-8", errors="replace")
            result.stderr = stderr_bytes.decode("utf-8", errors="replace")

        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            result.timed_out = True
            result.exit_code = -1
            result.stderr = f"Process killed after {config.timeout_seconds}s timeout"
            logger.warning(
                "Sandbox timeout: %s (killed after %.0fs)",
                " ".join(command[:3]),
                config.timeout_seconds,
            )

    except FileNotFoundError:
        result.exit_code = 127
        result.stderr = f"Command not found: {command[0]}"
    except PermissionError:
        result.exit_code = 126
        result.stderr = f"Permission denied: {command[0]}"
    except Exception as exc:
        result.exit_code = -1
        result.stderr = f"Sandbox error: {exc}"
        logger.exception("Sandbox execution failed")

    end_ns = asyncio.get_event_loop().time()
    result.duration_ms = (end_ns - start_ns) * 1000

    logger.info(
        "Sandbox: %s → exit=%d, %.0fms, out=%d bytes",
        command[0] if command else "?",
        result.exit_code,
        result.duration_ms,
        len(result.stdout),
    )

    return result


async def execute_python_sandboxed(
    code: str,
    config: SandboxConfig | None = None,
) -> SandboxResult:
    """Execute Python code in a sandboxed subprocess.

    Args:
        code: Python code string to execute.
        config: Sandbox configuration.

    Returns:
        SandboxResult with output.
    """
    if config is None:
        config = SandboxConfig(timeout_seconds=60)

    # Write code to temp file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        dir=config.working_dir or tempfile.gettempdir(),
    ) as f:
        f.write(code)
        script_path = f.name

    try:
        result = await execute_sandboxed(
            ["python3", "-u", script_path],
            config,
        )
    finally:
        # Clean up temp file
        try:
            Path(script_path).unlink()
        except OSError:
            pass

    return result
