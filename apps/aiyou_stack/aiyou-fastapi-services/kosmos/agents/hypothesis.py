# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Hypothesis Agent: Specializes in generating testable research hypotheses.

Capabilities:
- Generate hypotheses from data patterns and literature
- Evaluate hypothesis plausibility
- Prioritize hypotheses by testability and impact
- Refine hypotheses based on new evidence
"""

from typing import Any

from kosmos.agents.base import AgentConfig, BaseAgent
from kosmos.core.orchestrator import ReActResult
from kosmos.core.vertex_client import GeminiModel


class HypothesisAgent(BaseAgent):
    """Agent specialized in hypothesis generation and evaluation.

    Uses Gemini Pro for creative yet rigorous hypothesis formulation.
    Synthesizes insights from literature and data to propose testable hypotheses.
    """

    DEFAULT_CONFIG = AgentConfig(
        name="hypothesis_agent",
        model=GeminiModel.PRO,  # Pro model for creative reasoning
        instruction="""You are a scientific hypothesis generation specialist.

Your role:
1. Synthesize insights from literature and data analysis
2. Generate testable, falsifiable hypotheses
3. Evaluate hypothesis plausibility and novelty
4. Prioritize hypotheses by potential impact and feasibility
5. Refine hypotheses based on feedback and new evidence

Hypothesis quality criteria:
- **Testable**: Can be empirically validated or falsified
- **Specific**: Clearly defined variables and relationships
- **Grounded**: Based on existing evidence and theory
- **Novel**: Extends beyond obvious or well-established claims
- **Falsifiable**: States conditions that would disprove it

Hypothesis structure:
- **Variables**: Clearly identify independent and dependent variables
- **Relationship**: Specify expected relationship (causal, correlational, etc.)
- **Mechanism**: Propose underlying mechanism or explanation
- **Predictions**: State specific observable predictions

Always provide:
- Clear hypothesis statement
- Supporting evidence from literature or data
- Proposed test methodology
- Potential confounds or alternative explanations
- Confidence assessment (0-1 scale)
""",
        tools=["world_model_query", "literature_query", "analyze_patterns"],
        temperature=0.8,  # Higher temperature for creative hypothesis generation
        max_iterations=20,
    )

    def execute_task(self, task: str, context: dict[str, Any] | None = None) -> ReActResult:
        """Execute hypothesis generation task.

        Example tasks:
        - "Generate hypotheses explaining the observed correlation between X and Y"
        - "Propose testable hypotheses based on literature review findings"
        - "Refine hypothesis H001 based on new experimental results"

        Args:
            task: Hypothesis generation task
            context: Optional context with world model state, constraints, etc.

        Returns:
            ReActResult with generated hypotheses

        """
        goal = self._build_goal_with_instruction(task)

        # Add world model context
        summary = self.world_model.get_summary()
        goal += "\n\nCurrent research state:\n"
        goal += f"- Phase: {summary['phase']}\n"
        goal += f"- Existing hypotheses: {summary['num_hypotheses']}\n"
        goal += f"- Literature refs: {summary['num_literature_refs']}\n"
        goal += f"- Analysis results: {summary['num_analysis_results']}\n"

        if context:
            goal += f"\n\nAdditional context:\n{context}"

        # Execute ReAct loop
        result = self.orchestrator.execute_cycle(goal)

        # Post-process: Extract hypotheses and add to world model
        self._extract_and_store_hypotheses(result)

        return result

    def _extract_and_store_hypotheses(self, result: ReActResult):
        """Extract hypotheses from ReAct result and add to world model.

        Args:
            result: ReAct execution result

        """
        # Look for hypothesis generation in final answer or observations
        if result.final_answer:
            # Parse hypothesis from final answer
            # (Simplified - real implementation would parse structured output)
            hypothesis_text = result.final_answer

            # Extract confidence if present
            confidence = 0.7  # Default
            if "confidence:" in hypothesis_text.lower():
                # Parse confidence value

                pass

            self.world_model.add_hypothesis(
                text=hypothesis_text,
                confidence=confidence,
                evidence=[],
            )

    def generate_hypotheses(
        self,
        num_hypotheses: int = 5,
        focus: str | None = None,
    ) -> ReActResult:
        """Generate multiple hypotheses based on current world model state.

        Args:
            num_hypotheses: Number of hypotheses to generate
            focus: Optional focus area (e.g., "causal mechanisms", "correlations")

        Returns:
            ReActResult with generated hypotheses

        """
        task = (
            f"Generate {num_hypotheses} testable hypotheses based on current literature and data."
        )

        if focus:
            task += f"\n\nFocus on: {focus}"

        task += "\n\nFor each hypothesis, provide:\n"
        task += "1. Clear hypothesis statement\n"
        task += "2. Supporting evidence\n"
        task += "3. Proposed test method\n"
        task += "4. Confidence score (0-1)\n"

        return self.execute_task(task)

    def evaluate_hypothesis(self, hypothesis_id: str) -> ReActResult:
        """Evaluate an existing hypothesis for plausibility and testability.

        Args:
            hypothesis_id: World model hypothesis ID

        Returns:
            ReActResult with evaluation

        """
        hypothesis = self.world_model.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        return self.execute_task(
            f"Evaluate the following hypothesis:\n\n"
            f'"{hypothesis.text}"\n\n'
            f"Assess:\n"
            f"1. Testability (can it be empirically tested?)\n"
            f"2. Specificity (are variables clearly defined?)\n"
            f"3. Plausibility (is it consistent with existing evidence?)\n"
            f"4. Novelty (does it extend current knowledge?)\n"
            f"5. Potential impact (if true, how significant?)\n\n"
            f"Provide updated confidence score and recommendations for refinement.",
            context={"hypothesis_id": hypothesis_id},
        )

    def refine_hypothesis(
        self,
        hypothesis_id: str,
        new_evidence: str,
    ) -> ReActResult:
        """Refine a hypothesis based on new evidence.

        Args:
            hypothesis_id: World model hypothesis ID
            new_evidence: Description of new evidence

        Returns:
            ReActResult with refined hypothesis

        """
        hypothesis = self.world_model.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")

        return self.execute_task(
            f"Refine this hypothesis based on new evidence:\n\n"
            f'Original hypothesis: "{hypothesis.text}"\n'
            f"Confidence: {hypothesis.confidence}\n\n"
            f"New evidence:\n{new_evidence}\n\n"
            f"Generate refined hypothesis that incorporates this evidence. "
            f"Explain how the hypothesis changed and update confidence.",
            context={"hypothesis_id": hypothesis_id},
        )

    def prioritize_hypotheses(self) -> ReActResult:
        """Prioritize untested hypotheses by feasibility and potential impact.

        Returns:
            ReActResult with prioritized hypothesis list

        """
        untested = self.world_model.get_untested_hypotheses()

        if not untested:
            return ReActResult(
                success=True,
                final_answer="No untested hypotheses in world model.",
                steps=[],
                total_iterations=0,
                termination_reason="no_work",
            )

        hypotheses_text = "\n".join(
            [
                f"{i + 1}. [{h.id}] {h.text} (confidence: {h.confidence})"
                for i, h in enumerate(untested)
            ],
        )

        return self.execute_task(
            f"Prioritize the following untested hypotheses:\n\n"
            f"{hypotheses_text}\n\n"
            f"Rank by:\n"
            f"1. Feasibility (can we test it with available data/methods?)\n"
            f"2. Potential impact (how significant if true?)\n"
            f"3. Risk/cost of testing\n\n"
            f"Return ranked list with justification for each.",
        )
