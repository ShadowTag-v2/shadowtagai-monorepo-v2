"""Base Agent class for the pinkln Agent Architecture System.

Agents are autonomous personas that use one or more Skills to execute tasks.
They inherit the "pnkln OS" philosophy and apply it to specific domains.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .base_skill import BaseSkill, SkillRegistry


class AgentType(Enum):
    """Types of agents in the system."""

    SIMPLE = "simple"  # Single-skill agent
    SUB_AGENT = "sub_agent"  # Specialized sub-agent
    DEEP_AGENT = "deep_agent"  # Orchestrating agent with memory/state
    MULTI_AGENT = "multi_agent"  # Collaborative agent system


@dataclass
class AgentMetadata:
    """Metadata for an agent."""

    name: str
    role: str
    agent_type: AgentType
    version: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Base class for all pinkln Agents.

    An Agent incorporates skills and executes tasks. Every agent:
    - Channels the "Steve Jobs" philosophy
    - Questions assumptions
    - Plans elegantly
    - Iterates ruthlessly
    - Applies the Boy Scout Rule
    - Ties outputs to wealth generation when applicable

    Agents have access to:
    - Memory for context persistence
    - Projects for workspaces
    - Extended thinking for deep reasoning
    - Multiple instance collaboration
    """

    def __init__(
        self,
        name: str,
        role: str,
        agent_type: AgentType = AgentType.SIMPLE,
        version: str = "1.0",
        description: str = "",
    ):
        """Initialize an agent.

        Args:
            name: Agent name
            role: Agent role/persona
            agent_type: Type of agent
            version: Version number
            description: Description of agent's purpose

        """
        self.metadata = AgentMetadata(
            name=name, role=role, agent_type=agent_type, version=version, description=description,
        )
        self.skills: list[BaseSkill] = []
        self.skill_registry = SkillRegistry()
        self.memory: dict[str, Any] = {}
        self.context: dict[str, Any] | None = None

    @abstractmethod
    async def execute(self, task: str, **kwargs) -> dict[str, Any]:
        """Execute a task.

        Args:
            task: Task description
            **kwargs: Additional parameters

        Returns:
            Result dictionary with:
            - output: Main result
            - metadata: Execution metadata
            - boy_scout: Boy Scout Rule metadata
            - wealth_insight: Revenue/monetization insights (when applicable)

        """

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent.

        Returns:
            Formatted system prompt

        """

    def add_skill(self, skill: BaseSkill):
        """Add a skill to this agent.

        Args:
            skill: Skill to add

        """
        self.skills.append(skill)
        self.skill_registry.register(skill)
        self.metadata.skills.append(skill.metadata.name)

    def get_skill(self, name: str) -> BaseSkill | None:
        """Get a skill by name."""
        return self.skill_registry.get(name)

    async def use_skill(self, skill_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """Use a specific skill.

        Args:
            skill_name: Name of skill to use
            input_data: Input data

        Returns:
            Skill execution result

        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        return await skill.execute(input_data, agent_context=self.context)

    def set_memory(self, key: str, value: Any):
        """Store value in memory."""
        self.memory[key] = value

    def get_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve value from memory."""
        return self.memory.get(key, default)

    def clear_memory(self):
        """Clear agent memory."""
        self.memory = {}

    def set_context(self, context: dict[str, Any]):
        """Set execution context."""
        self.context = context

    def reflect(self) -> dict[str, Any]:
        """Reflect on recent performance (RCR framework).

        Returns:
            Reflection dictionary

        """
        return {
            "assumptions_made": [],
            "decisions": [],
            "improvements": [],
            "boy_scout_actions": [],
        }

    def critique(self, _other_agent_output: dict[str, Any]) -> dict[str, Any]:
        """Critique another agent's output (for multi-agent systems).

        Args:
            other_agent_output: Output from another agent

        Returns:
            Critique dictionary

        """
        return {"strengths": [], "weaknesses": [], "suggestions": []}

    async def refine(self, output: dict[str, Any], critique: dict[str, Any]) -> dict[str, Any]:
        """Refine output based on critique.

        Args:
            output: Original output
            critique: Critique to address

        Returns:
            Refined output

        """
        # Base implementation - override in subclasses
        return output

    def get_metadata(self) -> dict[str, Any]:
        """Get agent metadata."""
        return {
            "name": self.metadata.name,
            "role": self.metadata.role,
            "type": self.metadata.agent_type.value,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "capabilities": self.metadata.capabilities,
            "skills": self.metadata.skills,
            "memory_size": len(self.memory),
        }

    def __repr__(self) -> str:
        return f"<Agent: {self.metadata.name} ({self.metadata.role}) v{self.metadata.version}>"


class SubAgent(BaseAgent):
    """Sub-Agent: Specialized agent under a parent agent.

    Sub-agents handle well-defined sub-tasks so the parent doesn't need to
    micromanage. Examples:
    - DataGathererSubAgent under ResearchAgent
    - UIEdgeCaseSubAgent under DesignAgent
    """

    def __init__(self, name: str, role: str, parent_agent: BaseAgent | None = None, **kwargs):
        """Initialize sub-agent."""
        super().__init__(name, role, agent_type=AgentType.SUB_AGENT, **kwargs)
        self.parent = parent_agent


class DeepAgent(BaseAgent):
    """Deep Agent: Higher-order agent architecture.

    Deep agents:
    - Orchestrate other agents/sub-agents
    - Use memory, tool integration, and state management
    - Perform multi-step, multi-tool workflows
    - Implement complex reasoning patterns
    """

    def __init__(self, name: str, role: str, **kwargs):
        """Initialize deep agent."""
        super().__init__(name, role, agent_type=AgentType.DEEP_AGENT, **kwargs)
        self.sub_agents: list[SubAgent] = []
        self.orchestration_state: dict[str, Any] = {}

    def add_sub_agent(self, sub_agent: SubAgent):
        """Add a sub-agent to this deep agent."""
        sub_agent.parent = self
        self.sub_agents.append(sub_agent)

    async def orchestrate(self, task: str, **kwargs) -> dict[str, Any]:
        """Orchestrate multiple sub-agents to complete a complex task.

        Args:
            task: Complex task description
            **kwargs: Additional parameters

        Returns:
            Orchestrated result

        """
        # Base orchestration logic - override in subclasses
        results = {}
        for sub_agent in self.sub_agents:
            result = await sub_agent.execute(task, **kwargs)
            results[sub_agent.metadata.name] = result

        return {"orchestrated_results": results, "state": self.orchestration_state}
