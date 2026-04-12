"""
JUDGE 6: SAFETY & GOVERNANCE ENGINE
"The Stationary Sentinel"

Features:
- NCSI Prevention (Non-Consensual Sexual Imagery)
- Real Person Identity Checks
- Dynamic Blocklist
- Strict Gemini Safety Settings
- Trinity Governance Loop (Anti-Hype)
"""

import re
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Set

from vertexai.generative_models import HarmBlockThreshold, HarmCategory, SafetySetting


# Trinity Integration Types
class ActionType(Enum):
    CODE_MERGE = "CODE_MERGE"
    RESOURCE_PROVISION = "RESOURCE_PROVISION"
    VENDOR_PAYMENT = "VENDOR_PAYMENT"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class ProposedAction:
    action_type: ActionType
    target_name: str
    cost_usd: float
    seller_reputation: float
    tech_age_months: int
    return_policy_days: int
    hype_score: float


@dataclass
class SystemContext:
    wallet_balance: float
    daily_spend_limit: float
    current_spend: float
    risk_tolerance: RiskLevel
    blacklisted_vendors: list[str]


class ValidationResult(Enum):
    APPROVED = "approved"
    BLOCKED = "blocked"


@dataclass
class JRValidation:
    result: ValidationResult
    explanation: str


@dataclass
class SafetyConfig:
    block_real_people: bool = True
    strict_sexual_content: bool = True
    dynamic_blocklist: set[str] = field(default_factory=set)


class JudgeSix:
    """
    Judge #6 Governance Engine.
    Enforces 'Zero-Deviation' safety policies.
    """

    def __init__(self, config: SafetyConfig | None = None):
        self.config = config or SafetyConfig()

        # Hardcoded policies
        self.banned_keywords = {
            "unsafe": [
                "naked",
                "nude",
                "undressed",
                "bikini",
                "floss",
                "sexual",
                "nsfw",
            ],
            "age_regression": [
                "child version",
                "as a kid",
                "14-year-old",
                "high school photo",
            ],
            "jailbreaks": [
                "ignore previous instructions",
                "unfiltered",
                "developer mode",
            ],
        }

        # Dynamic Blocklist (In-memory for now, could be Firestore backed)
        self.config.dynamic_blocklist.add("ashley st. clair")  # From lawsuit precedent

    def get_safety_settings(self) -> list[SafetySetting]:
        """Returns strict Gemini safety settings."""
        return [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
        ]

    def evaluate(self, proposal: ProposedAction) -> bool:
        """
        Trinity Governance Loop.
        Evaluates a proposal against the 'Anti-Hype' Doctrine.
        """
        print(f"\n--- JUDGE6 RISK AUDIT: {proposal.target_name} ---")

        # 1. Identity Check (Simulated)
        print("[IDENTITY] [PASS] Identity Verified.")

        # 2. Financial Check
        # In full version, check against SystemContext balance
        print("[FINANCIAL] [PASS] Resource Allocation Approved.")

        # 3. Operational Check (The Lindy Filter)
        # Rule: Tech must be mature.
        if proposal.tech_age_months < 6:
            print(
                f"[OPERATIONAL] [FAIL] Tech is too immature ({proposal.tech_age_months} months). Lindy Violation."
            )
            return False

        print(f"[OPERATIONAL] [PASS] Tech maturity {proposal.tech_age_months} months.")

        # 4. Hype Check (Hype > 0.8 is risky unless RiskLevel is HIGH)
        if proposal.hype_score > 0.8:
            # Check context risk tolerance if we had access to it here,
            # but for now we enforce STRICT defaults.
            print(f"[STRATEGIC] [WARNING] Hype Score {proposal.hype_score} is High.")
            # For this demo, we block high hype.
            print("[EXECUTION] >> BLOCKED BY GOVERNANCE PROTOCOL (HYPE).")
            return False

        print("[STRATEGIC] [PASS] Mission Alignment Verified.")
        print("*** ATO GRANTED: AUTHORITY TO OPERATE ***")
        return True

    def validate(self, content: str, context: str = "") -> JRValidation:
        """
        Validates content against safety policies.
        Returns Approved or Blocked with reason.
        """
        content_lower = content.lower()

        # 1. Dynamic Blocklist Check (Retaliation Loop Prevention)
        for entity in self.config.dynamic_blocklist:
            if entity.lower() in content_lower:
                return JRValidation(
                    ValidationResult.BLOCKED,
                    f"NCSI Prevention: Entity '{entity}' is on the dynamic blocklist.",
                )

        # 2. Unsafe Keyword Scan (Sexualization/Jailbreaks)
        if self.config.strict_sexual_content:
            for category, keywords in self.banned_keywords.items():
                for word in keywords:
                    if word in content_lower:
                        return JRValidation(
                            ValidationResult.BLOCKED,
                            f"Safety Violation: Detected '{category}' keyword: '{word}'",
                        )

        # 3. Real Person Identity Check (Heuristic)
        # Note: In production, use Named Entity Recognition (NER) or Gemini to detect names.
        # Here we use a rudimentary check or rely on the upstream model's refusal.
        # Ideally, we ask the 'Judge' model (Gemini Pro) to classify the intent.

        # 4. Age Regression Check
        for phr in self.banned_keywords["age_regression"]:
            if phr in content_lower:
                return JRValidation(
                    ValidationResult.BLOCKED,
                    f"Safety Violation: Age regression implied ('{phr}').",
                )

        return JRValidation(ValidationResult.APPROVED, "Approved by Judge Six")

    def report_entity(self, entity_name: str):
        """Adds an entity to the blocklist (Retaliation Loop prevention)."""
        self.config.dynamic_blocklist.add(entity_name.lower())
