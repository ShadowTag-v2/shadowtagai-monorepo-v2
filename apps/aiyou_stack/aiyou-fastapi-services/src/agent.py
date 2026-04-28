# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import time

from src.config.settings import settings
from src.memory import MemoryManager

# from agents.autoresearch import minion # Removed to use tools singleton
from src.tools.governance_tools import audit_action, get_governance_rules
from src.tools.swarm_tools import get_swarm_status, start_swarm, stop_swarm


class GeminiAgent:
    """A production-grade agent wrapper for Gemini 3.
    Implements the Think-Act-Reflect loop compliant with Antigravity Enterprise standards.
    Orchestrates the Flying minion swarm via Tools.
    """

    def __init__(self):
        self.settings = settings
        self.memory = MemoryManager()
        print(
            f"🤖 Initializing {self.settings.AGENT_NAME} with model {self.settings.GEMINI_MODEL_NAME}...",
        )

        # Swarm is now managed by src.tools.swarm_tools._SWARM

        # Register Tools (Conceptually - for LLM usage)
        self.available_tools = {
            "audit_action": audit_action,
            "get_governance_rules": get_governance_rules,
            "start_swarm": start_swarm,
            "stop_swarm": stop_swarm,
            "get_swarm_status": get_swarm_status,
        }

    def think(self, task: str) -> str:
        """Simulates the 'Deep Think' process of Gemini 3.
        Generates a plan artifact before execution.
        """
        print(f"\n🤔 <thought> Analyzing task: '{task}'")
        print("   - Checking mission context...")
        print("   - Identifying necessary tools...")
        print("   - Formulating execution plan...")

        # Generate Plan Artifact
        plan_path = f"{self.settings.ARTIFACTS_DIR}/plan_{int(time.time())}.md"
        with open(plan_path, "w") as f:
            f.write(f"# Plan for Task: {task}\n\n")
            f.write(f"## Context\n{self.memory.get_context()}\n\n")
            f.write(
                "## Execution Strategy\n1. Activate Flying minion Swarm\n2. Audit Governance Status\n3. Execute Revenue Actions",
            )

        print(f"   - Generated Artifact: {plan_path}")
        print("</thought>\n")

        return "Plan formulated."

    def act(self, task: str) -> str:
        """Executes the task using the Flying minion Swarm via Tools."""
        self.memory.add_entry("user", task)

        # 1. Think
        self.think(task)

        # 2. Activate Swarm
        print(f"🛠️  Activating Flying minion Swarm for: {task}")
        start_swarm()

        # Monitor for a few seconds (simulation of active management)
        time.sleep(5)

        # Get Status
        status = get_swarm_status()

        # 3. Generate Response
        response = f"Swarm Active. Status: {status}"
        print(f"   - Swarm Report: {response}")

        self.memory.add_entry("assistant", response, metadata=status)
        return response

    def reflect(self):
        """Review past actions to improve future performance."""
        history = self.memory.get_history()
        print(f"🧠 Reflecting on {len(history)} past interactions...")

        # Check if we need to stop the swarm based on history/mission (simplified)
        # In a real scenario, this would analyze the 'brakes' score from Judge 6

    def run(self, task: str):
        """Main entry point for the agent."""
        print(f"🚀 Starting Task: {task}")
        try:
            result = self.act(task)
            print(f"✅ Result: {result}")
            self.reflect()
        except KeyboardInterrupt:
            print("\n🛑 Stopping Swarm...")
            stop_swarm()


if __name__ == "__main__":
    agent = GeminiAgent()
    agent.run("Initialize Revenue Operations")
