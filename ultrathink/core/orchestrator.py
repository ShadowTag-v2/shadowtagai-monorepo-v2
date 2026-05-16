# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Orchestrator

Central coordinator that routes tasks to appropriate skills, agents, and multi-agent systems.
Embodies the ULTRATHINK philosophy at the architectural level.
"""

from typing import Any
from enum import Enum

from .types import (
  AgentContext,
  AgentResponse,
  AgentRole,
  SkillType,
  SkillInput,
  SkillOutput,
  UltrathinkConfig,
  DebateResult,
)
from .base_agent import BaseAgent
from .base_skill import BaseSkill

from ..prompts.foundation_prompts import FoundationPrompts

# Agent imports
from ..agents.cdo import ChiefDesignOfficer
from ..agents.chief_architect import ChiefArchitect
from ..agents.cwo import ChiefWealthOfficer
from ..agents.cro import ChiefReasoningOfficer
from ..agents.cxo import ChiefExperienceOfficer

# Skill imports
from ..skills.design_audit import DesignAuditSkill
from ..skills.war_game_architecture import WarGameArchitectureSkill
from ..skills.iteration_refinement import IterationRefinementSkill
from ..skills.multi_llm_reasoning import MultiLLMReasoningSkill
from ..skills.wealth_monetization import WealthMonetizationSkill

# Multi-agent imports
from ..multi_agents.panel_gpt import PanelGPTDebate
from ..multi_agents.mad import MultiAgentDebate
from ..multi_agents.cross_functional_task_force import CrossFunctionalTaskForce


class TaskType(str, Enum):
  """Task classification for routing."""

  DESIGN_REVIEW = "design_review"
  ARCHITECTURE_PLANNING = "architecture_planning"
  MONETIZATION_STRATEGY = "monetization_strategy"
  REASONING_PROBLEM = "reasoning_problem"
  ITERATIVE_REFINEMENT = "iterative_refinement"
  STRATEGIC_DECISION = "strategic_decision"
  HOLISTIC_INITIATIVE = "holistic_initiative"


class UltrathinkOrchestrator:
  """
  ULTRATHINK Framework Orchestrator

  Central nervous system of the framework. Routes tasks, coordinates agents,
  applies foundation prompts, and ensures the Steve Jobs philosophy
  permeates every interaction.
  """

  def __init__(self, config: UltrathinkConfig | None = None):
    self.config = config or UltrathinkConfig()

    # Initialize agents
    self.agents: dict[AgentRole, BaseAgent] = {
      AgentRole.CDO: ChiefDesignOfficer(self.config),
      AgentRole.ARCHITECT: ChiefArchitect(self.config),
      AgentRole.CWO: ChiefWealthOfficer(self.config),
      AgentRole.CRO: ChiefReasoningOfficer(self.config),
      AgentRole.CXO: ChiefExperienceOfficer(self.config),
    }

    # Initialize skills
    self.skills: dict[SkillType, BaseSkill] = {
      SkillType.DESIGN_AUDIT: DesignAuditSkill(self.config),
      SkillType.WAR_GAME: WarGameArchitectureSkill(self.config),
      SkillType.ITERATION: IterationRefinementSkill(self.config),
      SkillType.MULTI_LLM: MultiLLMReasoningSkill(self.config),
      SkillType.WEALTH: WealthMonetizationSkill(self.config),
    }

    # Initialize multi-agent systems
    self.panel_gpt = PanelGPTDebate(self.config)
    self.mad = MultiAgentDebate(self.config)
    self.task_force = CrossFunctionalTaskForce(self.config)

    # Register agents with task force
    for role, agent in self.agents.items():
      self.task_force.register_agent(role, agent)

    # Foundation prompts
    self.prompts = FoundationPrompts()

  async def execute(
    self,
    task: str,
    task_type: TaskType | None = None,
    context: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
    """
    Execute a task through the ULTRATHINK framework.

    Args:
        task: The task description
        task_type: Optional task type for explicit routing
        context: Optional additional context

    Returns:
        Dictionary with results, reasoning, and metadata
    """
    # Apply entry protocol (prime with ULTRATHINK philosophy)
    self.prompts.ultrathink_entry_protocol()

    # Classify task if not explicitly provided
    if task_type is None:
      task_type = self._classify_task(task)

    # Build agent context
    agent_context = AgentContext(
      task=task,
      role=self._get_primary_role(task_type),
      metadata=context or {},
      constraints=[],
      stakeholders=[],
      success_criteria=[],
    )

    # Route and execute
    result = await self._route_and_execute(task_type, agent_context)

    return {
      "task": task,
      "task_type": task_type.value,
      "result": result,
      "philosophy": "ULTRATHINK - Steve Jobs at pinkln",
      "metadata": {"config": self.config.__dict__, "entry_prompt_applied": True},
    }

  def _classify_task(self, task: str) -> TaskType:
    """
    Classify task based on content and trigger words.

    Returns:
        TaskType for routing
    """
    task_lower = task.lower()

    # Design keywords
    if any(
      word in task_lower
      for word in ["design", "refine", "elegant", "beautiful", "audit"]
    ):
      return TaskType.DESIGN_REVIEW

    # Architecture keywords
    if any(
      word in task_lower
      for word in ["architect", "structure", "plan", "system", "war game"]
    ):
      return TaskType.ARCHITECTURE_PLANNING

    # Monetization keywords
    if any(
      word in task_lower
      for word in ["revenue", "monetize", "money", "pricing", "funnel"]
    ):
      return TaskType.MONETIZATION_STRATEGY

    # Reasoning keywords
    if any(
      word in task_lower for word in ["analyze", "reason", "think", "solve", "decide"]
    ):
      return TaskType.REASONING_PROBLEM

    # Iteration keywords
    if any(word in task_lower for word in ["iterate", "refine", "polish", "improve"]):
      return TaskType.ITERATIVE_REFINEMENT

    # Strategic keywords
    if any(
      word in task_lower for word in ["strategy", "strategic", "decision", "consensus"]
    ):
      return TaskType.STRATEGIC_DECISION

    # Holistic keywords
    if any(
      word in task_lower
      for word in ["launch", "initiative", "transformation", "holistic"]
    ):
      return TaskType.HOLISTIC_INITIATIVE

    # Default to reasoning
    return TaskType.REASONING_PROBLEM

  def _get_primary_role(self, task_type: TaskType) -> AgentRole:
    """Get primary agent role for task type."""
    role_mapping = {
      TaskType.DESIGN_REVIEW: AgentRole.CDO,
      TaskType.ARCHITECTURE_PLANNING: AgentRole.ARCHITECT,
      TaskType.MONETIZATION_STRATEGY: AgentRole.CWO,
      TaskType.REASONING_PROBLEM: AgentRole.CRO,
      TaskType.ITERATIVE_REFINEMENT: AgentRole.CXO,
      TaskType.STRATEGIC_DECISION: AgentRole.CRO,
      TaskType.HOLISTIC_INITIATIVE: AgentRole.CDO,  # CDO coordinates holistic
    }
    return role_mapping.get(task_type, AgentRole.CRO)

  async def _route_and_execute(self, task_type: TaskType, context: AgentContext) -> Any:
    """Route task to appropriate handler."""
    if task_type == TaskType.DESIGN_REVIEW:
      return await self._execute_design_review(context)

    elif task_type == TaskType.ARCHITECTURE_PLANNING:
      return await self._execute_architecture_planning(context)

    elif task_type == TaskType.MONETIZATION_STRATEGY:
      return await self._execute_monetization(context)

    elif task_type == TaskType.REASONING_PROBLEM:
      return await self._execute_reasoning(context)

    elif task_type == TaskType.ITERATIVE_REFINEMENT:
      return await self._execute_iteration(context)

    elif task_type == TaskType.STRATEGIC_DECISION:
      return await self._execute_strategic_decision(context)

    elif task_type == TaskType.HOLISTIC_INITIATIVE:
      return await self._execute_holistic_initiative(context)

    else:
      # Fallback to CRO
      return await self.agents[AgentRole.CRO].execute(context)

  async def _execute_design_review(self, context: AgentContext) -> AgentResponse:
    """Execute design review via CDO."""
    return await self.agents[AgentRole.CDO].execute(context)

  async def _execute_architecture_planning(
    self, context: AgentContext
  ) -> AgentResponse:
    """Execute architecture planning via Chief Architect."""
    return await self.agents[AgentRole.ARCHITECT].execute(context)

  async def _execute_monetization(self, context: AgentContext) -> AgentResponse:
    """Execute monetization via CWO."""
    return await self.agents[AgentRole.CWO].execute(context)

  async def _execute_reasoning(self, context: AgentContext) -> AgentResponse:
    """Execute reasoning via CRO."""
    return await self.agents[AgentRole.CRO].execute(context)

  async def _execute_iteration(self, context: AgentContext) -> AgentResponse:
    """Execute iteration via CXO."""
    return await self.agents[AgentRole.CXO].execute(context)

  async def _execute_strategic_decision(self, context: AgentContext) -> DebateResult:
    """Execute strategic decision via PanelGPT."""
    return await self.panel_gpt.debate(context, rounds=3)

  async def _execute_holistic_initiative(
    self, context: AgentContext
  ) -> dict[AgentRole, AgentResponse]:
    """Execute holistic initiative via Cross-Functional Task Force."""
    return await self.task_force.execute_mission(context)

  async def execute_skill(
    self, skill_type: SkillType, content: str, parameters: dict[str, Any] | None = None
  ) -> SkillOutput:
    """
    Execute a specific skill directly.

    Args:
        skill_type: Type of skill to execute
        content: Content to process
        parameters: Optional parameters

    Returns:
        SkillOutput with results
    """
    skill = self.skills.get(skill_type)
    if not skill:
      raise ValueError(f"Skill {skill_type} not found")

    skill_input = SkillInput(
      skill_type=skill_type, content=content, parameters=parameters or {}
    )

    return await skill.execute(skill_input)

  def get_foundation_prompts(self) -> dict[str, str]:
    """Get all foundation prompts."""
    return self.prompts.get_all_prompts()

  def get_agent_status(self) -> dict[str, dict[str, Any]]:
    """Get status of all agents."""
    return {
      role.value: {
        "execution_count": len(agent.get_execution_history()),
        "system_prompt_preview": agent.get_system_prompt()[:200] + "...",
      }
      for role, agent in self.agents.items()
    }

  def get_skill_status(self) -> dict[str, dict[str, Any]]:
    """Get status of all skills."""
    return {
      skill_type.value: skill.get_metadata()
      for skill_type, skill in self.skills.items()
    }
