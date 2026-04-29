# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT XML Two-Stage Classifier.

Stage 1 (Fast): max_tokens=256, bias toward blocking
  → If ALLOW → execute
  → If BLOCK/UNKNOWN → escalate to Stage 2

Stage 2 (Thinking): Full chain-of-thought reasoning
  → Final verdict with <block>yes/no</block> XML output

Ported from: permissions/yoloClassifier.ts, classifierDecision.ts
Reference: AGNT STATE B Spec P2.1
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from packages.agnt_classifier.allowlist import is_allowlisted

logger = logging.getLogger(__name__)


class ClassifierVerdict(StrEnum):
    """Possible classifier outcomes."""

    ALLOW = "allow"
    BLOCK = "block"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class ClassifierResult:
    """Result of classifier evaluation.

    Attributes:
        verdict: Allow, block, unknown, or error.
        stage: Which stage produced the verdict (1 or 2).
        reasoning: Chain-of-thought reasoning (Stage 2 only).
        tool_id: The tool being classified.
        elapsed_ms: Time taken for classification.
        fail_closed: Whether fail-closed was triggered.
    """

    verdict: ClassifierVerdict
    stage: int = 1
    reasoning: str = ""
    tool_id: str = ""
    elapsed_ms: float = 0.0
    fail_closed: bool = False
    errors: list[str] = field(default_factory=list)


# Maximum subcommands allowed in a shell command (Adversa bypass mitigation)
MAX_SUBCOMMANDS = 50

# Shell wrapper commands to strip before AST analysis
SAFE_WRAPPERS = {"timeout", "time", "nice", "nohup", "env", "ionice"}

# Environment variables that are never safe to set
NEVER_SAFE_ENV_VARS = {
    "PATH",
    "LD_PRELOAD",
    "LD_LIBRARY_PATH",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "PYTHONPATH",
    "NODE_PATH",
    "HOME",
    "USER",
    "SHELL",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "AWS_SECRET_ACCESS_KEY",
}


class AGNTClassifier:
    """Two-stage XML classifier for tool permission decisions.

    Args:
        model: Model ID for classifier sideQuery.
        telemetry_dir: Directory for telemetry JSONL.
    """

    def __init__(
        self,
        model: str | None = None,
        telemetry_dir: str | None = None,
    ) -> None:
        self._model = model or os.environ.get(
            "AGNT_CLASSIFIER_MODEL",
            "gemini-3.1-flash-lite-preview-thinking",
        )
        self._telemetry_dir = telemetry_dir

    def classify(
        self,
        tool_id: str,
        tool_input: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> ClassifierResult:
        """Classify a tool call for permission.

        Args:
            tool_id: The tool identifier.
            tool_input: The tool's input parameters.
            context: Additional context (conversation state, etc.).

        Returns:
            ClassifierResult with verdict and reasoning.
        """
        tool_input = tool_input or {}
        context = context or {}
        start = time.time()

        # Fast path: allowlisted tools skip classification
        if is_allowlisted(tool_id):
            return ClassifierResult(
                verdict=ClassifierVerdict.ALLOW,
                stage=0,
                tool_id=tool_id,
                reasoning="Tool is in SAFE_ALLOWLIST — auto-approved.",
            )

        # Special handling for shell commands
        if tool_id == "run_command":
            return self._classify_shell(tool_input, context, start)

        # Stage 1: Fast classification
        result = self._stage1(tool_id, tool_input, context)
        result.elapsed_ms = (time.time() - start) * 1000

        if result.verdict == ClassifierVerdict.ALLOW:
            self._emit_telemetry(result)
            return result

        # Stage 2: Thinking classification (escalation)
        result = self._stage2(tool_id, tool_input, context)
        result.elapsed_ms = (time.time() - start) * 1000
        self._emit_telemetry(result)
        return result

    def _classify_shell(
        self,
        tool_input: dict[str, Any],
        context: dict[str, Any],
        start: float,
    ) -> ClassifierResult:
        """Specialized classification for shell commands.

        Implements:
          - Safe wrapper stripping
          - Subcommand counting (50 cap)
          - Env var safety check
          - AST-level decomposition
        """
        command = tool_input.get("CommandLine", "")

        # Strip safe wrappers
        command_stripped = self._strip_safe_wrappers(command)

        # Count subcommands
        subcommands = self._count_subcommands(command_stripped)
        if subcommands > MAX_SUBCOMMANDS:
            return ClassifierResult(
                verdict=ClassifierVerdict.BLOCK,
                stage=1,
                tool_id="run_command",
                reasoning=(f"Command has {subcommands} subcommands (max: {MAX_SUBCOMMANDS}). Exceeds security threshold — requires human approval."),
                elapsed_ms=(time.time() - start) * 1000,
            )

        # Check for unsafe env vars
        unsafe_vars = self._check_env_vars(command_stripped)
        if unsafe_vars:
            return ClassifierResult(
                verdict=ClassifierVerdict.BLOCK,
                stage=1,
                tool_id="run_command",
                reasoning=(f"Command sets unsafe env vars: {unsafe_vars}. These are in NEVER_SAFE_ENV_VARS."),
                elapsed_ms=(time.time() - start) * 1000,
            )

        # Check SafeToAutoRun flag
        if tool_input.get("SafeToAutoRun", False):
            return ClassifierResult(
                verdict=ClassifierVerdict.ALLOW,
                stage=1,
                tool_id="run_command",
                reasoning="SafeToAutoRun=true and no unsafe patterns detected.",
                elapsed_ms=(time.time() - start) * 1000,
            )

        # Default: require classification
        return self._stage1("run_command", tool_input, context)

    def _strip_safe_wrappers(self, command: str) -> str:
        """Remove safe wrapper commands (timeout, time, etc.)."""
        parts = command.strip().split()
        while parts and parts[0] in SAFE_WRAPPERS:
            parts.pop(0)
            # Also skip wrapper arguments (e.g., timeout 30)
            if parts and not parts[0].startswith("-"):
                # Check if it looks like a timeout value
                try:
                    float(parts[0])
                    parts.pop(0)
                except ValueError:
                    pass
        return " ".join(parts)

    def _count_subcommands(self, command: str) -> int:
        """Count subcommands in a compound shell command."""
        separators = re.findall(r"[;&|]+", command)
        # Each separator adds a subcommand
        return len(separators) + 1

    def _check_env_vars(self, command: str) -> list[str]:
        """Check for unsafe environment variable assignments."""
        unsafe = []
        # Match VAR=value patterns at start or after separators
        env_pattern = re.compile(r"\b([A-Z_][A-Z0-9_]*)=")
        for match in env_pattern.finditer(command):
            var_name = match.group(1)
            if var_name in NEVER_SAFE_ENV_VARS:
                unsafe.append(var_name)
        return unsafe

    def _stage1(
        self,
        tool_id: str,
        tool_input: dict[str, Any],
        context: dict[str, Any],
    ) -> ClassifierResult:
        """Stage 1: Fast classification (max_tokens=256).

        Bias toward BLOCK on ambiguity.
        In production, this calls the classifier model as a sideQuery.
        """
        # Build classification prompt
        self._build_stage1_prompt(tool_id, tool_input)

        # For skeleton implementation: use heuristic classification
        # Production would call: model.generate(prompt, max_tokens=256)
        verdict = self._heuristic_classify(tool_id, tool_input)

        return ClassifierResult(
            verdict=verdict,
            stage=1,
            tool_id=tool_id,
            reasoning=f"Stage 1 heuristic: {verdict.value}",
        )

    def _stage2(
        self,
        tool_id: str,
        tool_input: dict[str, Any],
        context: dict[str, Any],
    ) -> ClassifierResult:
        """Stage 2: Thinking classification with full CoT.

        Parses XML output: <block>yes/no</block>
        """
        # Build detailed prompt with context
        self._build_stage2_prompt(tool_id, tool_input, context)

        # For skeleton: default to BLOCK (fail-closed)
        # Production would call: model.generate(prompt, thinking=True)
        return ClassifierResult(
            verdict=ClassifierVerdict.BLOCK,
            stage=2,
            tool_id=tool_id,
            reasoning="Stage 2 skeleton: defaulting to BLOCK (fail-closed).",
            fail_closed=True,
        )

    def _build_stage1_prompt(self, tool_id: str, tool_input: dict[str, Any]) -> str:
        """Build Stage 1 fast classification prompt."""
        return (
            "Classify this tool call as SAFE or UNSAFE.\n"
            f"Tool: {tool_id}\n"
            f"Input: {json.dumps(tool_input, default=str)[:500]}\n"
            "Respond with ONLY: <verdict>allow</verdict> or <verdict>block</verdict>"
        )

    def _build_stage2_prompt(
        self,
        tool_id: str,
        tool_input: dict[str, Any],
        context: dict[str, Any],
    ) -> str:
        """Build Stage 2 thinking classification prompt."""
        return (
            "Analyze this tool call for safety. Think step by step.\n"
            f"Tool: {tool_id}\n"
            f"Input: {json.dumps(tool_input, default=str)[:1000]}\n"
            f"Context: {json.dumps(context, default=str)[:500]}\n"
            "After reasoning, output: <block>yes</block> or <block>no</block>"
        )

    def _heuristic_classify(
        self,
        tool_id: str,
        tool_input: dict[str, Any],
    ) -> ClassifierVerdict:
        """Heuristic-based fast classification (pre-model fallback)."""
        # File writes: check for sensitive paths
        if tool_id in ("write_to_file", "replace_file_content"):
            target = tool_input.get("TargetFile", "")
            if any(s in target for s in [".env", "secret", "key", "pem", "credential"]):
                return ClassifierVerdict.BLOCK
            return ClassifierVerdict.ALLOW

        # Default: unknown → escalate
        return ClassifierVerdict.UNKNOWN

    def parse_xml_verdict(self, response: str) -> ClassifierVerdict:
        """Parse XML verdict from model response.

        Handles both <verdict> and <block> XML tags.
        Defaults to BLOCK on parse failure (fail-closed).
        """
        # Try <verdict> tag first
        match = re.search(r"<verdict>(.*?)</verdict>", response, re.IGNORECASE)
        if match:
            val = match.group(1).strip().lower()
            if val == "allow":
                return ClassifierVerdict.ALLOW
            if val == "block":
                return ClassifierVerdict.BLOCK

        # Try <block> tag
        match = re.search(r"<block>(.*?)</block>", response, re.IGNORECASE)
        if match:
            val = match.group(1).strip().lower()
            if val in ("yes", "true"):
                return ClassifierVerdict.BLOCK
            if val in ("no", "false"):
                return ClassifierVerdict.ALLOW

        # Fail closed
        return ClassifierVerdict.BLOCK

    def _emit_telemetry(self, result: ClassifierResult) -> None:
        """Write classifier telemetry."""
        if not self._telemetry_dir:
            return

        from pathlib import Path

        event = {
            "event": "agnt_classifier_outcome",
            "timestamp": time.time(),
            "tool_id": result.tool_id,
            "verdict": result.verdict.value,
            "stage": result.stage,
            "fail_closed": result.fail_closed,
            "elapsed_ms": result.elapsed_ms,
        }

        path = Path(self._telemetry_dir) / "telemetry.jsonl"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as f:
                f.write(json.dumps(event) + "\n")
        except OSError:
            pass
