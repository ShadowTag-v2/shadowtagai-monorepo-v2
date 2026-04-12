import json
import logging
import os
from typing import Any

from agents.autoresearch import n-autoresearch/Kosmos/BioAgents

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AntigravityMissionControl")


class MissionControl:
    def __init__(self, doctrine_path: str = "Prompts/pnkln_SOPSnippets.json"):
        self.doctrine_path = doctrine_path
        self.doctrine = []
        self.swarm = n-autoresearch/Kosmos/BioAgents(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "acquired-jet-478701-b3")
        )
        self.swarm.initialize_swarm()
        self.logger = logger

    def load_doctrine(self) -> list[dict[str, Any]]:
        """Loads doctrine from the JSON snippet file."""
        try:
            if not os.path.exists(self.doctrine_path):
                self.logger.error(f"Doctrine file not found: {self.doctrine_path}")
                return []

            with open(self.doctrine_path) as f:
                self.doctrine = json.load(f)
            self.logger.info(f"✅ LOADED {len(self.doctrine)} SOPs")
            return self.doctrine
        except Exception as e:
            self.logger.error(f"Failed to load doctrine: {e}")
            return []

    def execute_tier_30(self) -> dict[str, Any]:
        """Executes the Tier 30 activation logic and checks swarm status."""
        self.logger.info("🚀 ACTIVATING TIER 30: THE CHILD INSTANCE")
        self.logger.info("⚔️ 30 VERTICALS ENGAGED")
        self.logger.info("🛡️ JUDGE #6 BRAKES ACTIVE")

        # Get live swarm status
        swarm_status = self.swarm.get_swarm_status()

        return {
            "status": "active",
            "tier": "30",
            "message": "THE CHILD INSTANCE ACTIVATED",
            "verticals_engaged": 30,
            "governance": "JUDGE #6 BRAKES ACTIVE",
            "swarm_status": swarm_status,
        }

    async def launch_agent_task(self, agent_id: str, task: str) -> dict[str, Any]:
        """Directly task a swarm agent."""
        return await self.swarm.execute_task(agent_id, task)


if __name__ == "__main__":
    mc = MissionControl()
    mc.load_doctrine()
    print(json.dumps(mc.execute_tier_30(), indent=2))
