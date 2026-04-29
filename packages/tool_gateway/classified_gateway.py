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
from pathlib import Path
from typing import Any

import yaml

from packages.agnt_classifier import AGNTClassifier, ClassifierVerdict
from packages.tool_gateway.gateway import Decision, ToolGateway

logger = logging.getLogger(__name__)


class ClassifiedGateway:
    """Tool Gateway enhanced with 2-stage XML classification.

    Args:
        repo_root: Absolute path to the monorepo root.
        permissions_path: Path to tool_permissions.yaml.
        classifier: Optional pre-configured classifier instance.
        gateway: Optional pre-configured gateway instance.
    """

    def __init__(
        self,
        repo_root: Path,
        permissions_path: Path | None = None,
        classifier: AGNTClassifier | None = None,
        gateway: ToolGateway | None = None,
    ) -> None:
        self._repo_root = repo_root.resolve()
        self._gateway = gateway or ToolGateway(repo_root=self._repo_root)
        self._classifier = classifier or AGNTClassifier()

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

    def check(
        self,
        tool_id: str,
        tool_input: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Decision:
        """Check whether a tool call should proceed.

        Pipeline:
            1. Always-blocked → reject
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
        tool_input = tool_input or {}
        context = context or {}

        # Tier 1: Always blocked
        if tool_id in self._always_blocked:
            return Decision(
                allowed=False,
                reason=f"Tool '{tool_id}' is in ALWAYS_BLOCKED tier (RULE 00/TACSOP 7).",
                contract_id="always_blocked",
            )

        # Tier 2: Auto-approved — skip classifier, contract check only
        if tool_id in self._auto_approved:
            return self._gateway.check(tool_id, context)

        # Tier 3: Requires classifier (or unknown → fail-safe to classifier)
        classifier_result = self._classifier.classify(
            tool_id=tool_id,
            tool_input=tool_input,
            context=context,
        )

        if classifier_result.verdict == ClassifierVerdict.BLOCK:
            return Decision(
                allowed=False,
                reason=(f"Classifier BLOCKED (stage {classifier_result.stage}): {classifier_result.reasoning}"),
                contract_id=f"classifier_stage_{classifier_result.stage}",
            )

        if classifier_result.verdict == ClassifierVerdict.ERROR:
            # Fail-closed: errors → block
            return Decision(
                allowed=False,
                reason=f"Classifier ERROR (fail-closed): {classifier_result.errors}",
                contract_id="classifier_error",
            )

        # Classifier ALLOWED — now run contract check
        contract_decision = self._gateway.check(tool_id, context)

        # If contract also allows, proceed
        if contract_decision.allowed:
            return Decision(
                allowed=True,
                reason=(f"Classifier ALLOWED (stage {classifier_result.stage}) AND contracts passed: {contract_decision.reason}"),
                reuse_hints=contract_decision.reuse_hints,
                preconditions_met=contract_decision.preconditions_met,
                contract_id=contract_decision.contract_id,
            )

        # Contract blocked even though classifier allowed
        return contract_decision

    @property
    def tier_counts(self) -> dict[str, int]:
        """Summary of tool counts per tier."""
        return {
            "auto_approved": len(self._auto_approved),
            "requires_classifier": len(self._requires_classifier),
            "always_blocked": len(self._always_blocked),
        }

    def __repr__(self) -> str:
        return f"ClassifiedGateway(auto={len(self._auto_approved)}, classifier={len(self._requires_classifier)}, blocked={len(self._always_blocked)})"
