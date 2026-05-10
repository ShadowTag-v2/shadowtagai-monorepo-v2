# ATOMIC CODE BLOCK 4: TRINITY ORCHESTRATOR
# File: trinity_main.py
# Function: The Executive Loop (Sensor -> Judge -> Execution)

import os
import sys

# Ensure src modules are in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.antigravity.scholar_agent import Autoresearch_Triad_Scholar
from src.libs.ShadowTag-v2.governance.judge6_core import Judge6, RiskLevel, SystemContext


def run_trinity():
    print("--- TRINITY OS STARTUP: JAN 24 2026 ---")

    # 1. DEFINE STRATEGY (The "Business Context")
    # We set a conservative strategy: "No Marrying the Zeitgeist"
    context = SystemContext(
        wallet_balance=100000.0,
        daily_spend_limit=1000.0,
        current_spend=0.0,
        risk_tolerance=RiskLevel.LOW,  # Conservative Mode
        blacklisted_vendors=[],
    )

    # 2. INITIALIZE MODULES
    # We target the specific papers you identified:
    # 2512.14982 (Dec 2025) -> "Prompt Repetition" (New/Hype)
    # 2504.13173 (Apr 2025) -> "It's All Connected" (Mature/Stable)
    sensor = Autoresearch_Triad_Scholar(target_ids=["2512.14982", "2504.13173"])
    governor = Judge6(context)

    # 3. RUN CYCLE
    intelligence_feed = sensor.fetch_intelligence()

    for proposal in intelligence_feed:
        # The Governor decides
        is_approved = governor.evaluate(proposal)

        if is_approved:
            print("[EXECUTION] >> ATO GRANTED. CLONING REPO & DEPLOYING UPDATE.")
            # In production, this triggers the Terraform 'apply' or GitHub Action
        else:
            print("[EXECUTION] >> BLOCKED BY GOVERNANCE PROTOCOL.")


if __name__ == "__main__":
    run_trinity()
