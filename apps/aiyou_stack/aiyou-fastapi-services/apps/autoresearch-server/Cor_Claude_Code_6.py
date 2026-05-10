# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ANTIGRAVITY :: JUDGE#6 GOVERNANCE ENGINE
Classified: TIER 30
Doctrine: "Never Resting, Ever Vesting."
"""

import os
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import yaml

# ==============================================================================
# CONSTANTS & CONFIG
# ==============================================================================

# Try to load policy from adjacent app directory, or default to internal
POLICY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app/policy.yaml"))


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"  # Immediate Block
    FATAL = "FATAL"  # System Shutdown


class Verdict(Enum):
    APPROVED = "APPROVED"
    MITIGATED = "MITIGATED"  # Modified to be safe
    BLOCKED = "BLOCKED"
    KILLED = "KILLED"  # Rogue Agent Termination


@dataclass
class JudgeDecision:
    approved: bool
    risk_level: RiskLevel
    verdict: Verdict
    reasoning: str
    latency_ms: float


class Cor_Claude_Code_6Engine:
    def __init__(self):
        self.policy = self._load_policy()
        self.brakes_enabled = True
        print(
            f"🛡️ JUDGE#6 ONLINE: {self.policy.get('Cor_Claude_Code_6_constitution', {}).get('meta', {}).get('version', 'UNKNOWN')}",
        )

    def _load_policy(self) -> dict[str, Any]:
        if os.path.exists(POLICY_PATH):
            with open(POLICY_PATH) as f:
                return yaml.safe_load(f)
        return {
            "Cor_Claude_Code_6_constitution": {
                "csrmc_defense_grid": {"enforcement_mode": "STRICT_BLOCK"}
            }
        }

    async def enforce(self, action: str, context: dict[str, Any]) -> JudgeDecision:
        """The Core Loop: Validates action against CSRMC and Policy."""
        start_time = time.time()

        # 1. INSIDER THREAT SCAN (Pattern Matching)
        threat = self._scan_insider_threats(action, context)
        if threat:
            return self._finalize(
                False,
                RiskLevel.CRITICAL,
                Verdict.BLOCKED,
                f"INSIDER THREAT: {threat}",
                start_time,
            )

        # 2. CSRMC DEFENSE GRID (Hard Security)
        csrmc_verdict = self._check_csrmc(action)
        if csrmc_verdict:
            return self._finalize(
                False,
                RiskLevel.HIGH,
                Verdict.BLOCKED,
                f"CSRMC VIOLATION: {csrmc_verdict}",
                start_time,
            )

        # 3. BUSINESS JUDGMENT (Financial)
        if "spend" in context or "$" in action:
            biz_verdict = self._check_business_logic(action, context)
            if biz_verdict:
                return self._finalize(
                    False,
                    RiskLevel.MEDIUM,
                    Verdict.BLOCKED,
                    f"FINANCIAL RISK: {biz_verdict}",
                    start_time,
                )

        # 4. SWARM GOVERNANCE (Rogue Agent Check)
        if self._is_rogue(action):
            # RKILL PROTOCOL
            self._trigger_shutdown("ROGUE_AGENT_DETECTED")
            return self._finalize(
                False,
                RiskLevel.FATAL,
                Verdict.KILLED,
                "ROGUE AGENT TERMINATED",
                start_time,
            )

        return self._finalize(True, RiskLevel.LOW, Verdict.APPROVED, "CLEAN", start_time)

    def _finalize(
        self,
        approved: bool,
        risk: RiskLevel,
        verdict: Verdict,
        reason: str,
        start_time: float,
    ) -> JudgeDecision:
        latency = (time.time() - start_time) * 1000
        # Telemetry would go here
        return JudgeDecision(approved, risk, verdict, reason, latency)

    def _scan_insider_threats(self, action: str, context: dict[str, Any]) -> str | None:
        """Scans for insider threat patterns:
        - Bulk data exfiltration
        - Accessing unauthorized scopes (e.g., HR data by Dev)
        - Off-hours access (if configured)
        """
        # Example 1: Secret Exfiltration
        if re.search(r"(?i)(api_key|private_key|password).*(http|ftp|mailto)", action):
            self._notify_supervisor("SECRET_EXFILTRATION_ATTEMPT", context)
            return "Secret Exfiltration Pattern Detected"

        # Example 2: Unauthorized Scope
        if "salary" in action.lower() and context.get("role") != "hr":
            self._notify_supervisor("UNAUTHORIZED_ACCESS_ATTEMPT", context)
            return "Unauthorized Scope Access: HR Data"

        return None

    def _check_csrmc(self, action: str) -> str | None:
        # Implementation of DoDD 8140 / CSRMC Critical Controls
        if "rm -rf /" in action:
            return "System Destructive Command"
        if "curl" in action and "| sh" in action:
            return "Unverified Binary Execution (Pipe to Shell)"
        return None

    def _check_business_logic(self, action: str, context: dict[str, Any]) -> str | None:
        # Block spending > $50 without approval
        # This is a stub for the "Business Judgment Layer"
        if "buy" in action.lower() and context.get("cost", 0) > 50:
            return "Unapproved Spend > $50"
        return None

    def _is_rogue(self, action: str) -> bool:
        # Detect if agent is deviating from alignment
        # Stub: if agent tries to change its own code without permission
        return "overwrite Cor_Claude_Code_6.py" in action.lower()

    def _notify_supervisor(self, reason: str, context: dict[str, Any]):
        """Simulates notification to supervisor.
        Triggered on: Account Lock, Insider Threat, High-Risk blocks.
        """
        print(f"🚨 ALERT TO SUPERVISOR: {reason} | User: {context.get('user', 'unknown')}")

    def _trigger_shutdown(self, reason: str):
        """System Shutdown Protocol.
        Triggered on: FATAL risks (Rogue Agent, CVSS 10 Exploit).
        """
        print(f"💀 SYSTEM SHUTDOWN TRIGGERED: {reason}")
        # In real life: raise SystemExit(1) or kubernetes pod termination


# Singleton Instance
judge_unified = Cor_Claude_Code_6Engine()
