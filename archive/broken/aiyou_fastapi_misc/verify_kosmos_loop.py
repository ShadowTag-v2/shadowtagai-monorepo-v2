import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.agents.n-autoresearch/Kosmos/BioAgents7 import n-autoresearch/Kosmos/BioAgents7


def test_kosmos_loop_v2():
    print("🧪 [TEST] Initializing n-autoresearch/Kosmos/BioAgents7 (Kosmos v2)...")
    kosmos = n-autoresearch/Kosmos/BioAgents7()

    objective = "Analyze the impact of recursive self-improvement on AI coherence."
    print(f"🧪 [TEST] Objective: {objective}")

    # Run slightly longer search to trigger "Director Planning" output
    print("🧪 [TEST] Running Discovery Cycle (Max 3 cycles)...")
    kosmos.execute_discovery_cycle(objective, max_cycles=3)

    # Assertions for rich structure
    state = kosmos.world_model.get_context_snapshot()
    print(f"🧪 [TEST] Final State Snapshot: {state}")

    # Check for specific rich fields
    assert len(kosmos.world_model.findings_log) > 0, "No findings logged."

    # Check provenance
    first_finding = kosmos.world_model.findings_log[0]
    print(f"🧪 [TEST] Sample Finding Provenance: {first_finding.provenance}")
    assert first_finding.provenance.timestamp > 0
    assert first_finding.provenance.source_type in ["Literature", "Code"]

    print("✅ [TEST] PASSED: Kosmos v2 (Rich World Model) Verified.")


if __name__ == "__main__":
    test_kosmos_loop_v2()
