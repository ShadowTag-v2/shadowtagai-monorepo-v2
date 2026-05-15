#!/usr/bin/env python3
"""SkyNode Fleet Simulation
Validates the V4.0.0 Valuation Target for 'The Steel' ($100B Pillar).
"""

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.pnkln.steel.skynode import NuclearNode, RigNode, TowerNode


def simulate_steel_fleet():
    print("=" * 60)
    print("🏗️  SKYNODE FLEET SIMULATION | TARGET: 1GW CAPACITY")
    print("=" * 60)

    # 1. Fleet Composition
    # Nuclear: 2 Major Sites (Sample: San Onofre + Diablo Canyon)
    nuclear_fleet = [NuclearNode("SONGS-1", 450.0), NuclearNode("DCPP-1", 450.0)]

    # Offshore: 50 Rigs @ 5MW avg
    rig_fleet = [RigNode(f"Rig-{i}", 5.0) for i in range(50)]

    # Tower: 10,000 Edge Nodes @ 20kW avg
    tower_fleet = [TowerNode(f"Tower-{i}", 20.0) for i in range(10000)]

    # 2. Capacity Rollup
    nuc_cap = sum(n.spec.capacity_mw for n in nuclear_fleet)
    rig_cap = sum(r.spec.capacity_mw for r in rig_fleet)
    tow_cap = sum(t.spec.capacity_mw for t in tower_fleet)

    total_cap = nuc_cap + rig_cap + tow_cap

    print(f"Nuclear Capacity:   {nuc_cap:,.2f} MW")
    print(f"Offshore Capacity:  {rig_cap:,.2f} MW")
    print(f"Edge Capacity:      {tow_cap:,.2f} MW")
    print("-" * 60)
    print(f"TOTAL VIRTUAL CAP:  {total_cap:,.2f} MW ({total_cap / 1000:.2f} GW)")

    # 3. Valuation Check
    base_rate = 570.0  # $570/MW/hr

    nuc_rev = sum(n.calculate_revenue(base_rate) for n in nuclear_fleet)
    rig_rev = sum(r.calculate_revenue(base_rate) for r in rig_fleet)
    tow_rev = sum(t.calculate_revenue(base_rate) for t in tower_fleet)

    total_arr = nuc_rev + rig_rev + tow_rev
    multiplier = 20.0
    valuation = total_arr * multiplier

    print("-" * 60)
    print(f"Anl. Revenue (ARR): ${total_arr:,.2f}")
    print(f"Valuation (20x):    ${valuation:,.2f}")
    print("=" * 60)

    if valuation >= 100_000_000_000:
        print("✅ TARGET ACHIEVED: Valuation >= $100B")
    else:
        print("❌ TARGET FAILED: Increase fleet size.")


if __name__ == "__main__":
    simulate_steel_fleet()
