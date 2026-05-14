# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ReAct Orchestrator: Implements the Reason → Act → Observe → Reason loop.

Based on the ReAct framework (arxiv 2210.03629), this orchestrator enables
interpretable, grounded agent behavior through explicit reasoning traces,
tool actions, and observation feedback.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections.abc import Callable
import re
import json
from datetime import datetime

from kosmos.core.world_model import KosmosWorldModel


@dataclass
class ReActStep:
    """A single step in the ReAct loop."""

    iteration: int
    thought: str  # LLM's reasoning trace
    action: str | None  # Tool name to invoke
    action_input: dict[str, Any] | None  # Tool parameters
    observation: str | None  # Tool result / feedback
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "iteration": self.iteration,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReActResult:
    """Result from a complete ReAct execution."""

    success: bool
    final_answer: str | None
    steps: list[ReActStep]
    total_iterations: int
    termination_reason: str  # "goal_achieved", "max_iterations", "error"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "final_answer": self.final_answer,
            "steps": [step.to_dict() for step in self.steps],
            "total_iterations": self.total_iterations,
            "termination_reason": self.termination_reason,
            "error": self.error,
        }


class ReActOrchestrator:
    """
    Core ReAct loop orchestrator for Kosmos-pattern agents.

    Implements the Reason → Act → Observe cycle:
    1. REASON: LLM generates thought + selects action
    2. ACT: Execute tool/function call
    3. OBSERVE: Capture result and append to context
    4. Repeat until goal achieved or max iterations

    The orchestrator coordinates with the world model to maintain
    long-horizon state across multiple ReAct cycles.
    """

    # ReAct prompt template following arxiv 2210.03629 format
    REACT_PROMPT_TEMPLATE = """You are a research agent working towards the following goal:

GOAL: {goal}

You have access to the following tools:
{tool_descriptions}

Use the following format:

Thought: [Your reasoning about what to do next]
Action: [Tool name to use, or "Final Answer" if goal is achieved]
Action Input: [JSON object with tool parameters, or final answer text]

After each action, you will receive an observation. Then continue with another Thought/Action/Observation cycle.

When you have completed the goal, use:
Action: Final Answer
Action Input: [Your final answer/result]

Current world model state:
{world_model_summary}

Previous steps:
{previous_steps}

Begin!

Thought:"""

    def __init__(
        self,
        llm_client: Any,  # Vertex AI GenerativeModel instance
        tools: dict[str, Callable],
        world_model: KosmosWorldModel | None = None,
        max_iterations: int = 50,
        temperature: float = 0.7,
    ):
        """
        Initialize ReAct orchestrator.

        Args:
            llm_client: Vertex AI GenerativeModel instance
            tools: Dictionary of tool_name -> callable function
            world_model: Optional KosmosWorldModel for state tracking
            max_iterations: Maximum ReAct loop iterations (safety limit)
            temperature: LLM temperature for generation
        """
        self.llm_client = llm_client
        self.tools = tools
        self.world_model = world_model
        self.max_iterations = max_iterations
        self.temperature = temperature

    def execute_cycle(self, goal: str, context: list[ReActStep] | None = None) -> ReActResult:
        """
        Execute a complete ReAct cycle until goal is achieved or max iterations.

        Args:
            goal: Task description / research question
            context: Optional previous ReAct steps to continue from

        Returns:
            ReActResult with execution trace and outcome
        """
        steps = context or []
        iteration = len(steps)

        try:
            while iteration < self.max_iterations:
                # Build prompt with current context
                prompt = self._build_prompt(goal, steps)

                # REASON: Get LLM response
                response = self._generate_response(prompt)

                # Parse thought, action, action_input
                thought, action, action_input = self._parse_response(response)

                # Create step record
                step = ReActStep(
                    iteration=iteration,
                    thought=thought,
                    action=action,
                    action_input=action_input,
                    observation=None,  # Will be filled after action
                )

                # Check for termination
                if action == "Final Answer":
                    steps.append(step)
                    return ReActResult(
                        success=True,
                        final_answer=action_input.get("answer") if isinstance(action_input, dict) else action_input,
                        steps=steps,
                        total_iterations=iteration + 1,
                        termination_reason="goal_achieved",
                    )

                # ACT: Execute tool
                try:
                    observation = self._execute_tool(action, action_input)
                    step.observation = observation
                except Exception as e:
                    step.observation = f"Error executing {action}: {str(e)}"

                steps.append(step)
                iteration += 1

                # Update world model if available
                if self.world_model:
                    self._update_world_model(step)

            # Max iterations reached
            return ReActResult(
                success=False,
                final_answer=None,
                steps=steps,
                total_iterations=iteration,
                termination_reason="max_iterations",
            )

        except Exception as e:
            return ReActResult(
                success=False,
                final_answer=None,
                steps=steps,
                total_iterations=iteration,
                termination_reason="error",
                error=str(e),
            )

    def _build_prompt(self, goal: str, previous_steps: list[ReActStep]) -> str:
        """
        Build ReAct prompt with goal, tools, world model state, and history.

        Args:
            goal: Task description
            previous_steps: Previous ReAct steps in this cycle

        Returns:
            Formatted prompt string
        """
        # Format tool descriptions
        tool_descriptions = "\n".join([f"- {name}: {func.__doc__ or 'No description'}" for name, func in self.tools.items()])

        # Format previous steps
        steps_text = ""
        for step in previous_steps[-5:]:  # Show last 5 steps to avoid context bloat
            steps_text += f"\nThought: {step.thought}\n"
            if step.action:
                steps_text += f"Action: {step.action}\n"
                steps_text += f"Action Input: {json.dumps(step.action_input)}\n"
            if step.observation:
                steps_text += f"Observation: {step.observation}\n"

        # Get world model summary if available
        world_model_summary = ""
        if self.world_model:
            summary = self.world_model.get_summary()
            world_model_summary = f"""
Phase: {summary["phase"]}
Hypotheses: {summary["num_hypotheses"]} ({summary["num_tested_hypotheses"]} tested)
Analysis results: {summary["num_analysis_results"]}
Literature refs: {summary["num_literature_refs"]}
Top hypotheses:
{chr(10).join(["  - " + h["text"] + f" (confidence: {h['confidence']:.2f})" for h in summary["top_hypotheses"]])}
"""

        return self.REACT_PROMPT_TEMPLATE.format(
            goal=goal,
            tool_descriptions=tool_descriptions,
            world_model_summary=world_model_summary,
            previous_steps=steps_text or "[No previous steps]",
        )

    def _generate_response(self, prompt: str) -> str:
        """
        Generate LLM response using Vertex AI Gemini.

        Args:
            prompt: Formatted ReAct prompt

        Returns:
            LLM response text
        """
        # This will be implemented with actual Vertex AI call
        # For now, returns a placeholder that will be replaced
        # when vertex_client.py is implemented
        try:
            response = self.llm_client.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": 2048,
                },
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

    def _parse_response(self, response: str) -> tuple[str, str | None, Any | None]:
        """
        Parse LLM response to extract Thought, Action, Action Input.

        Args:
            response: Raw LLM response text

        Returns:
            Tuple of (thought, action, action_input)
        """
        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|\n*$)", response, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else response.strip()

        # Extract Action
        action_match = re.search(r"Action:\s*(.+?)(?=\nAction Input:|\n|$)", response)
        action = action_match.group(1).strip() if action_match else None

        # Extract Action Input
        action_input = None
        if action:
            input_match = re.search(r"Action Input:\s*(.+?)(?=\n\n|\n*$)", response, re.DOTALL)
            if input_match:
                input_text = input_match.group(1).strip()
                # Try to parse as JSON, fall back to raw string
                try:
                    action_input = json.loads(input_text)
                except json.JSONDecodeError:
                    action_input = input_text

        return thought, action, action_input

    def _execute_tool(self, action: str, action_input: Any) -> str:
        """
        Execute a tool and return observation.

        Args:
            action: Tool name
            action_input: Tool parameters

        Returns:
            Tool execution result as string
        """
        if action not in self.tools:
            return f"Error: Unknown tool '{action}'. Available tools: {list(self.tools.keys())}"

        tool_func = self.tools[action]

        try:
            # Call tool with input
            if isinstance(action_input, dict):
                result = tool_func(**action_input)
            else:
                result = tool_func(action_input)

            # Convert result to string for observation
            if isinstance(result, str):
                return result
            elif isinstance(result, dict) or isinstance(result, list):
                return json.dumps(result, indent=2)
            else:
                return str(result)

        except Exception as e:
            return f"Tool execution error: {str(e)}"

    def _update_world_model(self, step: ReActStep):
        """
        Update world model based on ReAct step results.

        This is where we bridge ReAct loop outputs to world model state.
        Extracts structured information from observations and updates
        hypotheses, analysis results, etc.

        Args:
            step: Completed ReAct step
        """
        if not self.world_model:
            return

        # Example: if action was "generate_hypothesis", add to world model
        if step.action == "generate_hypothesis" and step.observation:
            # Parse hypothesis from observation
            # (This is simplified - actual implementation would parse structured output)
            self.world_model.add_hypothesis(
                text=str(step.action_input.get("hypothesis_text", step.observation)),
                confidence=step.action_input.get("confidence", 0.5),
            )

        # Example: if action was "run_analysis", add result to world model
        elif step.action == "run_analysis" and step.observation:
            self.world_model.add_analysis_result(
                code=step.action_input.get("code", ""),
                outputs=[step.observation],
                hypothesis_id=step.action_input.get("hypothesis_id"),
            )

        # More sophisticated parsing would happen in real implementation
        # based on specific tool outputs and world model schema

    def get_tool_description(self, tool_name: str) -> str:
        """Get formatted description of a tool for prompting."""
        if tool_name in self.tools:
            return self.tools[tool_name].__doc__ or "No description available"
        return "Unknown tool"

    def add_tool(self, name: str, func: Callable):
        """
        Add a new tool to the orchestrator.

        Args:
            name: Tool name (will be used in Action: field)
            func: Callable tool function
        """
        self.tools[name] = func

    def remove_tool(self, name: str):
        """Remove a tool from the orchestrator."""
        if name in self.tools:
            del self.tools[name]

    def __repr__(self) -> str:
        return (
            f"ReActOrchestrator(tools={list(self.tools.keys())}, "
            f"max_iterations={self.max_iterations}, "
            f"has_world_model={self.world_model is not None})"
        )
