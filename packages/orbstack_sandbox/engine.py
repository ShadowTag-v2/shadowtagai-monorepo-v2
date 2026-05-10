# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Sandbox Engine — Container lifecycle for isolated code execution.

Deterministic lifecycle: PENDING → CREATING → READY → EXECUTING →
VERIFYING → MERGING → DESTROYED.

Integrates with OverlayManager for filesystem isolation and
DeepResearchEngine for phase-gated execution.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from orbstack_sandbox.overlay import OverlayDiff, OverlayManager

logger = logging.getLogger(__name__)


class ContainerLifecycle(StrEnum):
  """Container lifecycle states."""

  PENDING = "pending"
  CREATING = "creating"
  READY = "ready"
  EXECUTING = "executing"
  VERIFYING = "verifying"
  MERGING = "merging"
  DESTROYED = "destroyed"
  ERROR = "error"


@dataclass
class SandboxConfig:
  """Configuration for a sandbox container."""

  image: str = "python:3.14-slim"
  workspace_mount: str = "/workspace"
  overlay_mount: str = "/overlay"
  memory_limit: str = "512m"
  cpu_limit: float = 1.0
  timeout_s: float = 120.0
  network_enabled: bool = False
  read_only_workspace: bool = True
  env_vars: dict[str, str] = field(default_factory=dict)
  allowed_commands: set[str] = field(
    default_factory=lambda: {
      "python",
      "pip",
      "pytest",
      "ruff",
      "biome",
      "npm",
      "node",
    }
  )


@dataclass
class CommandResult:
  """Result of a single command execution in the sandbox."""

  command: str
  exit_code: int
  stdout: str
  stderr: str
  duration_ms: float


@dataclass
class SandboxResult:
  """Complete result of a sandbox session."""

  session_id: str
  container_id: str
  lifecycle: ContainerLifecycle
  commands: list[CommandResult] = field(default_factory=list)
  overlay_diff: OverlayDiff | None = None
  merged_files: int = 0
  total_duration_ms: float = 0.0
  success: bool = False
  error: str | None = None

  def to_dict(self) -> dict[str, Any]:
    return {
      "session_id": self.session_id,
      "container_id": self.container_id[:12],
      "lifecycle": self.lifecycle.value,
      "commands_run": len(self.commands),
      "overlay_changes": self.overlay_diff.file_count if self.overlay_diff else 0,
      "merged_files": self.merged_files,
      "duration_ms": round(self.total_duration_ms, 1),
      "success": self.success,
      "error": self.error,
    }


class SandboxEngine:
  """Orchestrates isolated container execution with overlay merging.

  Usage::

      engine = SandboxEngine(workspace_root=Path("/path/to/repo"))
      result = await engine.run(
          session_id="dr-abc123",
          commands=["pytest tests/", "ruff check ."],
      )
  """

  def __init__(
    self,
    workspace_root: Path | None = None,
    config: SandboxConfig | None = None,
    overlay_manager: OverlayManager | None = None,
  ) -> None:
    self._workspace = workspace_root or Path.cwd()
    self._config = config or SandboxConfig()
    self._overlay = overlay_manager or OverlayManager(
      workspace_root=self._workspace,
    )
    self._lifecycle = ContainerLifecycle.PENDING
    self._container_id = ""

  @property
  def lifecycle(self) -> ContainerLifecycle:
    return self._lifecycle

  @property
  def container_id(self) -> str:
    return self._container_id

  async def run(
    self,
    session_id: str,
    commands: list[str],
    auto_merge: bool = False,
  ) -> SandboxResult:
    """Execute commands in an isolated sandbox.

    Args:
        session_id: Deep research session ID.
        commands: Shell commands to execute sequentially.
        auto_merge: If True, automatically merge overlay on success.

    Returns:
        SandboxResult with command outputs and overlay diff.
    """
    start = time.time()
    self._container_id = f"sb-{uuid.uuid4().hex[:12]}"
    result = SandboxResult(
      session_id=session_id,
      container_id=self._container_id,
      lifecycle=ContainerLifecycle.PENDING,
    )

    try:
      # Phase 1: Create overlay.
      self._lifecycle = ContainerLifecycle.CREATING
      overlay_path = self._overlay.create(session_id)
      self._lifecycle = ContainerLifecycle.READY

      # Phase 2: Execute commands.
      self._lifecycle = ContainerLifecycle.EXECUTING
      all_passed = True
      for cmd in commands:
        cmd_result = await self._execute_command(
          cmd,
          overlay_path,
        )
        result.commands.append(cmd_result)
        if cmd_result.exit_code != 0:
          all_passed = False
          break

      # Phase 3: Compute diff.
      self._lifecycle = ContainerLifecycle.VERIFYING
      result.overlay_diff = self._overlay.compute_diff(session_id)

      # Phase 4: Merge if requested and all passed.
      if auto_merge and all_passed and result.overlay_diff.has_changes:
        self._lifecycle = ContainerLifecycle.MERGING
        result.merged_files = self._overlay.merge_to_workspace(
          session_id,
        )

      result.success = all_passed

    except Exception as exc:
      self._lifecycle = ContainerLifecycle.ERROR
      result.error = str(exc)
      logger.exception("[Sandbox] Session %s failed: %s", session_id, exc)

    finally:
      # Always destroy overlay.
      self._overlay.destroy(session_id)
      self._lifecycle = ContainerLifecycle.DESTROYED

    result.lifecycle = self._lifecycle
    result.total_duration_ms = (time.time() - start) * 1000

    logger.info(
      "[Sandbox] %s: %d commands, %s (%.0fms)",
      session_id,
      len(result.commands),
      "PASS" if result.success else "FAIL",
      result.total_duration_ms,
    )

    # Emit telemetry.
    try:
      from deep_research.telemetry import emit_sandbox_event

      emit_sandbox_event(
        session_id=session_id,
        action="complete",
        container_id=self._container_id,
        duration_ms=result.total_duration_ms,
        success=result.success,
      )
    except ImportError:
      pass

    return result

  async def _execute_command(
    self,
    command: str,
    overlay_path: Path,
  ) -> CommandResult:
    """Execute a single command in the sandbox environment.

    Uses subprocess with workspace and overlay env vars set.
    For OrbStack containers, this would use `orbctl run`.
    Currently runs locally with overlay-aware environment.
    """
    start = time.time()
    env = {
      "WORKSPACE": str(self._workspace),
      "OVERLAY": str(overlay_path),
      "HOME": str(overlay_path / ".home"),
      "PATH": "/usr/local/bin:/usr/bin:/bin",
      **self._config.env_vars,
    }

    try:
      proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(self._workspace),
        env=env,
      )
      stdout_bytes, stderr_bytes = await asyncio.wait_for(
        proc.communicate(),
        timeout=self._config.timeout_s,
      )
      duration_ms = (time.time() - start) * 1000
      return CommandResult(
        command=command,
        exit_code=proc.returncode or 0,
        stdout=stdout_bytes.decode("utf-8", errors="replace")[:10000],
        stderr=stderr_bytes.decode("utf-8", errors="replace")[:5000],
        duration_ms=duration_ms,
      )
    except TimeoutError:
      duration_ms = (time.time() - start) * 1000
      return CommandResult(
        command=command,
        exit_code=-1,
        stdout="",
        stderr=f"Command timed out after {self._config.timeout_s}s",
        duration_ms=duration_ms,
      )
    except Exception as exc:
      duration_ms = (time.time() - start) * 1000
      return CommandResult(
        command=command,
        exit_code=-2,
        stdout="",
        stderr=str(exc),
        duration_ms=duration_ms,
      )


def create_sandbox(
  workspace_root: Path | None = None,
  config: SandboxConfig | None = None,
) -> SandboxEngine:
  """Convenience factory for SandboxEngine."""
  return SandboxEngine(workspace_root=workspace_root, config=config)
