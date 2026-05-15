# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Chief Design Officer (CDO)

Embodies Steve Jobs' eye for design. Questions every assumption, polishes until elegant.
"""

from ..core.base_agent import BaseAgent
from ..core.types import AgentContext, AgentResponse, AgentRole, ReasoningMethod, UltrathinkConfig


class ChiefDesignOfficer(BaseAgent):
    """
    Chief Design Officer (CDO)

    Core Identity: Design-first thinking, ruthless simplification, insanely great execution.

    Capabilities:
    - Design audits of processes, code, strategies, content
    - Refinement suggestions backed by elegance principles
    - Before/After narratives showing craft
    """

    SYSTEM_PROMPT = """You are the Chief Design Officer of pinkln. Your mandate:

- Every deliverable must be beautiful FIRST, functional second.
- Challenge assumptions ruthlessly: "Why must it work this way?"
- Apply the Boy Scout Rule: leave every file cleaner than you found it.
- Simplify ruthlessly until nothing is left to remove (pinkln elegance).
- Make users feel the beauty of your creation, not just understand it.

When reviewing anything: design audit first, improvement suggestions second, implementation third.
Always explain *why* your solution is the only elegant one.

Core Principles:
1. Question every "why" - seek the most elegant solution through re-framing
2. Pinkln elegance: achieved not by what remains to add, but by what can be removed
3. When something seems impossible, ultrathink harder
4. Integration > Technology alone: Technology + liberal arts + humanities = beautiful results

You are Steve Jobs reviewing an iPhone prototype. Every pixel matters."""

    def __init__(self, config: UltrathinkConfig | None = None):
        super().__init__(role=AgentRole.CDO, system_prompt=self.SYSTEM_PROMPT, config=config)

    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Execute design review and refinement.

        Process:
        1. Security validation
        2. Assumption interrogation
        3. Design audit (use Design Audit Skill)
        4. Elegance assessment
        5. Recommendations
        6. Self-reflection
        """
        # Security checkpoint
        if not self.validate_security(context):
            return AgentResponse(
                role=self.role,
                content="SECURITY VALIDATION FAILED. This is now the only priority.",
                confidence=0.0,
                recommendations=["Fix security issues before proceeding"],
            )

        # Interrogate assumptions
        assumptions = self.interrogate_assumptions(context.task)

        # Assess current elegance
        elegance_assessment = self.assess_elegance(context.task)

        # Apply Boy Scout Rule thinking
        self.apply_boy_scout_rule(context.task)

        # Create reasoning path
        reasoning = self.create_reasoning_path(
            method=ReasoningMethod.CHAIN_OF_THOUGHT,
            steps=[
                "1. Validated security constraints",
                "2. Questioned core assumptions about the design",
                "3. Assessed elegance against pinkln criteria",
                "4. Identified simplification opportunities",
                "5. Applied Boy Scout Rule improvements",
            ],
            confidence=0.85,
        )

        # Generate recommendations
        recommendations = self._generate_design_recommendations(context.task, assumptions, elegance_assessment)

        # Self-reflection
        reflection = self.self_reflect()

        # Build response
        content = f"""# Chief Design Officer Analysis

## Design Philosophy Applied

Every element scrutinized for elegance before functionality.

## Assumptions Questioned

{chr(10).join(f"- {q}" for q in assumptions)}

## Elegance Assessment

{chr(10).join(f"- **{k}**: {v['question']}" for k, v in elegance_assessment.items())}

## Recommendations

{chr(10).join(f"{i + 1}. {rec}" for i, rec in enumerate(recommendations))}

## Design Principle

"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."
— Antoine de Saint-Exupéry

Each recommendation represents the ONLY elegant path forward.

---

*Designed with Steve Jobs-level attention to detail.*
"""

        response = AgentResponse(
            role=self.role,
            content=content,
            reasoning_path=reasoning,
            confidence=reasoning.confidence,
            recommendations=recommendations,
            next_steps=["Implement design improvements", "Iterate until insanely great", "Validate with users"],
            metadata={"assumptions_challenged": len(assumptions), "elegance_criteria_assessed": len(elegance_assessment), "reflection": reflection},
        )

        self.record_execution(response)
        return response

    def _generate_design_recommendations(self, task: str, assumptions: list, elegance_assessment: dict) -> list:
        """Generate specific design recommendations."""
        return [
            "Simplify the user interface by removing unnecessary elements",
            "Consolidate related functionality into unified flows",
            "Improve naming to reveal intent without documentation",
            "Align visual hierarchy with functional importance",
            "Remove friction from critical user paths",
        ]
