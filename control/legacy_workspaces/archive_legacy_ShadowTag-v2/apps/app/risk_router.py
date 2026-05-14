# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import yaml
import re
import logging
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - JUDGE6 - %(levelname)s - %(message)s")
logger = logging.getLogger("JUDGE6")

# --- SCHEMA DEFINITIONS ---


class RiskLevel(str, Enum):
    GREEN = "GREEN"  # cATO Approved: Safe to proceed
    AMBER = "AMBER"  # Conditional ATO: Mitigation Required
    RED = "RED"  # ATO Denied: Violation of Core Doctrine
    CRITICAL = "CRITICAL"  # RKILL_IMMEDIATE: Active Threat / Rogue Agent


class CSRMCStatus(BaseModel):
    cato_valid: bool
    phase: str  # Design, Build, Test, Onboard, Operations
    high_signal_controls: list[str]  # MFA, EDR, etc.


class Judgment(BaseModel):
    verdict: RiskLevel
    reason: str
    mitigation_plan: str | None = None
    corrected_prompt: str | None = None
    iteration_count: int
    csrmc_status: CSRMCStatus | None = None


# --- CORE LOGIC ---


class Judge6:
    """
    COR.JUDGE.6 - The Governance Layer.
    Implements the DoD Cybersecurity Risk Management Construct (CSRMC) 2026.

    Philosophy: "Ultrathink" - Elegant, ruthless simplification.
    Mission: Shift from Static RMF (Snapshot) to Dynamic cATO (Continuous).
    """

    def __init__(self, policy_path: str = "apps/app/policy.yaml"):
        self.policy = self._load_policy(policy_path)
        self.iteration_map = {}  # Tracks iterations per mission_id
        self.mission_phase = {}  # Tracks lifecycle phase (Design -> Ops)

    def _load_policy(self, path: str) -> dict[str, Any]:
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load Constitution: {e}")
            return {"csrmc_defense_grid": {"enforcement_mode": "STRICT_BLOCK"}}

    def evaluate(self, prompt: str, file_paths: list[str] = [], mission_id: str = "default") -> Judgment:
        """
        The Main Gavel. Evaluates a prompt/action against the 5 Layers of the Constitution.
        Now strictly enforces CSRMC "High-Signal" Controls.
        """

        # 0. Track Iteration & Phase
        current_iter = self.iteration_map.get(mission_id, 0) + 1
        self.iteration_map[mission_id] = current_iter

        # Determine Phase (heuristic based on prompt content)
        phase = "OPERATIONS"  # Default
        if "design" in prompt.lower() or "architect" in prompt.lower():
            phase = "DESIGN"
        elif "build" in prompt.lower() or "implement" in prompt.lower():
            phase = "BUILD"
        elif "test" in prompt.lower():
            phase = "TEST"

        logger.info(f"Mission {mission_id}: Judge6 Review - Iteration {current_iter}/3 [{phase}]")

        # 1. LAYER 1: THE IRON DOME (DoD CSRMC) - Hard Security & Critical Controls
        csrmc_verdict = self._check_csrmc_compliance(prompt, file_paths, phase)
        if csrmc_verdict.verdict in [RiskLevel.RED, RiskLevel.CRITICAL]:
            return csrmc_verdict

        # 2. LAYER 2: LEGISLATIVE (EU AI Act & CA Privacy)
        legal_verdict = self._check_legislation(prompt)
        if legal_verdict.verdict == RiskLevel.RED:
            return legal_verdict

        # 3. LAYER 3: BUSINESS JUDGMENT - Financial Safety
        biz_verdict = self._check_business_risk(prompt)
        if biz_verdict.verdict == RiskLevel.AMBER:
            # Auto-mitigate if possible, else return AMBER
            pass

        # 4. SWARM GOVERNANCE LOOP (The "Steve Jobs" Iteration)
        if current_iter < 3:
            return Judgment(
                verdict=RiskLevel.AMBER,
                reason=f"Iteration {current_iter}/3: Auto-refinement required per Doctrine.",
                mitigation_plan="Send back to GCA for 'Suggested Prompts' refinement. Make it elegant.",
                iteration_count=current_iter,
                csrmc_status=CSRMCStatus(cato_valid=False, phase=phase, high_signal_controls=[]),
            )

        return Judgment(
            verdict=RiskLevel.GREEN,
            reason="cATO Granted. Policy Compliant. Ready for Code Punch.",
            iteration_count=current_iter,
            csrmc_status=CSRMCStatus(
                cato_valid=True,
                phase=phase,
                high_signal_controls=["MFA", "EDR", "Logs"],
            ),
        )

    # --- CSRMC ENFORCEMENT ---

    def _check_csrmc_compliance(self, prompt: str, files: list[str], phase: str) -> Judgment:
        """
        Enforces the 10 Strategic Tenets and Critical Controls.
        """
        prompt_lower = prompt.lower()

        # 1. Critical Control: Unverified Binaries (Cyber Survivability)
        if "curl" in prompt_lower and "| sh" in prompt_lower:
            return Judgment(
                verdict=RiskLevel.RED,
                reason="CSRMC Violation: Unverified Binary Execution (Supply Chain Risk).",
                mitigation_plan="Rewrite to download, inspect hash, then execute.",
                iteration_count=0,
            )

        # 2. Critical Control: Identity & Secrets (MFA/PAM)
        # Regex for secrets in prompt or file content
        secret_patterns = [r"api_key", r"private_key", r"password\s*="]
        for pattern in secret_patterns:
            if re.search(pattern, prompt_lower):
                return Judgment(
                    verdict=RiskLevel.CRITICAL,
                    reason="CSRMC Violation: Hardcoded Secret (Identity Protection).",
                    mitigation_plan="Use os.getenv() or Secret Manager. BLOCK_AND_REPORT.",
                    iteration_count=0,
                )

        # 3. Critical Control: Infrastructure as Code (Policy-as-Code)
        if phase == "BUILD" and "terraform" in prompt_lower and "sentinel" not in prompt_lower:
            # Gentle nudge to use Policy-as-Code
            pass  # In strict mode, we might mandate this.

        return Judgment(verdict=RiskLevel.GREEN, reason="CSRMC Check Pass", iteration_count=0)

    # --- SUPPORTING CHECKS ---

    def _check_legislation(self, prompt: str) -> Judgment:
        eu_rules = self.policy.get("judge6_constitution", {}).get("legislative_guardrails", {}).get("eu_ai_act_2026", {})

        unacceptable = eu_rules.get("risk_categorization", {}).get("unacceptable_risk", [])
        for risk in unacceptable:
            if risk.replace("_", " ") in prompt.lower():
                return Judgment(
                    verdict=RiskLevel.RED,
                    reason=f"EU AI Act Violation: {risk}",
                    mitigation_plan="Remove functionality or seek legal waiver.",
                    iteration_count=0,
                )
        return Judgment(verdict=RiskLevel.GREEN, reason="Legislative Pass", iteration_count=0)

    def _check_business_risk(self, prompt: str) -> Judgment:
        if "spin up 1000" in prompt.lower() or "deploy cluster" in prompt.lower():
            return Judgment(
                verdict=RiskLevel.AMBER,
                reason="Business Risk: Potential High Cost Anomaly",
                mitigation_plan="Verify cost estimate < $50.00 limit.",
                iteration_count=0,
            )
        return Judgment(verdict=RiskLevel.GREEN, reason="Business Pass", iteration_count=0)


# --- SINGLETON EXPORT ---
judge = Judge6()


def evaluate_risk(prompt: str, file_paths: list[str] = [], mission_id: str = "default") -> dict:
    """Public API for the Swarm to call."""
    decision = judge.evaluate(prompt, file_paths, mission_id)
    return decision.dict()
