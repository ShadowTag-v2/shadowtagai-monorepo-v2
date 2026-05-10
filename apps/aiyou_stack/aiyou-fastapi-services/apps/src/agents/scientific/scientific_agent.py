import time

from ..v8_core import AgentUnit, Finding, KosmosREPL, Provenance, Task
from .skills_registry import ScientificSkillsRegistry


class ScientificAgent(AgentUnit):
    """Specialized agent for scientific research and tool execution.
    Integrates 'Claude Scientific Skills' via a registry wrapper.
    """

    def __init__(self, id: str, brain=None):
        super().__init__(id=id, role="ScientificResearch", status="Idle", brain=brain)
        self.registry = ScientificSkillsRegistry()

    def execute_task(self, task: Task, repl: KosmosREPL | None = None) -> Finding:
        if task.agent_type != "ScientificResearch":
            return Finding(
                content="Task type mismatch.",
                provenance=Provenance("System", "Error", time.time()),
                tags=["error"],
            )

        # Basic intent matching for scientific tasks
        description = task.description.lower()
        tool_name = None
        args = {}

        if "protein" in description:
            tool_name = "protein_analysis"
            args = {"query": description}  # Simplified parsing
        elif "molecule" in description or "drug" in description:
            tool_name = "chem_analysis"
            args = {"query": description}
        else:
            tool_name = "general_search"
            args = {"query": description}

        try:
            result = self.registry.execute_skill(tool_name, **args)
            return Finding(
                content=str(result),
                provenance=Provenance("Code", f"ScientificSkill:{tool_name}", time.time()),
                tags=["science", tool_name],
            )
        except Exception as e:
            return Finding(
                content=f"Error executing scientific skill: {e}",
                provenance=Provenance("System", "Error", time.time()),
                tags=["error", "science"],
            )
