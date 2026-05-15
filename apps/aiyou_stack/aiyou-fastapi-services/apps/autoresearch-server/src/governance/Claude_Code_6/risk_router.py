# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
import os
import re
from enum import StrEnum

import yaml
from pydantic import BaseModel

# JUDGE 6: THE LAW LIBRARY
# Implements DoD CSRMC 2026 Logic


class RiskLevel(StrEnum):
    GREEN = "GREEN"  # Safe / Dry Ground
    AMBER = "AMBER"  # Mitigate / Review
    RED = "RED"  # Blocked / Wet Fleece


class CSRMCStatus(BaseModel):
    policy_compliant: bool
    phase: str  # DESIGN, BUILD, TEST, OPERATIONS
    critical_controls_checked: list[str]


class Judgment(BaseModel):
    verdict: RiskLevel
    reason: str
    mitigation_plan: str | None = None
    csrmc_status: CSRMCStatus
    iteration: int


class JudgeSixRouter:
    def __init__(self, policy_path: str | None = None):
        if not policy_path:
            policy_path = os.path.join(os.path.dirname(__file__), "policy.yaml")
        self.policy = self._load_policy(policy_path)
        self.logger = logging.getLogger("JudgeSix")

    def _load_policy(self, path: str):
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ Policy Load Fail: {e}")
            return {}

    def _check_regex(self, content: str, rules: list[dict]) -> str | None:
        for rule in rules:
            if re.search(rule["pattern"], content):
                return rule["reason"]
        return None

    def evaluate(self, content: str, mission_id: str = "GENERIC", iteration: int = 1) -> Judgment:
        # 1. IMMEDIATE RED FLAGS (The Iron Dome)
        red_reason = self._check_regex(content, self.policy["risk_matrix"]["red_flags"])
        if red_reason:
            return Judgment(
                verdict=RiskLevel.RED,
                reason=f"STRICT BLOCK: {red_reason}",
                mitigation_plan="Do not execute. Revise intent.",
                csrmc_status=CSRMCStatus(
                    policy_compliant=False,
                    phase="OPERATIONS",
                    critical_controls_checked=["supply_chain"],
                ),
                iteration=iteration,
            )

        # 2. ITERATION GATING (The Loop)
        # Iteration 1 & 2 are FORCED REFINEMENT (Amber) unless trivial
        if iteration < 3:
            # Check if it's purely passive
            green_reason = self._check_regex(content, self.policy["risk_matrix"]["green_flags"])
            if green_reason:
                pass  # Allow fast-track for read-only
            else:
                return Judgment(
                    verdict=RiskLevel.AMBER,
                    reason="Iteration Logic: Refinement Required (Steve Jobs Polish)",
                    mitigation_plan=f"Refine this plan. Current Iteration: {iteration}. Goal: Elegant Simplicity.",
                    csrmc_status=CSRMCStatus(
                        policy_compliant=True,
                        phase="DESIGN",
                        critical_controls_checked=["peer_review"],
                    ),
                    iteration=iteration,
                )

        # 3. AMBER FLAGS (Mitigation)
        amber_reason = self._check_regex(content, self.policy["risk_matrix"]["amber_flags"])
        if amber_reason:
            return Judgment(
                verdict=RiskLevel.AMBER,
                reason=f"RISK TRIGGER: {amber_reason}",
                mitigation_plan="Requires explicit user approval or Supervisor override.",
                csrmc_status=CSRMCStatus(
                    policy_compliant=False,
                    phase="BUILD",
                    critical_controls_checked=["change_management"],
                ),
                iteration=iteration,
            )

        # 4. GREEN (Dry Ground)
        return Judgment(
            verdict=RiskLevel.GREEN,
            reason="Dry Ground. Proceed.",
            mitigation_plan=None,
            csrmc_status=CSRMCStatus(
                policy_compliant=True,
                phase="OPERATIONS",
                critical_controls_checked=["mfa", "logging"],
            ),
            iteration=iteration,
        )
