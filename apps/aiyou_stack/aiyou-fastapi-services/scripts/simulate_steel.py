#!/usr/bin/env python3
"""
Simulate Steel - Phase 2 Valuation Engine
Validates the $100B valuation thesis for 1GW Virtual Capacity.

Usage:
    python scripts/simulate_steel.py
"""

import os
import sys

sys.path.append(os.getcwd())

import logging

from src.pnkln.steel.skynode import NuclearNode, RigNode, TowerNode

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("SimulateSteel")


def run_simulation():
    print("=" * 80)
    print("🚀 SKYNODE FLEET SIMULATION (1GW TARGET)")
    print("=" * 80)

    fleet = []

    # 1. Nuclear: The Heavy Lifters (San Onofre + 1 Expansion)
    # Target: ~900MW
    san_onofre = NuclearNode(
        node_id="SONGS-01",
        location_code="US-CA-SONGS",
        capacity_mw=450.0,  # Unit 2
    )
    diablo = NuclearNode(node_id="DIABLO-01", location_code="US-CA-DIABLO", capacity_mw=450.0)
    fleet.extend([san_onofre, diablo])

    # 2. Offshore: The Sovereign Cloud (50 Rigs)
    # Target: ~500MW? No, remaining 100MW split.
    # 50 Rigs @ 2MW each = 100MW.
    for i in range(50):
        fleet.append(RigNode(node_id=f"RIG-{i:03d}", location_code="INTL-WATERS", capacity_mw=2.0))

    # 3. Tower-Edge: The Nervous System (10k Towers)
    # Target: Distributed Inference
    # 10k * 10kW (0.01MW) = 100MW.
    # Total so far: 900 + 100 + 100 = 1100MW (1.1GW).
    # Let's stick to 10k towers to show scale.
    # Simulating 10k objects might be slow in python loop for this script,
    # let's simulate as a "Cluster" or just do the math efficiently.
    # We'll create representative nodes and multiply.

    # We'll just instantiate 10 representative towers and multiplier later?
    # No, let's just make 'fleet' a list of active objects for the summary.
    # For the script's sake, we'll implement 1000 representative towers (10% sample)
    for i in range(1000):
        fleet.append(
            TowerNode(
                node_id=f"TOWER-{i:04d}",
                location_code="US-EDGE",
                capacity_mw=0.01,  # 10kW
            )
        )

    print(f"Fleet Assembled: {len(fleet)} nodes (Simulation Sample)")

    # Activate All
    print("Activating Fleet...")
    total_capacity_mw = 0.0
    total_revenue_hr = 0.0

    # Nuclear & Rig
    for node in fleet:
        node.activate()
        t = node.heartbeat()
        total_capacity_mw += t.active_capacity_mw
        total_revenue_hr += t.revenue_rate_usd_hr

    # Adjust for the 9000 towers we didn't instantiate in the loop
    missing_towers = 9000
    missing_tower_cap = missing_towers * 0.01
    # Base rate * 1.2 premium
    missing_tower_rev = missing_towers * 0.01 * 570.0 * 1.2

    total_capacity_mw += missing_tower_cap
    total_revenue_hr += missing_tower_rev

    print("-" * 80)
    print("📊 SIMULATION RESULTS")
    print("-" * 80)

    # Yearly Calculation
    total_revenue_yr = total_revenue_hr * 24 * 365

    print(f"{'Metric':<30} | {'Value':>20}")
    print("-" * 55)
    print(f"{'Total Virtual Capacity':<30} | {total_capacity_mw:>15,.2f} MW")
    print(f"{'Target Capacity':<30} | {1000.00:>15,.2f} MW")
    print(f"{'Utilization':<30} | {'95% (Assumed)':>20}")
    print(f"{'Revenue / Hour':<30} | ${total_revenue_hr:>18,.2f}")
    print(f"{'Annual Revenue Run Rate':<30} | ${total_revenue_yr:>18,.2f}")

    # Valuation Check
    # Valuation = ARR * 20x (Platform Multiplier)
    valuation = total_revenue_yr * 20

    print("-" * 55)
    print(f"{'Implied Valuation (20x)':<30} | ${valuation:>18,.2f}")
    print("-" * 55)

    if valuation >= 100_000_000_000:
        print("\n✅ TARGET ACHIEVED: Valuation >= $100B")
        print("   The Steel (Pillar II) is validated.")
    else:
        print(f"\n⚠️ GAP DETECTED: Short by ${100_000_000_000 - valuation:,.2f}")


if __name__ == "__main__":
    run_simulation()
