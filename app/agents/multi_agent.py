# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Multi-Agent System for Pinkln
Includes: Debate Panel, Code Crafter, Wealth Accelerator, Deep Reasoning
All enhanced with cheat sheet fusion and DTE evolution
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.core.pinkln_framework import UltrathinkPersona, ReasoningFramework, CheatSheetEssentials, WealthLeakDetection, PinklnFramework
from app.core.glicko2 import AgentRanking
from app.core.dte_evolution import DTEEngine

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent roles in the system"""

    DESIGNER = "ultrathink_designer"  # UX/architecture design
    WEALTH_ACCELERATOR = "wealth_accelerator"  # Revenue optimization
    DEEP_REASONING = "deep_reasoning"  # Complex problem solving
    PANEL_DEBATE = "panel_debate"  # Multi-perspective analysis
    CODE_CRAFTER = "code_crafter"  # Software development


@dataclass
class AgentResponse:
    """Response from an agent"""

    agent_id: str
    role: AgentRole
    content: str
    reasoning_path: list[ReasoningFramework]
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DebateParticipant:
    """Participant in a debate"""

    agent_id: str
    position: str  # Their stance
    arguments: list[str]
    rating: float  # Glicko-2 rating


class MultiAgentSystem:
    """
    Multi-agent orchestrator for Pinkln Ultrathink

    Coordinates:
    - Debate panels (multiple perspectives)
    - Code crafters (enhanced with cheat sheets)
    - Wealth accelerators (leak detection + optimization)
    - Deep reasoning (DTE-evolved)
    """

    def __init__(self, persona_iq: int = 160):
        self.persona_iq = persona_iq
        self.framework = PinklnFramework(persona_iq)
        self.ranking = AgentRanking()
        self.dte_engine = DTEEngine(persona_iq)
        self.agents: dict[str, dict[str, Any]] = {}

        logger.info(f"Multi-Agent System initialized at IQ {persona_iq}")

        # Register default agents
        self._register_default_agents()

    def _register_default_agents(self):
        """Register default agent roster"""
        default_agents = [
            ("designer_001", AgentRole.DESIGNER, 1550.0),
            ("wealth_001", AgentRole.WEALTH_ACCELERATOR, 1600.0),
            ("reasoning_001", AgentRole.DEEP_REASONING, 1650.0),
            ("debate_001", AgentRole.PANEL_DEBATE, 1500.0),
            ("code_001", AgentRole.CODE_CRAFTER, 1575.0),
        ]

        for agent_id, role, rating in default_agents:
            self.register_agent(agent_id, role, rating)

    def register_agent(self, agent_id: str, role: AgentRole, initial_rating: float = 1500.0):
        """Register new agent in the system"""
        self.agents[agent_id] = {"role": role, "created_at": datetime.utcnow(), "tasks_completed": 0}
        self.ranking.register_agent(agent_id, initial_rating)
        logger.info(f"Registered agent {agent_id} ({role.value}) with rating {initial_rating}")

    async def run_debate(self, topic: str, num_participants: int = 3, rounds: int = 2) -> dict[str, Any]:
        """
        Run multi-agent debate panel

        Args:
            topic: Topic to debate
            num_participants: Number of agents in debate
            rounds: Number of debate rounds

        Returns:
            Debate results with consensus and insights
        """
        logger.info(f"Starting debate: {topic} ({num_participants} agents, {rounds} rounds)")

        # Select debate agents
        debate_agents = [agent_id for agent_id, info in self.agents.items() if info["role"] == AgentRole.PANEL_DEBATE][:num_participants]

        if not debate_agents:
            # Fallback to any agents
            debate_agents = list(self.agents.keys())[:num_participants]

        # Set ultrathink persona for debate
        self.framework.set_persona(UltrathinkPersona.PAUSE_BREATHE)

        participants: list[DebateParticipant] = []
        positions = ["strongly_for", "neutral", "strongly_against"]

        # Initialize participants
        for i, agent_id in enumerate(debate_agents):
            position = positions[i % len(positions)]
            player = self.ranking.agents.get(agent_id)
            rating = player.mu if player else 1500.0

            participant = DebateParticipant(agent_id=agent_id, position=position, arguments=[], rating=rating)
            participants.append(participant)

        # Run debate rounds
        for round_num in range(1, rounds + 1):
            logger.info(f"Debate round {round_num}/{rounds}")

            for participant in participants:
                # Generate argument (at IQ 160)
                argument = self._generate_argument(topic=topic, position=participant.position, round_num=round_num)
                participant.arguments.append(argument)

        # Calculate consensus
        consensus = self._calculate_consensus(participants, topic)

        # Update agent ratings based on argument quality
        for participant in participants:
            # Simplified - would use actual argument quality scoring
            score = 0.6  # Neutral baseline
            self.agents[participant.agent_id]["tasks_completed"] += 1

        return {
            "topic": topic,
            "participants": len(participants),
            "rounds": rounds,
            "consensus": consensus,
            "arguments_generated": sum(len(p.arguments) for p in participants),
            "debate_summary": self._summarize_debate(participants),
            "persona_iq": self.persona_iq,
        }

    def _generate_argument(self, topic: str, position: str, round_num: int) -> str:
        """Generate argument for debate position"""
        # Apply reasoning framework
        self.framework.apply_reasoning(ReasoningFramework.RCR)

        # Generate argument (simplified - would use actual LLM)
        arguments = {
            "strongly_for": f"[Round {round_num}] Strong support for {topic} based on evidence and analysis at IQ {self.persona_iq}",
            "neutral": f"[Round {round_num}] Balanced perspective on {topic} considering multiple viewpoints",
            "strongly_against": f"[Round {round_num}] Critical analysis reveals concerns with {topic}",
        }

        return arguments.get(position, "No position")

    def _calculate_consensus(self, participants: list[DebateParticipant], topic: str) -> str:
        """Calculate debate consensus"""
        # Simplified consensus calculation
        positions = [p.position for p in participants]

        if positions.count("neutral") > len(positions) / 2:
            return f"Nuanced approach to {topic} recommended with careful consideration"

        return f"Diverse perspectives on {topic} - proceed with testing and validation"

    def _summarize_debate(self, participants: list[DebateParticipant]) -> str:
        """Summarize debate outcomes"""
        total_arguments = sum(len(p.arguments) for p in participants)
        positions = ", ".join(set(p.position for p in participants))

        return f"{len(participants)} agents generated {total_arguments} arguments across positions: {positions}"

    async def craft_code(self, task: str, language: str = "python", use_cheat_sheet: bool = True) -> AgentResponse:
        """
        Code crafter agent enhanced with cheat sheet fusion

        Args:
            task: Coding task description
            language: Programming language
            use_cheat_sheet: Apply cheat sheet fusion

        Returns:
            Generated code with reasoning
        """
        logger.info(f"Code crafting: {task} ({language})")

        # Set ultrathink persona
        self.framework.set_persona(UltrathinkPersona.DETAILS)

        # Apply reasoning
        self.framework.apply_reasoning(ReasoningFramework.BAB)

        # Optionally apply cheat sheet
        if use_cheat_sheet:
            cheat_sheet = CheatSheetEssentials(
                tone="technical",
                format="code_with_comments",
                act="senior_engineer",
                objective=f"Write {language} code for: {task}",
                context="Production-quality, tested, documented",
                keywords=[language, "best_practices", "clean_code"],
                audience="developers",
                citations=True,
                call_to_action="Review and test code",
            )
            prompt = self.framework.fuse_cheat_sheet(cheat_sheet)
        else:
            prompt = task

        # Generate code (simplified - would use actual code generation)
        code = f"""
# Task: {task}
# Language: {language}
# Generated at IQ {self.persona_iq} with ultrathink {self.framework.active_persona.value}

def solution():
    \"\"\"
    {task}

    Running at maximum intelligence for optimal code quality.
    \"\"\"
    # Implementation would go here
    pass

if __name__ == "__main__":
    solution()
"""

        return AgentResponse(
            agent_id="code_001",
            role=AgentRole.CODE_CRAFTER,
            content=code,
            reasoning_path=self.framework.reasoning_stack.copy(),
            confidence=0.92,
            metadata={"language": language, "cheat_sheet_used": use_cheat_sheet, "prompt": prompt if use_cheat_sheet else None},
        )

    async def accelerate_wealth(self, business_metrics: dict[str, float]) -> dict[str, Any]:
        """
        Wealth accelerator agent

        Detects leaks, proposes redesigns, structured as:
        - Hard truth
        - Plan
        - Challenge

        Args:
            business_metrics: Current metrics (conversion_rate, retention_rate, etc.)

        Returns:
            Wealth acceleration plan with detected leaks
        """
        logger.info(f"Running wealth acceleration at IQ {self.persona_iq}")

        # Set ultrathink persona
        self.framework.set_persona(UltrathinkPersona.URGENCY)

        # Apply reasoning
        self.framework.apply_reasoning(ReasoningFramework.RCR)

        leaks_detected: list[WealthLeakDetection] = []

        # Check for leaks in each metric
        leak_configs = [
            ("conversion", business_metrics.get("conversion_rate", 0.02), 0.05),
            ("retention", business_metrics.get("retention_rate", 0.60), 0.80),
            ("upsell", business_metrics.get("upsell_rate", 0.10), 0.25),
            ("viral", business_metrics.get("viral_coefficient", 0.5), 1.2),
        ]

        for leak_type, current, target in leak_configs:
            if current < target:
                leak = self.framework.detect_wealth_leak(leak_type, current, target)
                leaks_detected.append(leak)

        # Calculate total potential
        total_potential = sum(leak.potential_gain for leak in leaks_detected)

        # Prioritize leaks by severity
        prioritized = sorted(leaks_detected, key=lambda x: x.severity, reverse=True)

        return {
            "leaks_detected": len(leaks_detected),
            "total_potential_gain": total_potential,
            "prioritized_leaks": [
                {
                    "type": leak.leak_type,
                    "severity": leak.severity,
                    "current_rate": leak.current_rate,
                    "target_rate": leak.target_rate,
                    "hard_truth": leak.hard_truth,
                    "plan": leak.plan,
                    "challenge": leak.challenge,
                    "potential_gain": leak.potential_gain,
                }
                for leak in prioritized
            ],
            "persona_iq": self.persona_iq,
            "ultrathink_mode": self.framework.active_persona.value,
        }

    async def deep_reasoning(self, problem: str, use_dte_evolution: bool = True) -> AgentResponse:
        """
        Deep reasoning agent with DTE evolution

        Args:
            problem: Problem to solve
            use_dte_evolution: Apply DTE evolution for enhanced reasoning

        Returns:
            Reasoning response with evolution metrics
        """
        logger.info(f"Deep reasoning: {problem}")

        # Set ultrathink persona
        self.framework.set_persona(UltrathinkPersona.PAUSE_BREATHE)

        # Apply multiple reasoning frameworks
        self.framework.apply_reasoning(ReasoningFramework.COT)
        self.framework.apply_reasoning(ReasoningFramework.TOT)
        self.framework.apply_reasoning(ReasoningFramework.RCR)

        metadata = {}

        # Optionally use DTE evolution
        if use_dte_evolution:
            # Would create test cases and evolve strategies
            evolution_summary = self.dte_engine.get_evolution_summary()
            metadata["dte_evolution"] = evolution_summary

        # Generate reasoning (simplified)
        reasoning = f"""
Deep Reasoning Analysis (IQ {self.persona_iq}):

Problem: {problem}

Reasoning Path:
1. Chain of Thought: Break down into steps
2. Tree of Thoughts: Explore multiple solution paths
3. Reason-Critique-Refine: Iterate on best solution

Running at maximum intelligence with {len(self.framework.reasoning_stack)} frameworks applied.

[Solution would be generated here with actual reasoning]
"""

        return AgentResponse(
            agent_id="reasoning_001",
            role=AgentRole.DEEP_REASONING,
            content=reasoning,
            reasoning_path=self.framework.reasoning_stack.copy(),
            confidence=0.95,
            metadata=metadata,
        )

    def get_agent_rankings(self) -> list[dict[str, Any]]:
        """Get Glicko-2 rankings for all agents"""
        rankings = self.ranking.get_rankings()

        return [
            {
                "agent_id": agent_id,
                "rating": rating,
                "rating_deviation": rd,
                "role": self.agents[agent_id]["role"].value if agent_id in self.agents else "unknown",
                "tasks_completed": self.agents[agent_id].get("tasks_completed", 0) if agent_id in self.agents else 0,
            }
            for agent_id, rating, rd in rankings
        ]
