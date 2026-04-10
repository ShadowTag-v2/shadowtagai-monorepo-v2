import abc
from typing import Any
import sys
import os

# Add monorepo root to path to resolve `agents.jetski_agent`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class Agent(abc.ABC):
    @abc.abstractmethod
    def run(self, task: str) -> dict[str, Any]:
        pass


class SwarmOrchestrator:
    """
    The Hive Mind. Routes tasks to specialized agents.
    """

    def __init__(self):
        self.registry: dict[str, Agent] = {}
        # Pre-register Jetski Agent upon boot
        try:
            from agents.jetski_agent import JetskiBrowserAgent

            self.register("jetski", JetskiBrowserAgent())
        except ImportError as e:
            print(f"⚠️ [Swarm] Failed to load JetskiBrowserAgent: {e}")

    def register(self, name: str, agent: Agent):
        self.registry[name] = agent
        print(f"🐝 [Swarm] Agent registered: {name}")

    def route_and_execute(self, task: str) -> str:
        # Simple Keyword Routing to Jetski protocol if necessary
        if "browser" in task.lower() or "website" in task.lower() or "search" in task.lower():
            target = "jetski"
        else:
            target = "executive"

        print(f"🐝 [Swarm] Routing task to: {target.upper()}")

        if target not in self.registry:
            print(f"⚠️ [Swarm] {target} unavailable. Defaulting to general response.")
            return f"Fallback Execution for: {task}"

        return self.registry[target].run(task)
