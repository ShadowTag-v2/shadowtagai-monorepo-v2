#!/usr/bin/env python3
import os
import sys

# Add the current directory to sys.path so we can import agents
sys.path.append(os.getcwd())

from agents.complexity_analyzer import ComplexityAnalyzer
from agents.cor2_brain import Cor2Brain
from agents.final_boss import FinalBoss
from agents.ide_swarm_manager import IDESwarmManager
from agents.tier_tracker import TierTracker

from agents.dashboard import SwarmDashboard
from agents.autoresearch import n-autoresearch/Kosmos/BioAgents
from agents.intake_handler import IntakeHandler
from agents.swarm_boss import SwarmBoss


def main():
    print("=" * 80)
    print("Initializing COR2.0 BRAIN ORCHESTRATOR :: MAXIMUM RESOURCE EXPLOITATION")
    print("=" * 80)
    print("Pipeline: Sonnet 4.5 → Cor2.0 → 10 Antigravity → 10 IDE → Claude Max → Git")
    print("Mission: Maximize free tier usage. Route by complexity. Generate wealth.")
    print("=" * 80)

    # Layer 1: Core Infrastructure
    print("\n///▞ LAYER 1 :: Core Infrastructure")
    tier_tracker = TierTracker()
    complexity_analyzer = ComplexityAnalyzer()
    print(
        f"///▞ Tier Tracker: Initialized {tier_tracker.get_stats()['total_endpoints']} provider endpoints"
    )
    print(f"///▞ Providers: {', '.join(tier_tracker.get_stats()['providers'])}")

    # Layer 2: Intake Handler (Sonnet 4.5 Interface)
    print("\n///▞ LAYER 2 :: Intake (Sonnet 4.5)")
    intake = IntakeHandler()
    intake.start()

    # Layer 3: Cor2.0 Brain (11th Antigravity - Arbitrator)
    print("\n///▞ LAYER 3 :: Cor2.0 Brain (11th Antigravity)")
    cor2_brain = Cor2Brain(complexity_analyzer=complexity_analyzer, tier_tracker=tier_tracker)

    # Layer 4: Flying n-autoresearch/Kosmos/BioAgents (10 Employee Antigravity Instances)
    print("\n///▞ LAYER 4 :: Flying n-autoresearch/Kosmos/BioAgents (10 Employee Antigravity)")
    autoresearch = n-autoresearch/Kosmos/BioAgents()

    # Layer 5: IDE Swarm Manager (5 Cursor + 5 VS Code)
    print("\n///▞ LAYER 5 :: IDE Swarm (5 Cursor + 5 VS Code)")
    ide_swarm = IDESwarmManager()

    # Layer 6: Final Boss (Claude Code Max)
    print("\n///▞ LAYER 6 :: Final Boss (Claude Code Max)")
    final_boss = FinalBoss()

    # Wire the pipeline
    print("\n///▞ WIRING PIPELINE...")
    intake.autoresearch = autoresearch
    cor2_brain.ide_swarm = ide_swarm
    ide_swarm.claude_code_max = final_boss

    # Start all components
    print("\n///▞ STARTING ALL COMPONENTS...")
    autoresearch.start()
    cor2_brain.start()
    ide_swarm.start()

    print("\n///▞ PIPELINE ACTIVE :: 31+ instances running")
    print("///▞ Dashboard starting...")

    # Initialize Dashboard with all layers
    boss = SwarmBoss()
    boss.receive_mission("Cor2.0 Brain Orchestration - Maximum Resource Exploitation")
    dashboard = SwarmDashboard(boss, autoresearch)

    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\n///▞ SHUTDOWN INITIATED...")
    finally:
        print("\n///▞ Stopping all components...")
        intake.stop()
        cor2_brain.stop()
        autoresearch.stop()
        ide_swarm.stop()

        # Print final statistics
        print("\n" + "=" * 80)
        print("FINAL STATISTICS")
        print("=" * 80)

        print("\n///▞ Cor2.0 Brain:")
        cor2_stats = cor2_brain.get_stats()
        print(f"  - Atoms Received: {cor2_stats['total_atoms_received']}")
        print(f"  - Atoms Routed: {cor2_stats['total_atoms_routed']}")
        print(f"  - Atoms Completed: {cor2_stats['total_atoms_completed']}")
        print(f"  - Tier Migrations: {cor2_stats['total_tier_migrations']}")

        print("\n///▞ Tier Tracker:")
        tier_stats = tier_tracker.get_stats()
        print(f"  - Total Requests: {tier_stats['total_requests']}")
        print(f"  - Free Tokens Consumed: {tier_stats['total_free_tokens_consumed']:,}")
        print(f"  - Cost Saved: ${tier_stats['total_cost_saved']:.2f}")

        print("\n///▞ IDE Swarm:")
        ide_stats = ide_swarm.get_stats()
        print(f"  - Total Tasks: {ide_stats['total_atoms_completed']}")
        ab_results = ide_stats["ab_test_results"]
        print(f"  - A/B Test Winner: {ab_results['winner'].upper()}")
        print(f"  - Cursor Avg: {ab_results['cursor_avg_time']:.2f}s")
        print(f"  - VS Code Avg: {ab_results['vscode_avg_time']:.2f}s")

        print("\n///▞ Shutdown Complete. Generational wealth maximized.")
        print("=" * 80)


if __name__ == "__main__":
    main()
