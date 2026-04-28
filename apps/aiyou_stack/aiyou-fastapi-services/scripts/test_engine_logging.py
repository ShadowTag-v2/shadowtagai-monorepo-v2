# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.pnkln_agents.core.jr_engine import JREngine, Purpose, Reason


def test_logging():
    print("Testing JR Engine Logging...")
    engine = JREngine()

    purpose = Purpose(
        intent="Test Scribe Integration",
        business_value="Verify logging",
        customer_id="Test-User",
        cost_estimate_usd=0.01,
        expected_outcome="Log entry in tape",
    )

    reasons = [
        Reason(
            justification="Testing system integrity",
            risk_probability=0.1,
            risk_severity=0.1,
            mitigation_strategy="None",
        ),
    ]

    print("running validate()...")
    decision = engine.validate(purpose, reasons)
    print(f"Validation Result: Approved={decision.approved}")

    # Check tape
    tape_path = os.path.expanduser("~/antigravity-flattened/universal_tape.jsonl")
    print(f"Checking tape at {tape_path}...")
    with open(tape_path) as f:
        lines = f.readlines()
        last_line = lines[-1]
        print(f"Last Log: {last_line}")

    if "Test Scribe Integration" in last_line or "access_control" in last_line:
        print("✅ SUCCESS: Event logged.")
    else:
        print("❌ FAILURE: Event not found.")


if __name__ == "__main__":
    test_logging()
