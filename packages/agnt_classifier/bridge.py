# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Classified Gateway — Bridges agnt_classifier to tool execution pipeline.

Implements the pre/post-execution hook pattern from Claude Code's permission
system. Every tool call routes through the ClassifiedGateway:

    1. Pre-execution: classify → policy check → emit telemetry → allow/block
    2. Execution: delegate to tool handler
    3. Post-execution: emit outcome telemetry

The gateway is the single enforcement point for all tool permissions.
It integrates the TwoStageClassifier, MCP policy, and telemetry catalog.

Reference: Claude Code v2.1.91 channelPermissions.ts + config.ts
Reference: AGNT STATE B Spec P2.1
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable

from agnt_classifier.agnt_api import AGNTClassifier, ClassifierResult, ClassifierVerdict
from agnt_classifier.allowlist import is_allowlisted
from agnt_classifier.mcp_policy import (
    MCPPolicyConfig,
    MCPServerInfo,
    PolicyResult,
    get_default_agnt_policy,
    is_mcp_server_allowed_by_policy,
)

logger = logging.getLogger(__name__)


class GatewayAction(StrEnum):
    """Action taken by the gateway."""

    ALLOW_ALLOWLIST = "allow_allowlist"
    ALLOW_CLASSIFIER = "allow_classifier"
    ALLOW_POLICY = "allow_policy"
    BLOCK_CLASSIFIER = "block_classifier"
    BLOCK_POLICY = "block_policy"
    BLOCK_FAIL_CLOSED = "block_fail_closed"


@dataclass(frozen=True)
class GatewayResult:
    """Structured result from gateway evaluation."""

    allowed: bool
    action: GatewayAction
    tool_id: str
    reasoning: str = ""
    classifier_result: ClassifierResult | None = None
    policy_result: PolicyResult | None = None
    duration_ms: float = 0.0
    stage: int = 0


@dataclass
class GatewayTelemetry:
    """Accumulated telemetry from gateway decisions."""

    total_evaluations: int = 0
    total_allowed: int = 0
    total_blocked: int = 0
    total_fail_closed: int = 0
    allowlist_hits: int = 0
    classifier_allows: int = 0
    classifier_blocks: int = 0
    policy_blocks: int = 0
    avg_latency_ms: float = 0.0
    _latency_sum: float = 0.0

    def record(self, result: GatewayResult) -> None:
        """Record a gateway evaluation result."""
        self.total_evaluations += 1
        self._latency_sum += result.duration_ms
        self.avg_latency_ms = self._latency_sum / self.total_evaluations

        if result.allowed:
            self.total_allowed += 1
        else:
            self.total_blocked += 1

        match result.action:
            case GatewayAction.ALLOW_ALLOWLIST:
                self.allowlist_hits += 1
            case GatewayAction.ALLOW_CLASSIFIER:
                self.classifier_allows += 1
            case GatewayAction.BLOCK_CLASSIFIER:
                self.classifier_blocks += 1
            case GatewayAction.BLOCK_POLICY:
                self.policy_blocks += 1
            case GatewayAction.BLOCK_FAIL_CLOSED:
                self.total_fail_closed += 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize for telemetry emission."""
        return {
            "total_evaluations": self.total_evaluations,
            "total_allowed": self.total_allowed,
            "total_blocked": self.total_blocked,
            "total_fail_closed": self.total_fail_closed,
            "allowlist_hits": self.allowlist_hits,
            "classifier_allows": self.classifier_allows,
            "classifier_blocks": self.classifier_blocks,
            "policy_blocks": self.policy_blocks,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
        }


class ClassifiedGateway:
    """Central gateway for all tool execution permissions.

    Pipeline:
        1. Allowlist check (fast path — skip everything else)
        2. MCP policy check (enterprise denylist/allowlist)
        3. Two-stage classifier (YOLO bias → thinking escalation)
        4. Fail-closed on any error

    Usage::

        gateway = ClassifiedGateway()
        result = gateway.evaluate("run_command", {"CommandLine": "ls -la"})
        if result.allowed:
            # execute tool
        else:
            # block with reason
    """

    def __init__(
        self,
        policy: MCPPolicyConfig | None = None,
        classifier: AGNTClassifier | None = None,
        on_evaluation: Callable[[GatewayResult], None] | None = None,
    ) -> None:
        self._policy = policy or get_default_agnt_policy()
        self._classifier = classifier or AGNTClassifier()
        self._telemetry = GatewayTelemetry()
        self._on_evaluation = on_evaluation

    @property
    def telemetry(self) -> GatewayTelemetry:
        """Access accumulated telemetry."""
        return self._telemetry

    def evaluate(
        self,
        tool_id: str,
        tool_input: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        mcp_server_name: str | None = None,
    ) -> GatewayResult:
        """Evaluate a tool call through the full permission pipeline.

        Args:
            tool_id: The tool identifier (e.g., "run_command").
            tool_input: Tool-specific input parameters.
            context: Additional context for classification.
            mcp_server_name: If this is an MCP tool, the originating server name.

        Returns:
            GatewayResult with allowed/blocked status and reasoning.
        """
        start_time = time.perf_counter()
        tool_input = tool_input or {}

        try:
            result = self._evaluate_inner(
                tool_id, tool_input, context, mcp_server_name, start_time
            )
        except Exception as e:
            # P5.1: Fail-closed — any exception = BLOCK
            logger.error("Gateway evaluation error (fail-closed): %s", e)
            duration = (time.perf_counter() - start_time) * 1000
            result = GatewayResult(
                allowed=False,
                action=GatewayAction.BLOCK_FAIL_CLOSED,
                tool_id=tool_id,
                reasoning=f"Gateway error (fail-closed): {e}",
                duration_ms=duration,
            )

        self._telemetry.record(result)

        if self._on_evaluation:
            self._on_evaluation(result)

        return result

    def _evaluate_inner(
        self,
        tool_id: str,
        tool_input: dict[str, Any],
        context: dict[str, Any] | None,
        mcp_server_name: str | None,
        start_time: float,
    ) -> GatewayResult:
        """Inner evaluation logic — separated for fail-closed wrapping."""

        # ── Step 1: Allowlist fast path ──
        if is_allowlisted(tool_id):
            duration = (time.perf_counter() - start_time) * 1000
            return GatewayResult(
                allowed=True,
                action=GatewayAction.ALLOW_ALLOWLIST,
                tool_id=tool_id,
                reasoning=f"Tool '{tool_id}' is auto-approved (allowlist).",
                duration_ms=duration,
                stage=0,
            )

        # ── Step 2: MCP policy check (if tool is from an MCP server) ──
        if mcp_server_name:
            server_info = MCPServerInfo(name=mcp_server_name)
            policy_result = is_mcp_server_allowed_by_policy(
                mcp_server_name, server_info, self._policy
            )
            if not policy_result.allowed:
                duration = (time.perf_counter() - start_time) * 1000
                return GatewayResult(
                    allowed=False,
                    action=GatewayAction.BLOCK_POLICY,
                    tool_id=tool_id,
                    reasoning=policy_result.reason,
                    policy_result=policy_result,
                    duration_ms=duration,
                )

        # ── Step 3: Two-stage classifier ──
        classifier_result = self._classifier.classify(
            tool_id=tool_id,
            tool_input=tool_input,
            context=context,
        )

        duration = (time.perf_counter() - start_time) * 1000

        if classifier_result.verdict == ClassifierVerdict.ALLOW:
            return GatewayResult(
                allowed=True,
                action=GatewayAction.ALLOW_CLASSIFIER,
                tool_id=tool_id,
                reasoning=classifier_result.reasoning,
                classifier_result=classifier_result,
                duration_ms=duration,
                stage=classifier_result.stage,
            )

        if classifier_result.verdict == ClassifierVerdict.ERROR:
            return GatewayResult(
                allowed=False,
                action=GatewayAction.BLOCK_FAIL_CLOSED,
                tool_id=tool_id,
                reasoning=f"Classifier error (fail-closed): {classifier_result.errors}",
                classifier_result=classifier_result,
                duration_ms=duration,
            )

        return GatewayResult(
            allowed=False,
            action=GatewayAction.BLOCK_CLASSIFIER,
            tool_id=tool_id,
            reasoning=classifier_result.reasoning,
            classifier_result=classifier_result,
            duration_ms=duration,
            stage=classifier_result.stage,
        )

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the gateway state for diagnostics."""
        return {
            "policy": {
                "has_allowlist": self._policy.has_allowlist,
                "has_denylist": self._policy.has_denylist,
                "allowlist_count": (
                    len(self._policy.allowed_servers)
                    if self._policy.allowed_servers
                    else 0
                ),
                "denylist_count": len(self._policy.denied_servers),
            },
            "telemetry": self._telemetry.to_dict(),
        }
