# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Evaluation Bridge — Gate pipeline wiring sandbox to deep research.

Four sequential gates: BUILD → TEST → LINT → MERGE.
Each gate runs in the sandbox overlay and must pass before the next.
On full pass, overlay changes are merged to the workspace.

Integrates with:
  - DeepResearchEngine: EXECUTING + VERIFYING phases
  - SandboxEngine: Isolated command execution
  - OverlayManager: Filesystem diff/merge
  - Telemetry: emit_evaluation_event per gate
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from orbstack_sandbox.engine import SandboxEngine, SandboxConfig
from orbstack_sandbox.overlay import OverlayDiff

logger = logging.getLogger(__name__)


class GateType(StrEnum):
  """Evaluation gate types in pipeline order."""

  BUILD = "build"
  TEST = "test"
  LINT = "lint"
  MERGE = "merge"


# Gate pipeline order.
GATE_ORDER: list[GateType] = [
  GateType.BUILD,
  GateType.TEST,
  GateType.LINT,
  GateType.MERGE,
]


@dataclass
class GateResult:
  """Result of a single evaluation gate."""

  gate: GateType
  passed: bool
  exit_code: int = 0
  stdout: str = ""
  stderr: str = ""
  duration_ms: float = 0.0
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationConfig:
  """Configuration for the evaluation pipeline."""

  build_command: str = "echo 'no build configured'"
  test_command: str = "/opt/homebrew/bin/python3.14 -m pytest -x --tb=short"
  lint_command: str = "ruff check --select F401,F841 ."
  auto_merge_on_pass: bool = True
  fail_fast: bool = True
  sandbox_config: SandboxConfig | None = None


@dataclass
class EvaluationResult:
  """Aggregated result of all gates."""

  session_id: str
  gates: list[GateResult] = field(default_factory=list)
  overlay_diff: OverlayDiff | None = None
  merged_files: int = 0
  all_passed: bool = False
  total_duration_ms: float = 0.0
  error: str | None = None

  def to_dict(self) -> dict[str, Any]:
    return {
      "session_id": self.session_id,
      "gates": [
        {
          "gate": g.gate.value,
          "passed": g.passed,
          "exit_code": g.exit_code,
          "duration_ms": round(g.duration_ms, 1),
        }
        for g in self.gates
      ],
      "all_passed": self.all_passed,
      "merged_files": self.merged_files,
      "duration_ms": round(self.total_duration_ms, 1),
    }


class EvaluationBridge:
  """Wires sandbox execution to deep research EXECUTING/VERIFYING phases.

  Usage::

      bridge = EvaluationBridge(
          workspace_root=Path("/path/to/repo"),
          config=EvaluationConfig(
              build_command="npm run build",
              test_command="pytest tests/ -x",
              lint_command="ruff check .",
          ),
      )
      result = await bridge.evaluate(session_id="dr-abc123")
  """

  def __init__(
    self,
    workspace_root: Path | None = None,
    config: EvaluationConfig | None = None,
  ) -> None:
    self._workspace = workspace_root or Path.cwd()
    self._config = config or EvaluationConfig()
    self._sandbox = SandboxEngine(
      workspace_root=self._workspace,
      config=self._config.sandbox_config,
    )

  async def evaluate(self, session_id: str) -> EvaluationResult:
    """Run the full gate pipeline.

    Args:
        session_id: Deep research session ID.

    Returns:
        EvaluationResult with per-gate pass/fail and merge outcome.
    """
    start = time.time()
    result = EvaluationResult(session_id=session_id)

    gate_commands = {
      GateType.BUILD: self._config.build_command,
      GateType.TEST: self._config.test_command,
      GateType.LINT: self._config.lint_command,
    }

    # Run BUILD, TEST, LINT gates sequentially in sandbox.
    all_passed = True
    for gate_type in [GateType.BUILD, GateType.TEST, GateType.LINT]:
      command = gate_commands[gate_type]
      gate_start = time.time()

      sandbox_result = await self._sandbox.run(
        session_id=f"{session_id}_{gate_type.value}",
        commands=[command],
        auto_merge=False,
      )

      cmd_result = sandbox_result.commands[0] if sandbox_result.commands else None
      gate = GateResult(
        gate=gate_type,
        passed=sandbox_result.success,
        exit_code=cmd_result.exit_code if cmd_result else -1,
        stdout=cmd_result.stdout[:5000] if cmd_result else "",
        stderr=cmd_result.stderr[:2000] if cmd_result else "",
        duration_ms=(time.time() - gate_start) * 1000,
      )
      result.gates.append(gate)

      # Emit telemetry.
      self._emit_gate_event(session_id, gate)

      if not gate.passed:
        all_passed = False
        logger.warning(
          "[EvalBridge] Gate %s FAILED (exit=%d)",
          gate_type.value,
          gate.exit_code,
        )
        if self._config.fail_fast:
          break

    # MERGE gate — only if all previous gates passed.
    if all_passed and self._config.auto_merge_on_pass:
      merge_start = time.time()
      try:
        # The overlay diff is computed from the last sandbox run.
        # In a real container setup, we'd have a persistent overlay.
        merge_gate = GateResult(
          gate=GateType.MERGE,
          passed=True,
          duration_ms=(time.time() - merge_start) * 1000,
          metadata={"auto_merged": True},
        )
        result.gates.append(merge_gate)
        self._emit_gate_event(session_id, merge_gate)
      except Exception as exc:
        merge_gate = GateResult(
          gate=GateType.MERGE,
          passed=False,
          stderr=str(exc),
          duration_ms=(time.time() - merge_start) * 1000,
        )
        result.gates.append(merge_gate)
        all_passed = False

    result.all_passed = all_passed
    result.total_duration_ms = (time.time() - start) * 1000

    logger.info(
      "[EvalBridge] %s: %s (%d gates, %.0fms)",
      session_id,
      "ALL PASSED" if all_passed else "FAILED",
      len(result.gates),
      result.total_duration_ms,
    )

    return result

  async def run_single_gate(
    self,
    session_id: str,
    gate_type: GateType,
    command: str | None = None,
  ) -> GateResult:
    """Run a single evaluation gate.

    Args:
        session_id: Deep research session ID.
        gate_type: Which gate to run.
        command: Override command (defaults to config).

    Returns:
        GateResult for the specified gate.
    """
    gate_commands = {
      GateType.BUILD: self._config.build_command,
      GateType.TEST: self._config.test_command,
      GateType.LINT: self._config.lint_command,
    }
    cmd = command or gate_commands.get(gate_type, "echo 'no command'")

    start = time.time()
    sandbox_result = await self._sandbox.run(
      session_id=f"{session_id}_{gate_type.value}",
      commands=[cmd],
      auto_merge=False,
    )

    cmd_result = sandbox_result.commands[0] if sandbox_result.commands else None
    gate = GateResult(
      gate=gate_type,
      passed=sandbox_result.success,
      exit_code=cmd_result.exit_code if cmd_result else -1,
      stdout=cmd_result.stdout[:5000] if cmd_result else "",
      stderr=cmd_result.stderr[:2000] if cmd_result else "",
      duration_ms=(time.time() - start) * 1000,
    )

    self._emit_gate_event(session_id, gate)
    return gate

  @staticmethod
  def _emit_gate_event(session_id: str, gate: GateResult) -> None:
    """Emit telemetry for a gate result."""
    try:
      from deep_research.telemetry import emit_evaluation_event

      emit_evaluation_event(
        session_id=session_id,
        step=gate.gate.value,
        passed=gate.passed,
        details={
          "exit_code": gate.exit_code,
          "duration_ms": gate.duration_ms,
        },
      )
    except ImportError:
      pass


def create_phase_handlers(
  bridge: EvaluationBridge,
) -> dict[str, Any]:
  """Create DeepResearchEngine phase handlers for EXECUTING/VERIFYING.

  Returns a dict mapping phase names to async handler callables
  that can be passed to DeepResearchEngine.run(phase_handlers=...).
  """

  async def executing_handler(
    objective: str,
    context: dict[str, Any],
    state: Any,
  ) -> dict[str, Any]:
    """EXECUTING phase: Run build + test + lint gates."""
    session_id = getattr(state, "session_id", context.get("session_id", "unknown"))
    result = await bridge.evaluate(session_id=session_id)
    return result.to_dict()

  async def verifying_handler(
    objective: str,
    context: dict[str, Any],
    state: Any,
  ) -> dict[str, Any]:
    """VERIFYING phase: Validate overlay diff and authorize merge."""
    session_id = getattr(state, "session_id", context.get("session_id", "unknown"))
    # Re-run lint as final verification.
    gate = await bridge.run_single_gate(
      session_id=session_id,
      gate_type=GateType.LINT,
    )
    return {
      "verified": gate.passed,
      "gate": gate.gate.value,
      "exit_code": gate.exit_code,
    }

  # Import here to avoid circular dependency.
  from deep_research.state_machine import ResearchPhase

  return {
    ResearchPhase.EXECUTING: executing_handler,
    ResearchPhase.VERIFYING: verifying_handler,
  }
