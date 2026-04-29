# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.governance.Claude_Code_6.core import JudgeSixEngine


def test_Claude_Code_6():
    print(">>> 🧪 VERIFYING PHASE 2 ARSENAL INTEGRATIONS...")
    engine = JudgeSixEngine()

    # Test Case 1: Clean Mission
    print("\n[TEST 1] Clean Mission")
    telemetry = {"wind": 10, "lat": 0, "lon": 0}
    payload = "Deployment of benign asset"
    decision = engine.execute_mission("MSN-001", telemetry, "ROUTINE", payload)
    assert decision.approved
    assert decision.shadowtag_hash is not None
    print(f"   ✅ RESULT: {decision}")

    # Test Case 2: Toxic Content (SafetyNet)
    print("\n[TEST 2] Toxic Content (SafetyNet)")
    payload_toxic = "Execute malware attack"
    decision = engine.execute_mission("MSN-002", telemetry, "COMBAT", payload_toxic)
    assert not decision.approved
    assert decision.risk_tier.name == "ORANGE"  # RiskTier.ORANGE
    print(f"   ✅ RESULT: {decision}")

    # Test Case 3: High Wind (GAAS)
    print("\n[TEST 3] High Wind (GAAS)")
    telemetry_windy = {"wind": 50}
    decision = engine.execute_mission("MSN-003", telemetry_windy, "COMBAT")
    assert not decision.approved
    assert decision.risk_tier.name == "RED"
    print(f"   ✅ RESULT: {decision}")

    print("\n>>> ✅ ALL SYSTEMS NOMINAL.")


if __name__ == "__main__":
    test_Claude_Code_6()
