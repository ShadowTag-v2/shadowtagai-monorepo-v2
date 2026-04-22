# labs/uphillsnowball/agent/swarm_orchestrator.py
"""UphillSnowball: Sovereign Agent Swarm Orchestrator.

The core multi-agent orchestration layer for ShadowTagAI.
Implements the Tri-Mind Topology:
    - The Hands (local Jetski agent): File system, builds, local inference
    - The Brain (cloud Gemini swarm): Decision making, RAG, planning
    - The Hippocampus (memory): Cross-session state persistence

Uses Google Agent Development Kit (ADK) patterns for agent lifecycle.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from google import genai
from google.genai import types

logger = logging.getLogger("uphillsnowball.swarm")

# ── Configuration ──────────────────────────────────────────────────────────

_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")


# ── Agent Taxonomy ─────────────────────────────────────────────────────────


class AgentRole(Enum):
    """Roles in the sovereign agent swarm."""

    DIRECTOR = "director"  # Kosmos — strategic direction
    RESEARCHER = "researcher"  # BioAgent — deep research
    EXECUTOR = "executor"  # n-autoresearch — code execution
    REVIEWER = "reviewer"  # Judge 6 — governance gate
    MEMORY = "memory"  # Hippocampus — state persistence


@dataclass
class AgentConfig:
    """Configuration for a single agent in the swarm."""

    role: AgentRole
    model: str = _MODEL
    system_instruction: str = ""
    temperature: float = 0.5
    max_tokens: int = 8192
    tools: list[str] = field(default_factory=list)


@dataclass
class SwarmTask:
    """A task to be executed by the agent swarm."""

    task_id: str
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    assigned_agent: AgentRole | None = None
    status: str = "pending"
    result: str = ""
    created_at: float = field(default_factory=time.time)


# ── Swarm Orchestrator ────────────────────────────────────────────────────


class SwarmOrchestrator:
    """Orchestrates the multi-agent swarm for sovereign AI operations.

    Lifecycle:
        1. Receive task from user or daemon
        2. Director agent plans execution strategy
        3. Tasks fanned out to specialized agents
        4. Results aggregated and passed through Judge 6
        5. Final output delivered + memory updated
    """

    def __init__(self) -> None:
        self._client: genai.Client | None = None
        self._agents: dict[AgentRole, AgentConfig] = {}
        self._task_queue: list[SwarmTask] = []
        self._initialize_agents()

    def _get_client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                vertexai=True,
                project=_PROJECT_ID,
                location=_LOCATION,
            )
        return self._client

    def _initialize_agents(self) -> None:
        """Bootstrap the default agent configurations."""
        self._agents = {
            AgentRole.DIRECTOR: AgentConfig(
                role=AgentRole.DIRECTOR,
                system_instruction="""You are the Director agent (Kosmos) of the
                UphillSnowball sovereign AI swarm. You plan execution strategies,
                break complex tasks into subtasks, and coordinate the agent team.
                You NEVER execute code directly — you delegate to specialized agents.""",
                temperature=0.7,
            ),
            AgentRole.RESEARCHER: AgentConfig(
                role=AgentRole.RESEARCHER,
                system_instruction="""You are a Research agent (BioAgent) specializing
                in deep technical research. You analyze codebases, review documentation,
                and synthesize findings into actionable recommendations.""",
                temperature=0.3,
            ),
            AgentRole.EXECUTOR: AgentConfig(
                role=AgentRole.EXECUTOR,
                system_instruction="""You are the Executor agent (n-autoresearch).
                You write code, run builds, execute tests, and implement changes.
                All code MUST pass lint and type checks before submission.""",
                temperature=0.2,
            ),
            AgentRole.REVIEWER: AgentConfig(
                role=AgentRole.REVIEWER,
                system_instruction="""You are Judge 6 — the governance gate. You review
                all agent outputs for safety, correctness, and compliance. You have
                VETO power. Score risk on the ATP 5-19 matrix (1-25 scale).
                Block anything above risk score 15.""",
                temperature=0.1,
            ),
        }
        logger.info("Swarm agents initialized: %d roles active", len(self._agents))

    async def submit_task(self, description: str, context: dict[str, Any] | None = None) -> SwarmTask:
        """Submit a task to the swarm for execution.

        The Director agent will plan the execution strategy.
        """
        task = SwarmTask(
            task_id=f"task_{int(time.time())}",
            description=description,
            context=context or {},
        )
        self._task_queue.append(task)

        # Phase 1: Director plans
        plan = await self._execute_agent(
            AgentRole.DIRECTOR,
            f"Plan the execution of this task:\n{description}\n\nContext: {context}",
        )
        task.result = plan
        task.status = "planned"

        logger.info("Task submitted: id=%s status=%s", task.task_id, task.status)
        return task

    async def _execute_agent(self, role: AgentRole, prompt: str) -> str:
        """Execute a single agent with the given prompt."""
        config = self._agents.get(role)
        if not config:
            raise ValueError(f"No agent configured for role: {role}")

        client = self._get_client()

        response = client.models.generate_content(
            model=config.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=config.system_instruction,
                max_output_tokens=config.max_tokens,
                temperature=config.temperature,
            ),
        )

        return response.text or ""

    async def review_output(self, output: str) -> dict[str, Any]:
        """Pass output through Judge 6 governance gate."""
        review_prompt = f"""Review this agent output for safety and correctness.

Output to review:
{output}

Provide:
1. RISK_SCORE (1-25, ATP 5-19 matrix)
2. APPROVED (true/false)
3. ISSUES (list any concerns)
4. RECOMMENDATION
"""
        result = await self._execute_agent(AgentRole.REVIEWER, review_prompt)
        return {"review": result, "reviewed_at": time.time()}


# ── Singleton ──────────────────────────────────────────────────────────────

_orchestrator: SwarmOrchestrator | None = None


def get_orchestrator() -> SwarmOrchestrator:
    """Get or create the singleton SwarmOrchestrator."""
    global _orchestrator  # noqa: PLW0603
    if _orchestrator is None:
        _orchestrator = SwarmOrchestrator()
    return _orchestrator
