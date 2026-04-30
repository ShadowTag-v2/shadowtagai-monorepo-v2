#!/usr/bin/env python3
"""
engage_troop_b.py
Mission: Operation Deep Build
Objective: Refactor `src/legacy-traps.ts` using Troop B (BuilderAgent).
"""

import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.n-autoresearch/Kosmos/BioAgents7 import n-autoresearch/Kosmos/BioAgents7, Task


def main():
    print("🚀 Initiating Operation Deep Build (Troop B)...")

    # 1. Initialize Kosmos
    brain = n-autoresearch/Kosmos/BioAgents7()

    # 2. Define Mission
    target_file = "src/legacy-traps.ts"
    if not os.path.exists(target_file):
        print(f"❌ Target file not found: {target_file}")
        return

    print(f"🎯 Target Acquired: {target_file}")

    # 3. Task: Builder Agent via Director Plan (or direct assignment)
    # We'll use direct assignment to test the specific agent flow first
    task = Task(
        agent_type="Builder",
        description="Refactor legacy code to comply with Styleguide.",
        context_slice=target_file,
    )

    # 4. Execute
    print("👨‍ Engaging Builder Agent...")
    # Select the first builder from the pool
    builder = brain.builder_agent_pool[0]

    # Pass the REPL for RLM capabilities (Echo Protocol)
    finding = builder.execute_task(task, repl=brain.repl)

    # 5. Output Result
    if finding.content:
        print("\n✅ Refactor Complete. Result Preview:")
        print("-" * 40)
        print(finding.content[:500] + "...\n[Truncated]")
        print("-" * 40)

        # Save to a new file for review
        output_file = "src/legacy-traps.refactored.ts"
        with open(output_file, "w") as f:
            f.write(finding.content)
        print(f"💾 Saved refactored code to: {output_file}")

    else:
        print("❌ Refactor Failed (No content returned).")


if __name__ == "__main__":
    main()
