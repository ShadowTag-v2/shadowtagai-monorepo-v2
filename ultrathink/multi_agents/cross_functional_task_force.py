# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Cross-Functional Task Force

Coordinates multiple chief officers working in concert on holistic challenges.
"""

from typing import Dict, Any, Optional
from ..core.types import AgentContext, AgentResponse, AgentRole, UltrathinkConfig


class CrossFunctionalTaskForce:
    """
    Cross-Functional Task Force

    Coordinates CDO, Chief Architect, CWO, CRO, CXO working together.
    Best for: Major strategic initiatives, product launches, transformations.
    """

    def __init__(self, config: UltrathinkConfig | None = None):
        self.config = config or UltrathinkConfig()
        self.agents = {}

    def register_agent(self, role: AgentRole, agent: Any) -> None:
        """Register an agent with the task force."""
        self.agents[role] = agent

    async def execute_mission(self, context: AgentContext) -> dict[str, AgentResponse]:
        """
        Execute coordinated mission across all agents.

        Handoff chain:
        1. CDO audits design
        2. Architect scales it
        3. CWO monetizes it
        4. CRO validates robustness
        5. CXO polishes final delivery

        Returns:
            Dictionary of responses from each agent
        """
        responses = {}

        # Phase 1: Design (CDO)
        if AgentRole.CDO in self.agents:
            cdo_response = await self.agents[AgentRole.CDO].execute(context)
            responses[AgentRole.CDO] = cdo_response

            # Update context with CDO insights
            context.metadata["cdo_insights"] = cdo_response.content

        # Phase 2: Architecture (Chief Architect)
        if AgentRole.ARCHITECT in self.agents:
            architect_response = await self.agents[AgentRole.ARCHITECT].execute(context)
            responses[AgentRole.ARCHITECT] = architect_response

            context.metadata["architecture"] = architect_response.content

        # Phase 3: Monetization (CWO)
        if AgentRole.CWO in self.agents:
            cwo_response = await self.agents[AgentRole.CWO].execute(context)
            responses[AgentRole.CWO] = cwo_response

            context.metadata["monetization"] = cwo_response.content

        # Phase 4: Validation (CRO)
        if AgentRole.CRO in self.agents:
            cro_response = await self.agents[AgentRole.CRO].execute(context)
            responses[AgentRole.CRO] = cro_response

            context.metadata["validation"] = cro_response.content

        # Phase 5: Final Polish (CXO)
        if AgentRole.CXO in self.agents:
            cxo_response = await self.agents[AgentRole.CXO].execute(context)
            responses[AgentRole.CXO] = cxo_response

        return responses

    def synthesize_responses(self, responses: dict[AgentRole, AgentResponse]) -> str:
        """Synthesize all agent responses into unified deliverable."""
        synthesis = """# Cross-Functional Task Force Report

## Mission Completed

All chief officers have contributed their expertise.

"""
        for role, response in responses.items():
            synthesis += f"""
### {role.value.upper()}

{response.content}

---

"""

        synthesis += """
## Integrated Recommendation

The task force recommends proceeding with the synthesized plan above.
All aspects (design, architecture, monetization, validation, experience) have been optimized.

---

*Coordinated by the Cross-Functional Task Force for holistic excellence.*
"""
        return synthesis
