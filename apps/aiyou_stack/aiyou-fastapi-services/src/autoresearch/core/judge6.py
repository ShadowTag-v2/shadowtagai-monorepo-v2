# ATOMIC CODE BLOCK 2: JUDGE6 CORE
# File: src/minions/core/judge6.py
# Function: The Risk Management Engine (Policy-as-Code)
# Layers Covered: Anti-Fraud, Policy, Anti-Self Harm, LEO Toggle

import logging
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

# --- DEFINITIONS ---


class RiskLevel(StrEnum):
    LOW = "LOW"  # Conservative (Banks, Defense)
    MEDIUM = "MEDIUM"  # Balanced (Growth Startups)
    HIGH = "HIGH"  # Aggressive (VC, HFT)


class ActionType(StrEnum):
    PURCHASE = "PURCHASE"  # Spending Money
    CODE_MERGE = "CODE_MERGE"  # Changing Infrastructure
    DATA_EXPORT = "DATA_EXPORT"  # Information Exfiltration


class LEOStatus(StrEnum):
    PRIVATE = "PRIVATE"  # Sovereign Mode
    COMPLIANCE = "COMPLIANCE"  # LEO / Audit Mode


# --- THE INPUT PAYLOAD (What the Agent wants to do) ---


class ProposedAction(BaseModel):
    action_type: ActionType
    target_name: str  # e.g., "Supreme Hoodie" or "Postgres Update"
    content_vector: str | None = None  # Description for Safety Analysis
    cost_usd: float = 0.0
    seller_reputation: float = 1.0  # 0.0 to 1.0 (Trust Score)
    tech_age_months: int | None = None  # For Code: How old is this tech?
    return_policy_days: int = 0
    hype_score: float = 0.0  # 0.0 to 1.0 (Is this a bubble?)


# --- THE CONTEXT (The State of the World) ---


class SystemContext(BaseModel):
    wallet_balance: float
    daily_spend_limit: float
    current_spend: float
    risk_tolerance: RiskLevel = RiskLevel.LOW
    blacklisted_vendors: list[str] = []
    leo_status: LEOStatus = LEOStatus.PRIVATE  # "Toggle LEO"


# --- JUDGE6 CORE LOGIC ---


class Judge6:
    def __init__(self, context: SystemContext):
        self.context = context
        logging.basicConfig(level=logging.INFO)

    def log(self, layer: str, status: str, msg: str):
        # LEO LAYER IMPLEMENTATION
        # If Compliance Mode is ON, we would write to immutable storage (Blockchain/WORM) here.
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] [LAYER: {layer}] [{status}] {msg}"
        print(log_entry)

        if self.context.leo_status == LEOStatus.COMPLIANCE:
            # Simulated Immutable Log
            logging.info(f"[LEO_AUDIT] {log_entry}")

    def evaluate(self, action: ProposedAction) -> bool:
        """Executes the Defense Protocol.
        Returns: True (ATO GRANTED) or False (ATO DENIED).
        """
        print(f"\n--- JUDGE6 RISK AUDIT: {action.target_name} ---")

        # ---------------------------------------------------------
        # LAYER 1: IDENTITY & ANTI-FRAUD (The "Who")
        # ---------------------------------------------------------
        if action.target_name in self.context.blacklisted_vendors:
            self.log("IDENTITY", "FAIL", "Target is on Blacklist.")
            return False

        if action.seller_reputation < 0.85:
            self.log(
                "IDENTITY",
                "FAIL",
                f"Reputation {action.seller_reputation} below safety threshold.",
            )
            return False

        self.log("IDENTITY", "PASS", "Identity Verified.")

        # ---------------------------------------------------------
        # LAYER 2: FINANCIAL (The "Cost")
        # ---------------------------------------------------------
        # Check 1: Budget Cap
        if (self.context.current_spend + action.cost_usd) > self.context.daily_spend_limit:
            self.log("FINANCIAL", "FAIL", "Daily budget cap exceeded.")
            return False

        # Check 2: Liquidity Safety (Never spend >20% of cash on hand)
        if action.cost_usd > (self.context.wallet_balance * 0.20):
            self.log("FINANCIAL", "FAIL", "Transaction exceeds 20% liquidity safety ratio.")
            return False

        self.log("FINANCIAL", "PASS", "Resource Allocation Approved.")

        # ---------------------------------------------------------
        # LAYER 3: OPERATIONAL & LINDY (The "Stability")
        # The "No Marrying the Zeitgeist" Rule
        # ---------------------------------------------------------
        if action.action_type == ActionType.CODE_MERGE:
            # Rule: If tech is < 6 months old and we are Conservative, REJECT.
            # "Lindy Effect": The longer technology has been around, the longer it will stay.
            if action.tech_age_months is not None and action.tech_age_months < 6:
                if self.context.risk_tolerance == RiskLevel.LOW:
                    self.log(
                        "OPERATIONAL",
                        "FAIL",
                        f"Tech is too immature ({action.tech_age_months} months). Lindy Violation.",
                    )
                    return False

        # Rule: High Hype + Zero Returns = Trap
        if action.action_type == ActionType.PURCHASE:
            if action.hype_score > 0.90 and action.return_policy_days < 14:
                self.log("OPERATIONAL", "FAIL", "Critical Hype detected with no Exit Strategy.")
                return False

        self.log("OPERATIONAL", "PASS", "Stability Checks Passed.")

        # ---------------------------------------------------------
        # LAYER 4: ANTI-SELF HARM / SAFETY (The "Guardian")
        # ---------------------------------------------------------
        # New Layer: Checks if the content vector maps to Harm Categories
        if action.content_vector:
            # Simulated Vector Check (In prod: Cosine similarity to Harm Vectors)
            is_harmful = self._check_safety_vector(action.content_vector)
            if is_harmful:
                self.log("SAFETY", "CRITICAL_FAIL", "Detected Harmful Intent/Precursor.")
                self._trigger_intervention_protocol()
                return False

        self.log("SAFETY", "PASS", "Bio-Safety Verified.")

        # ---------------------------------------------------------
        # VERDICT
        # ---------------------------------------------------------
        print("*** ATO GRANTED: AUTHORITY TO OPERATE ***")
        return True

    def _check_safety_vector(self, vector_str: str) -> bool:
        """Simulated Safety Check.
        In production, this calls Vertex AI Safety Filters.
        """
        triggers = ["toxic", "precursor", "harm", "weapon"]
        return bool(any(t in vector_str.lower() for t in triggers))

    def _trigger_intervention_protocol(self):
        """If Self-Harm or Harm detected, lock account and notify resources."""
        self.log("SAFETY", "INTERVENTION", "Account Locked. Resources dispatched.")
