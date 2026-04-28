#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Loop Agent: Architect/Critic/Refiner pattern
Based on Google Cloud ADK Loop Agent architecture

Implements iterative refinement until critic is satisfied.

Part of 4-Module Agent Stack
Cost: ~$0.01-0.03/iteration (via minions)
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import requests


class LoopStatus(Enum):
    """Loop execution status."""

    INITIALIZING = "initializing"
    ARCHITECTING = "architecting"
    CRITIQUING = "critiquing"
    REFINING = "refining"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class LoopState:
    """State management for loop iterations."""

    current_doc: str = ""
    feedback: str = ""
    iteration: int = 0
    max_iterations: int = 5
    is_complete: bool = False
    status: LoopStatus = LoopStatus.INITIALIZING
    history: list[dict[str, Any]] = field(default_factory=list)

    def record(self, phase: str, content: str):
        """Record phase output to history."""
        self.history.append(
            {
                "iteration": self.iteration,
                "phase": phase,
                "content": content[:2000],  # Truncate for memory
            },
        )


class LoopAgent:
    """Architect/Critic/Refiner loop using minions backend.

    Flow:
    1. Architect: Initial design based on requirements
    2. Loop until satisfied:
       a. Critic: Evaluate design, provide feedback
       b. Refiner: Incorporate feedback into design
    3. Exit when: no feedback OR max iterations reached
    """

    minionS_URL = os.environ.get("minionS_URL", "http://localhost:8600")  # noqa: SIM112

    # Prompts for each agent role
    ARCHITECT_PROMPT = """You are a senior cloud architect. Design a solution for:

{requirement}

Include:
1. Architecture diagram (ASCII)
2. Components and services
3. Data flow
4. Security considerations
5. Cost estimate (low/medium/high)
6. Implementation steps

Use only Google Cloud services where applicable.
Output in structured markdown format.
"""

    CRITIC_PROMPT = """You are a senior technical reviewer. Evaluate this architecture:

{architecture}

Original requirement: {requirement}

Check for:
1. Does it meet all requirements?
2. Security gaps or vulnerabilities?
3. Cost optimization opportunities?
4. Scalability concerns?
5. Missing error handling?
6. Google Cloud best practices?

If the architecture is APPROVED, respond with exactly:
APPROVED: [one line summary]

If changes are needed, respond with:
FEEDBACK: [numbered list of required changes]
"""

    REFINER_PROMPT = """You are a senior cloud architect refining a design.

Current Architecture:
{architecture}

Feedback to Address:
{feedback}

Revise the architecture to address ALL feedback points.
Maintain the same structure but incorporate improvements.
Explain what changed for each feedback item.
"""

    def __init__(self, max_iterations: int = 5):
        """Initialize loop agent."""
        self.state = LoopState(max_iterations=max_iterations)

    def _call_minions(self, prompt: str, tier: str = "task") -> str:
        """Call minions API."""
        endpoint = f"{self.minionS_URL}/{tier}"

        try:
            response = requests.post(endpoint, json={"prompt": prompt}, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", str(result))

        except requests.RequestException as e:
            print(f"minions error: {e}")
            return f"Error: {e!s}"

    def architect(self, requirement: str) -> str:
        """Initial architecture design (Stage 1)."""
        print("///▞ LOOP AGENT :: Architecting solution...")
        self.state.status = LoopStatus.ARCHITECTING

        prompt = self.ARCHITECT_PROMPT.format(requirement=requirement)
        self.state.current_doc = self._call_minions(prompt, "task")
        self.state.record("architect", self.state.current_doc)

        return self.state.current_doc

    def critic(self, requirement: str) -> str:
        """Evaluate architecture, provide feedback (Stage 2a)."""
        print(f"///▞ LOOP AGENT :: Critic evaluating (iteration {self.state.iteration})...")
        self.state.status = LoopStatus.CRITIQUING

        prompt = self.CRITIC_PROMPT.format(
            architecture=self.state.current_doc,
            requirement=requirement,
        )

        # Use governance endpoint for critical evaluation
        self.state.feedback = self._call_minions(prompt, "governance")
        self.state.record("critic", self.state.feedback)

        # Check if approved
        feedback_lower = self.state.feedback.lower()
        if "approved:" in feedback_lower or "approved -" in feedback_lower:
            self.state.is_complete = True
            print("///▞ LOOP AGENT :: Architecture APPROVED")

        return self.state.feedback

    def refiner(self) -> str:
        """Refine architecture based on feedback (Stage 2b)."""
        print("///▞ LOOP AGENT :: Refining based on feedback...")
        self.state.status = LoopStatus.REFINING

        prompt = self.REFINER_PROMPT.format(
            architecture=self.state.current_doc,
            feedback=self.state.feedback,
        )

        self.state.current_doc = self._call_minions(prompt, "task")
        self.state.iteration += 1
        self.state.record("refiner", self.state.current_doc)

        return self.state.current_doc

    def run(self, requirement: str) -> dict[str, Any]:
        """Execute the full Architect/Critic/Refiner loop.

        Returns:
            dict with final architecture, iteration count, and status

        """
        print(f"///▞ LOOP AGENT :: Starting (max {self.state.max_iterations} iterations)")

        # Stage 1: Initial architecture
        self.architect(requirement)

        # Stage 2: Refinement loop
        while not self.state.is_complete and self.state.iteration < self.state.max_iterations:
            self.critic(requirement)

            if not self.state.is_complete:
                self.refiner()

        # Determine final status
        if self.state.is_complete:
            self.state.status = LoopStatus.COMPLETE
            print(f"///▞ LOOP AGENT :: Complete after {self.state.iteration} iteration(s)")
        else:
            self.state.status = LoopStatus.FAILED
            print("///▞ LOOP AGENT :: Max iterations reached without approval")

        return {
            "architecture": self.state.current_doc,
            "iterations": self.state.iteration,
            "status": self.state.status.value,
            "approved": self.state.is_complete,
            "final_feedback": self.state.feedback,
            "history": self.state.history,
        }

    def get_summary(self) -> str:
        """Generate markdown summary of the loop execution."""
        status_emoji = "✅" if self.state.is_complete else "⚠️"

        summary = f"""# Loop Agent Summary

{status_emoji} **Status**: {self.state.status.value}
**Iterations**: {self.state.iteration}/{self.state.max_iterations}
**Approved**: {self.state.is_complete}

## Iteration History
"""
        for entry in self.state.history:
            summary += f"\n### Iteration {entry['iteration']} - {entry['phase'].title()}\n"
            summary += f"```\n{entry['content'][:500]}...\n```\n"

        return summary


# Standalone execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: loop_agent.py '<requirement>'")
        print("Example: loop_agent.py 'Design a serverless API for image processing'")
        sys.exit(1)

    requirement = " ".join(sys.argv[1:])

    agent = LoopAgent(max_iterations=3)
    result = agent.run(requirement)

    print("\n" + "=" * 60)
    print("FINAL ARCHITECTURE")
    print("=" * 60)
    print(result["architecture"])
    print("\n" + agent.get_summary())
