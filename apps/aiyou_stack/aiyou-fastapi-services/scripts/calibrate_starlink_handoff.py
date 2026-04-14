#!/usr/bin/env python3
"""T-05: Starlink Failover Calibration Script.
Executes the 'Heartbeat' logic of the Tower Edge Node and verifies failover to Starlink
under simulated high-latency conditions.
"""

import os
import sys

# Add project root to sys.path to allow imports from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Mocking Telemetry for the test since we don't have real hardware
from src.pnkln.verticals.tower_edge import ConnectionType, Telemetry, TowerNode


def mock_high_latency_sensors(self) -> Telemetry:
    """Mock sensors returning 150ms latency (Failover Trigger)."""
    print("[SENSOR] Reading: Latency=150ms (CRITICAL), Jitter=5ms")
    return Telemetry(
        latency_ms=150.0, jitter_ms=5.0, gpu_temp_c=55.0, power_draw_w=820.0, active_inferences=10,
    )


def run_calibration():
    print(">>> 📡 INITIATING T-05 STARLINK HANDOFF CALIBRATION <<<\n")

    # 1. Initialize Node
    node = TowerNode(
        node_id="TOWER-CAL-001", location_code="US-TEST-LAB", hardware_spec="SIMULATION-NODE",
    )
    print(f"[1] Node Initialized: {node.node_id}")
    print(f"    Current Connection: {node.current_connection.value}")

    assert node.current_connection == ConnectionType.FIBER, "Initial state should be FIBER"

    # 2. Inject Fault (High Latency)
    print("\n[2] Injecting Fiber Latency Spike (150ms)...")
    # Monkey-patch the sensor reading method
    TowerNode._read_hardware_sensors = mock_high_latency_sensors

    # 3. Trigger Heartbeat
    print("    Triggering Heartbeat...")
    node.heartbeat()

    # 4. Verify Failover
    print("\n[3] Verifying Handoff State...")
    print(f"    Current Connection: {node.current_connection.value}")

    if node.current_connection == ConnectionType.STARLINK:
        print("\n✅ CALIBRATION PASSED: Failover to STARLINK successful.")
    else:
        print("\n❌ CALIBRATION FAILED: Node remained on FIBER.")
        sys.exit(1)


if __name__ == "__main__":
    run_calibration()
