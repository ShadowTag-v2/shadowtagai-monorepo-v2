"""
Vertex AI Agents Registry
Python implementation for loading and managing AI agents
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Agent:
    """Represents an AI agent configuration"""

    id: str
    name: str
    category: str
    description: str
    icon: str
    version: str
    system_prompt: str
    capabilities: list[str]
    use_cases: list[str]
    example_prompts: list[str]
    tools: list[str]
    model: str
    temperature: float
    max_tokens: int
    category_id: str


@dataclass
class Category:
    """Represents an agent category"""

    id: str
    name: str
    description: str
    icon: str
    agents: list[str]


class AgentRegistry:
    """Registry for managing AI agents"""

    def __init__(self, registry_dir: Path | None = None):
        self.registry_dir = registry_dir or Path(__file__).parent
        self.agents: dict[str, Agent] = {}
        self.categories: dict[str, Category] = {}
        self.loaded = False

    def load_agents(self) -> None:
        """Load all agents from the registry"""
        if self.loaded:
            return

        try:
            registry_path = self.registry_dir / "registry.json"
            with open(registry_path, encoding="utf-8") as f:
                registry_data = json.load(f)

            # Load each category
            for category_id, category_data in registry_data["categories"].items():
                self.categories[category_id] = Category(id=category_id, **category_data)

                # Load each agent in the category
                for agent_id in category_data["agents"]:
                    agent_path = self.registry_dir / category_id / f"{agent_id}.json"
                    try:
                        with open(agent_path, encoding="utf-8") as f:
                            agent_data = json.load(f)

                        self.agents[agent_id] = Agent(
                            id=agent_id,
                            name=agent_data["name"],
                            category=agent_data["category"],
                            description=agent_data["description"],
                            icon=agent_data["icon"],
                            version=agent_data["version"],
                            system_prompt=agent_data["systemPrompt"],
                            capabilities=agent_data["capabilities"],
                            use_cases=agent_data["useCases"],
                            example_prompts=agent_data["examplePrompts"],
                            tools=agent_data["tools"],
                            model=agent_data["model"],
                            temperature=agent_data["temperature"],
                            max_tokens=agent_data["maxTokens"],
                            category_id=category_id,
                        )
                    except Exception as e:
                        print(f"Warning: Failed to load agent {agent_id}: {e}")

            self.loaded = True
            print(f"Loaded {len(self.agents)} agents across {len(self.categories)} categories")

        except Exception as e:
            print(f"Error: Failed to load agent registry: {e}")
            raise

    def get_agent(self, agent_id: str) -> Agent | None:
        """Get an agent by ID"""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> list[Agent]:
        """Get all agents"""
        return list(self.agents.values())

    def get_agents_by_category(self, category_id: str) -> list[Agent]:
        """Get agents by category"""
        return [agent for agent in self.agents.values() if agent.category_id == category_id]

    def get_all_categories(self) -> list[Category]:
        """Get all categories"""
        return list(self.categories.values())

    def search_agents(self, keyword: str) -> list[Agent]:
        """Search agents by keyword"""
        keyword_lower = keyword.lower()
        results = []

        for agent in self.agents.values():
            if (
                keyword_lower in agent.name.lower()
                or keyword_lower in agent.description.lower()
                or any(keyword_lower in cap.lower() for cap in agent.capabilities)
            ):
                results.append(agent)

        return results

    def recommend_agents(self, use_case: str) -> list[Agent]:
        """Get agent recommendations based on use case"""
        use_case_lower = use_case.lower()
        results = []

        for agent in self.agents.values():
            if any(use_case_lower in uc.lower() for uc in agent.use_cases):
                results.append(agent)

        return results


# Singleton instance
_registry = None


def get_registry() -> AgentRegistry:
    """Get the singleton registry instance"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        _registry.load_agents()
    return _registry


# Convenience functions
def load_agents() -> None:
    """Load all agents"""
    get_registry().load_agents()


def get_agent(agent_id: str) -> Agent | None:
    """Get an agent by ID"""
    return get_registry().get_agent(agent_id)


def get_all_agents() -> list[Agent]:
    """Get all agents"""
    return get_registry().get_all_agents()


def get_agents_by_category(category_id: str) -> list[Agent]:
    """Get agents by category"""
    return get_registry().get_agents_by_category(category_id)


def get_all_categories() -> list[Category]:
    """Get all categories"""
    return get_registry().get_all_categories()


def search_agents(keyword: str) -> list[Agent]:
    """Search agents by keyword"""
    return get_registry().search_agents(keyword)


def recommend_agents(use_case: str) -> list[Agent]:
    """Get agent recommendations"""
    return get_registry().recommend_agents(use_case)
