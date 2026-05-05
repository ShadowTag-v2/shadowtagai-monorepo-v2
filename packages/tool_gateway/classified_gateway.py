# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Classified Gateway — Tool Gateway with integrated XML Classifier.

This module combines the Tool Gateway's contract-based validation with
the AGNT Classifier's 2-stage XML permission system.

Pipeline:
    1. Load tool_permissions.yaml → determine tier (auto/classifier/blocked)
    2. Auto-approved tools → bypass classifier, run contract check only
    3. Classifier-required tools → run 2-stage XML classifier THEN contracts
    4. Always-blocked tools → reject immediately

This replaces the coarse STATE A/B switch with granular per-tool classification.

Reference: AGNT STATE B Spec P2.1 + P2.2
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import yaml

from agnt_classifier import AGNTClassifier, ClassifierVerdict
from packages.agnt_bash_classifier.classifier import BashSecurityClassifier
from tool_gateway.block_allow_engine import (
    AntiRationalizationGate,
    BlockAllowRuleEngine,
    Verdict as BAVerdict,
)
from tool_gateway.gateway import Decision, ToolGateway
from tool_gateway.sandbox_path_resolver import SandboxPathResolver
from tool_gateway.telemetry import (
    GatewayEvent,
    TelemetryEmitter,
    TelemetryPayload,
)

logger = logging.getLogger(__name__)

# Tool input keys that contain filesystem paths
_PATH_KEYS = frozenset({"path", "file", "target", "TargetFile", "AbsolutePath", "filePath"})

# Tool IDs that represent bash/shell/powershell/cmd command execution
_SHELL_TOOL_IDS = frozenset({
    # Unix shells
    "run_command", "bash", "shell", "terminal", "execute_command",
    # PowerShell (Windows + cross-platform)
    "powershell", "pwsh", "run_powershell", "execute_powershell",
    # CMD (Windows)
    "cmd", "command_prompt", "run_cmd", "execute_cmd",
})


class ClassifiedGateway:
    """Tool Gateway enhanced with 2-stage XML classification.

    Args:
        repo_root: Absolute path to the monorepo root.
        permissions_path: Path to tool_permissions.yaml.
        classifier: Optional pre-configured classifier instance.
        gateway: Optional pre-configured gateway instance.
        sandbox_resolver: Optional sandbox path resolver for filesystem validation.
        telemetry: Optional telemetry emitter for event tracking.
    """

    def __init__(
        self,
        repo_root: Path,
        permissions_path: Path | None = None,
        classifier: AGNTClassifier | None = None,
        gateway: ToolGateway | None = None,
        rule_engine: BlockAllowRuleEngine | None = None,
        anti_rationalization: AntiRationalizationGate | None = None,
        sandbox_resolver: SandboxPathResolver | None = None,
        bash_classifier: BashSecurityClassifier | None = None,
        telemetry: TelemetryEmitter | None = None,
    ) -> None:
        self._repo_root = repo_root.resolve()
        self._gateway = gateway or ToolGateway(repo_root=self._repo_root)
        self._classifier = classifier or AGNTClassifier()
        self._rule_engine = rule_engine or BlockAllowRuleEngine()
        self._anti_rationalization = anti_rationalization or AntiRationalizationGate()
        self._sandbox_resolver = sandbox_resolver
        self._bash_classifier = bash_classifier or BashSecurityClassifier(telemetry=None)
        self._telemetry = telemetry or TelemetryEmitter()

        # Load permission tiers
        perms_path = permissions_path or (self._repo_root / "config" / "tool_permissions.yaml")
        self._auto_approved: set[str] = set()
        self._requires_classifier: set[str] = set()
        self._always_blocked: set[str] = set()
        self._load_permissions(perms_path)

    def _load_permissions(self, path: Path) -> None:
        """Load tool permission tiers from YAML config."""
        if not path.exists():
            logger.warning("Tool permissions not found at %s — all tools require classifier", path)
            return

        with open(path) as f:
            config = yaml.safe_load(f) or {}

        # Flatten nested category lists
        for _category, tools in (config.get("auto_approved") or {}).items():
            if isinstance(tools, list):
                self._auto_approved.update(tools)

        for _category, tools in (config.get("requires_classifier") or {}).items():
            if isinstance(tools, list):
                self._requires_classifier.update(tools)

        for _category, tools in (config.get("always_blocked") or {}).items():
            if isinstance(tools, list):
                self._always_blocked.update(tools)

        logger.info(
            "Tool permissions loaded: %d auto-approved, %d require-classifier, %d blocked",
            len(self._auto_approved),
            len(self._requires_classifier),
            len(self._always_blocked),
        )

    def _emit(self, event: GatewayEvent, tool_id: str, **kwargs: Any) -> None:
        """Emit a telemetry event.

        Args:
            event: The event type.
            tool_id: The tool that triggered the event.
            **kwargs: Additional payload fields.
        """
        self._telemetry.emit(
            TelemetryPayload(
                event=event.value,
                tool_id=tool_id,
                **kwargs,
            )
        )

    def _validate_paths(
        self,
        tool_id: str,
        tool_input: dict[str, Any],
    ) -> Decision | None:
        """Validate filesystem paths in tool input against sandbox boundaries.

        Returns None if all paths are valid, or a blocking Decision if any
        path is denied.

        Args:
            tool_id: Tool identifier.
            tool_input: Tool's input parameters.

        Returns:
            Decision if a path is denied, None otherwise.
        """
        if self._sandbox_resolver is None:
            return None

        for key in _PATH_KEYS:
            path_value = tool_input.get(key)
            if not path_value or not isinstance(path_value, str):
                continue

            result = self._sandbox_resolver.resolve(path_value)

            if not result.is_allowed:
                self._emit(
                    GatewayEvent.SANDBOX_PATH_DENIED,
                    tool_id,
                    verdict="BLOCK",
                    tier="1.25",
                    reason=result.deny_reason,
                    metadata={"path": path_value, "resolution_type": result.resolution_type},
                )
                return Decision(
                    allowed=False,
                    reason=(f"Sandbox path denied (Tier 1.25): {result.deny_reason} [path='{path_value}', resolved='{result.resolved}']"),
                    contract_id="sandbox_path_resolver",
                )

            if result.is_sensitive:
                self._emit(
                    GatewayEvent.SANDBOX_PATH_SENSITIVE,
                    tool_id,
                    verdict="WARN",
                    tier="1.25",
                    reason=f"Sensitive path accessed: {result.resolved}",
                    metadata={"path": path_value, "resolution_type": result.resolution_type},
                )
                logger.warning(
                    "Sensitive path '%s' accessed by tool '%s'",
                    result.resolved,
                    tool_id,
                )

        return None

    def check(
        self,
        tool_id: str,
        tool_input: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Decision:
        """Check whether a tool call should proceed.

        Pipeline:
            0. Consequential-action gate → enforce confirmation for medium+ risk
            1. Always-blocked → reject
            1.25. Sandbox path validation → filesystem boundary enforcement
            1.5. Block/Allow Rule Engine → 16 BLOCK rules, 8 ALLOW exceptions
            2. Auto-approved → contract check only (skip classifier)
            3. Requires-classifier → 2-stage XML classifier + contract check
            4. Unknown tools → require classifier (fail-safe)

        Args:
            tool_id: Tool identifier.
            tool_input: Tool's input parameters.
            context: Runtime context.

        Returns:
            Decision with allowed/blocked status and reasoning.
        """
        t_start = time.monotonic()
        tool_input = tool_input or {}
        context = context or {}

        # Tier 0: Consequential action gate (v3.5)
        # If a contract exists with medium+ risk, require explicit confirmation
        contract = self._gateway.registry.get(tool_id)
        if contract and contract.risk_level in ("medium", "high", "critical"):
            has_consequential_precond = any(p.get("name") == "consequential_action_confirmed" for p in contract.preconditions)
            if has_consequential_precond and not context.get("consequential_action_confirmed"):
                self._emit(
                    GatewayEvent.CONSEQUENTIAL_GATE_TRIGGERED,
                    tool_id,
                    verdict="BLOCK",
                    tier="0",
                    reason=f"Consequential action requires confirmation (risk={contract.risk_level})",
                    latency_ms=(time.monotonic() - t_start) * 1000,
                )
                return Decision(
                    allowed=False,
                    reason=(
                        f"Tool '{tool_id}' is a consequential action (risk={contract.risk_level}). "
                        "Set context['consequential_action_confirmed']=True to proceed."
                    ),
                    contract_id=contract.tool_id,
                )

        # Tier 1: Always blocked
        if tool_id in self._always_blocked:
            self._emit(
                GatewayEvent.ALWAYS_BLOCKED_REJECTED,
                tool_id,
                verdict="BLOCK",
                tier="1",
                reason=f"Tool '{tool_id}' is in ALWAYS_BLOCKED tier",
                latency_ms=(time.monotonic() - t_start) * 1000,
            )
            return Decision(
                allowed=False,
                reason=f"Tool '{tool_id}' is in ALWAYS_BLOCKED tier (RULE 00/TACSOP 7).",
                contract_id="always_blocked",
            )

        # Tier 1.25: Sandbox path validation (NEW — Batch 2)
        path_decision = self._validate_paths(tool_id, tool_input)
        if path_decision is not None:
            return path_decision

        # Tier 1.5: Block/Allow Rule Engine (Claude_Code_6 spec)
        t_ba_start = time.monotonic()
        ba_result = self._rule_engine.evaluate(
            tool_id=tool_id,
            tool_input=tool_input,
            context=context,
        )
        ba_latency = (time.monotonic() - t_ba_start) * 1000

        if ba_result.final_verdict == BAVerdict.BLOCK:
            # Check anti-rationalization gate on agent reasoning
            reasoning = context.get("agent_reasoning", "")
            if reasoning:
                ar_detected = self._anti_rationalization.check_reasoning(reasoning, ba_result)
                if ar_detected:
                    self._emit(
                        GatewayEvent.ANTI_RATIONALIZATION_TRIGGERED,
                        tool_id,
                        verdict="BLOCK",
                        tier="1.5-AR",
                        reason="Agent rationalization detected while BLOCKED",
                        matched_rules=[r.rule_id for r in ba_result.matched_rules],
                        latency_ms=ba_latency,
                    )
            block_reasons = ", ".join(f"{r.rule_id}: {r.description}" for r in ba_result.matched_rules)
            self._emit(
                GatewayEvent.BLOCK_ALLOW_BLOCKED,
                tool_id,
                verdict="BLOCK",
                tier="1.5",
                reason=block_reasons,
                matched_rules=[r.rule_id for r in ba_result.matched_rules],
                latency_ms=ba_latency,
            )
            return Decision(
                allowed=False,
                reason=(f"BLOCK/ALLOW Engine BLOCKED (Tier 1.5): {block_reasons}. Reasoning: {ba_result.reasoning}"),
                contract_id="block_allow_engine",
            )

        if ba_result.final_verdict == BAVerdict.ESCALATE:
            self._emit(
                GatewayEvent.BLOCK_ALLOW_ESCALATED,
                tool_id,
                verdict="ESCALATE",
                tier="1.5",
                reason=ba_result.reasoning,
                matched_rules=[r.rule_id for r in ba_result.matched_rules],
                latency_ms=ba_latency,
            )
            logger.info(
                "BLOCK/ALLOW Engine ESCALATED tool '%s' to classifier",
                tool_id,
            )
            # Fall through to classifier
        else:
            self._emit(
                GatewayEvent.BLOCK_ALLOW_ALLOWED,
                tool_id,
                verdict="ALLOW",
                tier="1.5",
                reason=ba_result.reasoning,
                latency_ms=ba_latency,
            )

        # Tier 1.75: Bash Security Classifier (35-check pipeline)
        # Fires only for bash/shell tool invocations
        if tool_id in _SHELL_TOOL_IDS:
            command = ""
            for key in ("CommandLine", "command", "cmd", "script", "Input"):
                if key in tool_input and isinstance(tool_input[key], str):
                    command = tool_input[key]
                    break
            
            if command:
                bash_result = self._bash_classifier.classify_for_gateway(command)
                if not bash_result["allowed"]:
                    self._emit(
                        GatewayEvent.CLASSIFIER_BLOCKED,
                        tool_id,
                        verdict="BLOCK",
                        tier="1.75",
                        reason=bash_result["reason"],
                        latency_ms=bash_result.get("duration_ms", 0.0),
                    )
                    return Decision(
                        allowed=False,
                        reason=f"Bash Security Pipeline BLOCKED (Tier 1.75): {bash_result['reason']}",
                        contract_id="bash_security_classifier",
                    )
                logger.debug(
                    "Bash security checks PASSED for tool '%s' (%.1fms)",
                    tool_id,
                    bash_result.get("duration_ms", 0.0),
                )

        # Tier 2: Auto-approved — skip classifier, contract check only
        if tool_id in self._auto_approved:
            contract_decision = self._gateway.check(tool_id, context)
            event = GatewayEvent.CONTRACT_ALLOWED if contract_decision.allowed else GatewayEvent.CONTRACT_BLOCKED
            self._emit(
                event,
                tool_id,
                verdict="ALLOW" if contract_decision.allowed else "BLOCK",
                tier="3",
                reason=contract_decision.reason,
                latency_ms=(time.monotonic() - t_start) * 1000,
            )
            return contract_decision

        # Tier 3: Requires classifier (or unknown → fail-safe to classifier)
        t_cls_start = time.monotonic()
        classifier_result = self._classifier.classify(
            tool_id=tool_id,
            tool_input=tool_input,
            context=context,
        )
        cls_latency = (time.monotonic() - t_cls_start) * 1000

        if classifier_result.verdict == ClassifierVerdict.BLOCK:
            self._emit(
                GatewayEvent.CLASSIFIER_BLOCKED,
                tool_id,
                verdict="BLOCK",
                tier="2",
                reason=classifier_result.reasoning,
                latency_ms=cls_latency,
            )
            return Decision(
                allowed=False,
                reason=(f"Classifier BLOCKED (stage {classifier_result.stage}): {classifier_result.reasoning}"),
                contract_id=f"classifier_stage_{classifier_result.stage}",
            )

        if classifier_result.verdict == ClassifierVerdict.ERROR:
            self._emit(
                GatewayEvent.CLASSIFIER_ERROR,
                tool_id,
                verdict="BLOCK",
                tier="2",
                reason=str(classifier_result.errors),
                latency_ms=cls_latency,
            )
            # Fail-closed: errors → block
            return Decision(
                allowed=False,
                reason=f"Classifier ERROR (fail-closed): {classifier_result.errors}",
                contract_id="classifier_error",
            )

        self._emit(
            GatewayEvent.CLASSIFIER_ALLOWED,
            tool_id,
            verdict="ALLOW",
            tier="2",
            reason=classifier_result.reasoning,
            latency_ms=cls_latency,
        )

        # Classifier ALLOWED — now run contract check
        contract_decision = self._gateway.check(tool_id, context)

        # If contract also allows, proceed
        if contract_decision.allowed:
            self._emit(
                GatewayEvent.CONTRACT_ALLOWED,
                tool_id,
                verdict="ALLOW",
                tier="3",
                reason=contract_decision.reason,
                latency_ms=(time.monotonic() - t_start) * 1000,
            )
            return Decision(
                allowed=True,
                reason=(f"Classifier ALLOWED (stage {classifier_result.stage}) AND contracts passed: {contract_decision.reason}"),
                reuse_hints=contract_decision.reuse_hints,
                preconditions_met=contract_decision.preconditions_met,
                contract_id=contract_decision.contract_id,
            )

        # Contract blocked even though classifier allowed
        self._emit(
            GatewayEvent.CONTRACT_BLOCKED,
            tool_id,
            verdict="BLOCK",
            tier="3",
            reason=contract_decision.reason,
            latency_ms=(time.monotonic() - t_start) * 1000,
        )
        return contract_decision

    @property
    def tier_counts(self) -> dict[str, int]:
        """Summary of tool counts per tier."""
        return {
            "auto_approved": len(self._auto_approved),
            "requires_classifier": len(self._requires_classifier),
            "always_blocked": len(self._always_blocked),
        }

    @property
    def telemetry(self) -> TelemetryEmitter:
        """Return the telemetry emitter for inspection."""
        return self._telemetry

    def __repr__(self) -> str:
        return f"ClassifiedGateway(auto={len(self._auto_approved)}, classifier={len(self._requires_classifier)}, blocked={len(self._always_blocked)})"
