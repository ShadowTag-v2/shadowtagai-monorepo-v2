# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework

Integrated Skills, Agents & Prompts Framework inspired by Steve Jobs' philosophy.

Core Philosophy:
- Design-first thinking
- Ruthless simplification (pinkln elegance)
- Reality distortion field mindset
- Boy Scout Rule
- Integration of technology + liberal arts

Usage:
    from ultrathink import UltrathinkOrchestrator, TaskType

    orchestrator = UltrathinkOrchestrator()
    result = await orchestrator.execute(
        "Design a monetization strategy for my SaaS",
        task_type=TaskType.MONETIZATION_STRATEGY
    )
"""

__version__ = "1.0.0"
__author__ = "pinkln"

# Core imports
from .core.orchestrator import UltrathinkOrchestrator, TaskType
from .core.types import (
    UltrathinkConfig,
    AgentContext,
    AgentResponse,
    AgentRole,
    SkillType,
    SkillInput,
    SkillOutput,
    ReasoningMethod,
    MonetizationStrategy,
    ArchitecturePlan,
    DebateResult,
)

# Agent imports
from .agents.cdo import ChiefDesignOfficer
from .agents.chief_architect import ChiefArchitect
from .agents.cwo import ChiefWealthOfficer
from .agents.cro import ChiefReasoningOfficer
from .agents.cxo import ChiefExperienceOfficer

# Skill imports
from .skills.design_audit import DesignAuditSkill
from .skills.war_game_architecture import WarGameArchitectureSkill
from .skills.iteration_refinement import IterationRefinementSkill
from .skills.multi_llm_reasoning import MultiLLMReasoningSkill
from .skills.wealth_monetization import WealthMonetizationSkill

# Multi-agent imports
from .multi_agents.panel_gpt import PanelGPTDebate
from .multi_agents.mad import MultiAgentDebate
from .multi_agents.cross_functional_task_force import CrossFunctionalTaskForce

# Prompt imports
from .prompts.foundation_prompts import FoundationPrompts

__all__ = [
    # Core
    "UltrathinkOrchestrator",
    "TaskType",
    "UltrathinkConfig",
    # Types
    "AgentContext",
    "AgentResponse",
    "AgentRole",
    "SkillType",
    "SkillInput",
    "SkillOutput",
    "ReasoningMethod",
    "MonetizationStrategy",
    "ArchitecturePlan",
    "DebateResult",
    # Agents
    "ChiefDesignOfficer",
    "ChiefArchitect",
    "ChiefWealthOfficer",
    "ChiefReasoningOfficer",
    "ChiefExperienceOfficer",
    # Skills
    "DesignAuditSkill",
    "WarGameArchitectureSkill",
    "IterationRefinementSkill",
    "MultiLLMReasoningSkill",
    "WealthMonetizationSkill",
    # Multi-Agents
    "PanelGPTDebate",
    "MultiAgentDebate",
    "CrossFunctionalTaskForce",
    # Prompts
    "FoundationPrompts",
]
