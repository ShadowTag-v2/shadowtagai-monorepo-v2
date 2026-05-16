# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pinkln Ultrathink API Endpoints
Multi-agent platform with debates, code crafters, wealth acceleration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from app.agents.multi_agent import MultiAgentSystem
from app.core.pinkln_framework import UltrathinkPersona, CheatSheetEssentials
from app.core.dte_evolution import GRPOSimulator

router = APIRouter()

# Initialize multi-agent system
mas = MultiAgentSystem(persona_iq=160)
grpo_sim = GRPOSimulator(group_size=8)


# Request/Response Models
class DebateRequest(BaseModel):
    """Request for multi-agent debate"""

    topic: str = Field(..., description="Topic to debate")
    num_participants: int = Field(default=3, ge=2, le=10)
    rounds: int = Field(default=2, ge=1, le=5)


class CodeCraftRequest(BaseModel):
    """Request for code crafting"""

    task: str = Field(..., description="Coding task description")
    language: str = Field(default="python", description="Programming language")
    use_cheat_sheet: bool = Field(default=True, description="Apply cheat sheet fusion")


class WealthAccelerationRequest(BaseModel):
    """Request for wealth acceleration analysis"""

    conversion_rate: float = Field(..., ge=0.0, le=1.0)
    retention_rate: float = Field(..., ge=0.0, le=1.0)
    upsell_rate: float = Field(..., ge=0.0, le=1.0)
    viral_coefficient: float = Field(..., ge=0.0)


class DeepReasoningRequest(BaseModel):
    """Request for deep reasoning"""

    problem: str = Field(..., description="Problem to solve")
    use_dte_evolution: bool = Field(default=True, description="Apply DTE evolution")


class CheatSheetRequest(BaseModel):
    """Request to generate evolved prompt"""

    tone: str = "professional"
    format: str = "structured"
    act: str = "expert"
    objective: str
    context: str
    keywords: list[str] = []
    examples: list[str] = []
    audience: str = "technical"
    citations: bool = True
    call_to_action: str = ""


class GRPOComparisonRequest(BaseModel):
    """Request for GRPO/PPO comparison"""

    rewards: list[float] = Field(..., description="Reward values for comparison")
    epsilon: float = Field(default=0.2, description="PPO clipping parameter")


# Endpoints


@router.post("/debate")
async def run_debate(request: DebateRequest) -> dict[str, Any]:
    """
    Run multi-agent debate panel

    Features:
    - Multiple AI perspectives (IQ 160)
    - Structured argumentation
    - Consensus building
    - Glicko-2 ranked participants
    """
    result = await mas.run_debate(topic=request.topic, num_participants=request.num_participants, rounds=request.rounds)
    return result


@router.post("/code/craft")
async def craft_code(request: CodeCraftRequest) -> dict[str, Any]:
    """
    Code crafter agent with cheat sheet fusion

    Features:
    - DTE-evolved prompts
    - Production-quality code
    - Best practices embedded
    - IQ 160 implementation
    """
    response = await mas.craft_code(task=request.task, language=request.language, use_cheat_sheet=request.use_cheat_sheet)

    return {
        "agent_id": response.agent_id,
        "role": response.role.value,
        "code": response.content,
        "reasoning_path": [f.value for f in response.reasoning_path],
        "confidence": response.confidence,
        "metadata": response.metadata,
    }


@router.post("/wealth/accelerate")
async def accelerate_wealth(request: WealthAccelerationRequest) -> dict[str, Any]:
    """
    Wealth accelerator agent

    Features:
    - Leak detection (conversion, retention, upsell, viral)
    - Hard truth / Plan / Challenge structure
    - Revenue optimization at IQ 160
    - Funnel redesign recommendations
    """
    metrics = {
        "conversion_rate": request.conversion_rate,
        "retention_rate": request.retention_rate,
        "upsell_rate": request.upsell_rate,
        "viral_coefficient": request.viral_coefficient,
    }

    result = await mas.accelerate_wealth(metrics)
    return result


@router.post("/reasoning/deep")
async def deep_reasoning(request: DeepReasoningRequest) -> dict[str, Any]:
    """
    Deep reasoning agent with DTE evolution

    Features:
    - Multi-framework reasoning (CoT, ToT, RCR)
    - DTE self-evolution
    - IQ 160 problem solving
    - Evolved strategies (+3.7% accuracy)
    """
    response = await mas.deep_reasoning(problem=request.problem, use_dte_evolution=request.use_dte_evolution)

    return {
        "agent_id": response.agent_id,
        "role": response.role.value,
        "reasoning": response.content,
        "reasoning_path": [f.value for f in response.reasoning_path],
        "confidence": response.confidence,
        "metadata": response.metadata,
    }


@router.post("/cheat-sheet/fuse")
async def fuse_cheat_sheet(request: CheatSheetRequest) -> dict[str, str]:
    """
    Cheat sheet fusion (21→10 essentials)

    Generates evolved prompts with:
    - Tone, format, act, objective, context
    - Keywords, examples, audience
    - Citations, call-to-action
    - Ultrathink enhancement at IQ 160
    """
    essentials = CheatSheetEssentials(
        tone=request.tone,
        format=request.format,
        act=request.act,
        objective=request.objective,
        context=request.context,
        keywords=request.keywords,
        examples=request.examples,
        audience=request.audience,
        citations=request.citations,
        call_to_action=request.call_to_action,
    )

    fused_prompt = mas.framework.fuse_cheat_sheet(essentials)

    return {"fused_prompt": fused_prompt, "persona_iq": mas.persona_iq, "ultrathink_mode": mas.framework.active_persona.value}


@router.get("/agents/rankings")
async def get_agent_rankings() -> list[dict[str, Any]]:
    """
    Get Glicko-2 agent rankings

    Returns:
    - Agent ratings (superiority over Elo)
    - Rating deviation (uncertainty)
    - Role and task completion
    """
    return mas.get_agent_rankings()


@router.post("/grpo/compare")
async def compare_grpo_ppo(request: GRPOComparisonRequest) -> dict[str, Any]:
    """
    GRPO vs PPO comparison

    Compares:
    - GRPO (Group Relative Policy Optimization)
    - PPO (Proximal Policy Optimization)

    Shows GRPO advantages:
    - No clipping needed
    - Relative advantages
    - Better sample efficiency
    """
    if len(request.rewards) != grpo_sim.group_size:
        raise HTTPException(status_code=400, detail=f"Expected {grpo_sim.group_size} rewards, got {len(request.rewards)}")

    comparison = grpo_sim.compare_with_ppo(request.rewards, request.epsilon)

    return {
        "grpo_loss": comparison["grpo_loss"],
        "ppo_loss": comparison["ppo_loss"],
        "grpo_advantages": comparison["grpo_advantages"],
        "ppo_advantages": comparison["ppo_advantages"],
        "grpo_better": comparison["grpo_better"],
        "difference": comparison["difference"],
        "interpretation": ("GRPO outperforms PPO" if comparison["grpo_better"] else "PPO outperforms GRPO"),
    }


@router.get("/system/status")
async def get_system_status() -> dict[str, Any]:
    """Get Pinkln system status"""
    return {
        "status": "operational",
        "persona_iq": mas.persona_iq,
        "agents_registered": len(mas.agents),
        "agent_roles": list(set(info["role"].value for info in mas.agents.values())),
        "dte_evolution": mas.dte_engine.get_evolution_summary(),
        "ultrathink_mode": mas.framework.active_persona.value,
        "frameworks_available": [f.value for f in mas.framework.reasoning_stack] or ["ready"],
        "glicko_agents": len(mas.ranking.agents),
    }


@router.get("/personas")
async def list_personas() -> list[dict[str, str]]:
    """List available ultrathink personas"""
    return [
        {"persona": UltrathinkPersona.PAUSE_BREATHE.value, "description": "Take a moment to think deeply"},
        {"persona": UltrathinkPersona.URGENCY.value, "description": "Ship it, make it happen NOW"},
        {"persona": UltrathinkPersona.BEAUTY.value, "description": "Insanely great design"},
        {"persona": UltrathinkPersona.DETAILS.value, "description": "Sweat every detail"},
        {"persona": UltrathinkPersona.SIMPLIFY.value, "description": "Remove everything unnecessary"},
        {"persona": UltrathinkPersona.BOY_SCOUT.value, "description": "Leave it better than you found it"},
    ]


@router.post("/personas/switch/{persona}")
async def switch_persona(persona: UltrathinkPersona) -> dict[str, str]:
    """Switch active ultrathink persona"""
    mas.framework.set_persona(persona)
    return {"active_persona": mas.framework.active_persona.value, "description": f"Switched to {persona.value} mode at IQ {mas.persona_iq}"}
