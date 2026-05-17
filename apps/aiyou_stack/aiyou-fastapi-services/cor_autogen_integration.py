# ⚠️ DEPRECATED — This file contains references to deprecated frameworks
# (AutoGen/AG2, LangGraph, Vertex AI Workbench) that are no longer part of
# the production CounselConduit architecture. These refs are slated for
# removal. See deploy-preflight findings 2026-05-17.
# Production path: apps/counselconduit/api/fastapi_kovel_enclave.py
"""COR AutoGen Integration - Multi-Agent Orchestration with Skill Routing

This module provides:
1. AutoGen agent orchestration with Anthropic Claude integration
2. Skill-aware task routing based on COR Skill Registry
3. Multi-agent conversation management
4. Task decomposition and parallel execution
5. ShadowTag watermark injection for audit trails

Architecture:
- SkillRouter: Routes tasks to appropriate skills based on capability matching
- COROrchestrator: Manages multi-agent conversations and task execution
- ClaudeAgent: Wrapper for Anthropic Claude with AutoGen compatibility
- WatermarkInjector: Ensures all outputs contain ShadowTag for provenance

Author: PNKLN Strategic Systems
Version: 1.0.0
"""

import logging
import os
from datetime import datetime
from typing import Any

from anthropic import Anthropic

# AutoGen imports - note: requires autogen package
try:
    import autogen  # noqa: F401
    from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent  # noqa: F401

    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    logging.warning("AutoGen not installed. Install with: pip install pyautogen")

from cor_skill_registry import CORSkillRegistry, SkillMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShadowTag:
    """ShadowTag watermark generator for audit trails"""

    @staticmethod
    def generate(task_id: str, agent_name: str, timestamp: str | None = None) -> str:
        """Generate a ShadowTag watermark

        Format: [ST:TASKID:AGENT:TIMESTAMP]
        """
        ts = timestamp or datetime.utcnow().isoformat()
        return f"[ST:{task_id}:{agent_name}:{ts}]"

    @staticmethod
    def inject(content: str, task_id: str, agent_name: str) -> str:
        """Inject ShadowTag into content (appended as comment)"""
        tag = ShadowTag.generate(task_id, agent_name)
        return f"{content}\n\n<!-- {tag} -->"


class SkillRouter:
    """Routes tasks to appropriate skills based on capability matching"""

    def __init__(self, skill_registry: CORSkillRegistry):
        """Initialize SkillRouter

        Args:
            skill_registry: COR Skill Registry instance

        """
        self.registry = skill_registry

    def route_task(self, task_description: str) -> SkillMetadata | None:
        """Route a task to the most appropriate skill

        Args:
            task_description: Natural language task description

        Returns:
            SkillMetadata for best-matching skill, or None if no match

        """
        # Simple keyword matching - in production, use embeddings/semantic search
        task_lower = task_description.lower()

        best_match = None
        best_score = 0

        for skill in self.registry.skills_cache.values():
            score = self._calculate_match_score(task_lower, skill)
            if score > best_score:
                best_score = score
                best_match = skill

        if best_match and best_score > 0.3:  # Threshold for match confidence
            logger.info(f"Routed task to skill: {best_match.name} (score: {best_score:.2f})")
            return best_match
        logger.warning(f"No skill match found for task: {task_description[:50]}...")
        return None

    def _calculate_match_score(self, task: str, skill: SkillMetadata) -> float:
        """Calculate match score between task and skill"""
        score = 0.0

        # Check name match
        if skill.name.lower() in task:
            score += 0.5

        # Check category match
        if skill.category.lower() in task:
            score += 0.3

        # Check capabilities match
        for capability in skill.capabilities:
            if capability.lower() in task:
                score += 0.2

        # Check description keywords
        desc_words = skill.description.lower().split()
        task_words = task.split()
        common_words = set(desc_words) & set(task_words)
        score += len(common_words) * 0.1

        return min(score, 1.0)  # Cap at 1.0


class ClaudeAgent:
    """Wrapper for Anthropic Claude that integrates with AutoGen

    This agent uses Claude as the backend LLM for AutoGen conversations
    """

    def __init__(
        self,
        name: str,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-5-20250929",
        system_prompt: str | None = None,
    ):
        """Initialize Claude Agent

        Args:
            name: Agent name
            api_key: Anthropic API key
            model: Claude model to use
            system_prompt: System prompt for agent

        """
        self.name = name
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.system_prompt = system_prompt or f"You are {name}, a helpful AI assistant."
        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history: list[dict[str, str]] = []

    def generate_response(self, message: str, context: list[dict] | None = None) -> str:
        """Generate a response using Claude

        Args:
            message: Input message
            context: Conversation context

        Returns:
            Claude's response

        """
        # Build conversation context
        messages = context or self.conversation_history.copy()
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages,
            )

            assistant_message = response.content[0].text

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Error generating response: {e}"


class COROrchestrator:
    """Multi-agent orchestrator with skill routing and task management"""

    def __init__(self, api_key: str | None = None, enable_watermarks: bool = True):
        """Initialize COR Orchestrator

        Args:
            api_key: Anthropic API key
            enable_watermarks: Enable ShadowTag watermarking

        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.enable_watermarks = enable_watermarks

        # Initialize components
        self.skill_registry = CORSkillRegistry(api_key=self.api_key)
        self.skill_router = SkillRouter(self.skill_registry)
        self.agents: dict[str, ClaudeAgent] = {}
        self.task_counter = 0

        # Discover skills
        self.skill_registry.discover_skills()

        logger.info("COR Orchestrator initialized")

    def create_agent(
        self,
        name: str,
        role: str,
        capabilities: list[str] | None = None,
    ) -> ClaudeAgent:
        """Create a specialized agent

        Args:
            name: Agent name
            role: Agent role description
            capabilities: List of capabilities

        Returns:
            ClaudeAgent instance

        """
        system_prompt = f"""You are {name}, a specialized AI agent.

Role: {role}

Capabilities: {", ".join(capabilities or [])}

Your task is to execute your role effectively while adhering to all constraints and doctrine requirements.
Always provide clear, actionable outputs with proper reasoning.
"""

        agent = ClaudeAgent(name=name, api_key=self.api_key, system_prompt=system_prompt)

        self.agents[name] = agent
        logger.info(f"Created agent: {name}")
        return agent

    def execute_task(
        self,
        task_description: str,
        agent_name: str | None = None,
        enable_skill_routing: bool = True,
    ) -> dict[str, Any]:
        """Execute a task using agents and skill routing

        Args:
            task_description: Task to execute
            agent_name: Specific agent to use (optional)
            enable_skill_routing: Enable automatic skill routing

        Returns:
            Execution result dictionary

        """
        self.task_counter += 1
        task_id = f"TASK_{self.task_counter:04d}"

        logger.info(f"Executing task {task_id}: {task_description[:50]}...")

        # Route to skill if enabled
        selected_skill = None
        if enable_skill_routing:
            selected_skill = self.skill_router.route_task(task_description)

        # Select or create agent
        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
        else:
            # Create default execution agent
            agent = self.create_agent(
                name=f"Agent_{task_id}",
                role="Task Executor",
                capabilities=["general_execution"],
            )

        # Execute task
        start_time = datetime.utcnow()

        # Enhance prompt with skill context if available
        enhanced_prompt = task_description
        if selected_skill:
            enhanced_prompt = f"""Task: {task_description}

Recommended Skill: {selected_skill.name}
Skill Description: {selected_skill.description}
Risk Level: {selected_skill.risk_level}
Capabilities: {", ".join(selected_skill.capabilities)}

Execute this task using the recommended skill approach."""

        response = agent.generate_response(enhanced_prompt)

        # Inject watermark if enabled
        if self.enable_watermarks:
            response = ShadowTag.inject(response, task_id, agent.name)

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()

        result = {
            "task_id": task_id,
            "task_description": task_description,
            "agent_name": agent.name,
            "skill_used": selected_skill.name if selected_skill else None,
            "risk_level": selected_skill.risk_level if selected_skill else "RA-4",
            "response": response,
            "execution_time_seconds": execution_time,
            "timestamp": end_time.isoformat(),
            "watermarked": self.enable_watermarks,
        }

        logger.info(f"Task {task_id} completed in {execution_time:.2f}s")
        return result

    def execute_multi_agent_task(
        self,
        task_description: str,
        agent_roles: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Execute a task using multiple agents in collaboration

        Args:
            task_description: Task to execute
            agent_roles: List of agent role specifications
                        [{'name': 'Agent1', 'role': 'Researcher', 'capabilities': [...]}]

        Returns:
            Execution result with multi-agent conversation

        """
        if not AUTOGEN_AVAILABLE:
            logger.error("AutoGen not available for multi-agent execution")
            return {
                "error": "AutoGen not installed",
                "message": "Install with: pip install pyautogen",
            }

        self.task_counter += 1
        task_id = f"MULTI_TASK_{self.task_counter:04d}"

        logger.info(f"Executing multi-agent task {task_id}")

        # Create agents for this task
        for role_spec in agent_roles:
            self.create_agent(
                name=role_spec["name"],
                role=role_spec["role"],
                capabilities=role_spec.get("capabilities", []),
            )

        # Note: Full AutoGen integration would go here
        # This is a simplified version showing the architecture

        result = {
            "task_id": task_id,
            "task_description": task_description,
            "agents": [spec["name"] for spec in agent_roles],
            "status": "multi_agent_execution_pending",
            "message": "Full AutoGen integration in progress",
        }

        return result


def main():
    """Example usage and smoke test"""
    print("=== COR AutoGen Integration - Multi-Agent Orchestration ===\n")

    # Initialize orchestrator
    orchestrator = COROrchestrator()

    # Example 1: Simple task execution with skill routing
    print("\n--- Example 1: Skill-Routed Task Execution ---")
    result = orchestrator.execute_task(
        task_description="Analyze the security vulnerabilities in a Python web application",
    )
    print(f"Task ID: {result['task_id']}")
    print(f"Agent: {result['agent_name']}")
    print(f"Skill Used: {result['skill_used']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Execution Time: {result['execution_time_seconds']:.2f}s")
    print(f"Response Preview: {result['response'][:200]}...")

    # Example 2: High-risk task (should route to RA-1/RA-2 skill)
    print("\n--- Example 2: High-Risk Task Routing ---")
    result = orchestrator.execute_task(
        task_description="Execute database deletion of production user records",
    )
    print(f"Task ID: {result['task_id']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Skill Used: {result['skill_used']}")

    # Example 3: Multi-agent collaboration
    print("\n--- Example 3: Multi-Agent Task ---")
    result = orchestrator.execute_multi_agent_task(
        task_description="Develop a healthcare GTM strategy with regulatory compliance",
        agent_roles=[
            {"name": "Researcher", "role": "Market Research", "capabilities": ["market_analysis"]},
            {
                "name": "ComplianceOfficer",
                "role": "Regulatory Review",
                "capabilities": ["hipaa_compliance"],
            },
            {
                "name": "Strategist",
                "role": "Strategy Development",
                "capabilities": ["gtm_planning"],
            },
        ],
    )
    print(f"Task ID: {result['task_id']}")
    print(f"Agents: {', '.join(result['agents'])}")
    print(f"Status: {result['status']}")

    print("\n✓ COR AutoGen Integration smoke test complete")


if __name__ == "__main__":
    main()
