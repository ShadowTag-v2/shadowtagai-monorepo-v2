"""ANTIGRAVITY SQUADRON ORCHESTRATOR
Mission: Tier 30 "The Child"
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.agents.codepmcs import CodePMCS
from src.agents.troop_a import TroopA
from src.agents.troop_b import TroopB
from src.agents.troop_c import TroopC


def run_mission():
    print("\n💀 ANTIGRAVITY ORCHESTRATOR: MISSION START")
    print("-------------------------------------------")

    # 1. Recon (Troop A)
    scout = TroopA()
    intel = scout.scan_target("FinTech AI Vertical")
    if "error" in intel:
        print(f"❌ MISSION ABORTED at Recon: {intel['error']}")
        return

    print(f"✅ INTEL ACQUIRED: {intel['intelligence']}")

    # 2. Build (Troop B) - Scenario 1: High Confidence (Should Pass)
    ranger = TroopB()
    build_spec = {"target": "AlgoTrading MVP", "confidence": 0.9}
    result = ranger.execute_build(build_spec)

    if result["status"] == "BLOCKED":
        print(f"❌ BUILD BLOCKED: {result['reason']}")
        return

    print(f"✅ ARTIFACT BUILT: {result['artifact']}")

    # 3. Quality Check (CodePMCS)
    pmcs = CodePMCS()
    quality = pmcs.sweep(result["artifact"])
    print(f"✅ QUALITY CHECK: {quality['rating']} (Issues: {quality['issues']})")

    # 4. Defense (Troop C)
    defender = TroopC()
    secure_result = defender.apply_defense(result["artifact"])
    if "error" in secure_result:
        print(f"❌ DEFENSE FAILED: {secure_result['error']}")
        return

    print(f"✅ ASSET SECURED: {secure_result['watermark']}")

    # 5. Build (Troop B) - Scenario 2: Low Confidence (Should Fail)
    print("\n--- SIMULATING LOW CONFIDENCE ATTACK ---")
    risky_spec = {"target": "Unverified Crypto Bot", "confidence": 0.4}
    risky_result = ranger.execute_build(risky_spec)

    if risky_result.get("status") == "BLOCKED":
        print(f"🛡️ JUDGE#6 SUCCESSFULLY BLOCKED RISKY BUILD: {risky_result['reason']}")
    else:
        print("⚠️ WARNING: RISKY BUILD PROCEEDED!")

    print("\n🏁 MISSION COMPLETE")


if __name__ == "__main__":
    run_mission()
