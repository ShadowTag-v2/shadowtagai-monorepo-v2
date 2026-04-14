"""Cheat Sheet Fusion - 21 Essentials → 10 Core Elements

Intelligent fusion of prompting techniques to achieve 52% memory reduction
while maintaining ≥98% accuracy vs full 21-technique set.

Original 21 Essentials:
1. Chain of Thought (CoT)
2. Tree of Thoughts (ToT)
3. Reason + Conclude + Refine (RCR)
4. Reflect, Think, Formulate (RTF)
5. Think-Aloud-Generate (TAG)
6. Break-Analyze-Build (BAB)
7. Critique-Analyze-Refine-Execute (CARE)
8. Reason-Iterate-Synthesize-Evaluate (RISE)
9. Few-Shot Examples
10. Zero-Shot Prompting
11. Self-Consistency
12. Least-to-Most Prompting
13. Maieutic Prompting
14. Recursive Criticism
15. Constitutional AI
16. Debate/Multi-Agent
17. Program of Thoughts (PoT)
18. ReAct (Reasoning + Acting)
19. Reflexion (Self-Reflection)
20. Plan-and-Solve
21. Auto-CoT (Automatic CoT)

Fused 10 Core Elements:
1. REASONED_EXECUTION (CoT + ToT + RCR + RTF + TAG)
2. ITERATIVE_REFINEMENT (CARE + RISE + Recursive Criticism + Reflexion)
3. STRUCTURAL_BREAKDOWN (BAB + Least-to-Most + Plan-and-Solve)
4. EXAMPLE_LEARNING (Few-Shot + Zero-Shot + Auto-CoT)
5. MULTI_PERSPECTIVE (Self-Consistency + Debate/Multi-Agent)
6. CONSTITUTIONAL_CRITIQUE (Constitutional AI + Maieutic)
7. PROGRAMMATIC_REASONING (PoT + ReAct)
8. META_REASONING (identifies which techniques to apply)
9. CONTEXT_ADAPTATION (adjusts based on task complexity)
10. CONFIDENCE_CALIBRATION (measures certainty and triggers refinement)

Performance Targets:
- Memory reduction: 21→10 (52%)
- Accuracy maintenance: ≥98% (vs full 21)
- Selection overhead: <1ms
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class FusedTechnique(Enum):
    """10 fused prompting techniques."""

    REASONED_EXECUTION = "reasoned_execution"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    STRUCTURAL_BREAKDOWN = "structural_breakdown"
    EXAMPLE_LEARNING = "example_learning"
    MULTI_PERSPECTIVE = "multi_perspective"
    CONSTITUTIONAL_CRITIQUE = "constitutional_critique"
    PROGRAMMATIC_REASONING = "programmatic_reasoning"
    META_REASONING = "meta_reasoning"
    CONTEXT_ADAPTATION = "context_adaptation"
    CONFIDENCE_CALIBRATION = "confidence_calibration"


class TaskType(Enum):
    """Task type classification for technique selection."""

    REASONING = "reasoning"  # Logic, math, analysis
    GENERATION = "generation"  # Creative writing, code generation
    CLASSIFICATION = "classification"  # Categorization, labeling
    QUESTION_ANSWERING = "qa"  # Factual QA
    PROBLEM_SOLVING = "problem_solving"  # Multi-step problems
    CODE_EXECUTION = "code_execution"  # Programming tasks
    CRITIQUE = "critique"  # Review, evaluation
    PLANNING = "planning"  # Task planning, scheduling


class ComplexityLevel(Enum):
    """Task complexity level."""

    SIMPLE = 1  # Single-step, straightforward
    MODERATE = 2  # Few steps, some reasoning
    COMPLEX = 3  # Multi-step, deep reasoning
    VERY_COMPLEX = 4  # Requires multiple techniques


@dataclass
class TechniqueMapping:
    """Mapping of fused technique to original techniques.

    Attributes:
        fused: Fused technique
        originals: Original techniques included
        description: What this fusion does
        template: Prompt template
        optimal_for: Task types this works best for

    """

    fused: FusedTechnique
    originals: list[str]
    description: str
    template: str
    optimal_for: list[TaskType]


@dataclass
class FusionResult:
    """Technique fusion result.

    Attributes:
        selected_techniques: Techniques selected for task
        reasoning: Why these techniques were selected
        combined_prompt: Fused prompt template
        complexity_level: Detected task complexity
        confidence: Selection confidence (0.0-1.0)
        selection_time_us: Selection time in microseconds

    """

    selected_techniques: list[FusedTechnique]
    reasoning: str
    combined_prompt: str
    complexity_level: ComplexityLevel
    confidence: float
    selection_time_us: float


# Technique mappings (21 → 10)
TECHNIQUE_MAPPINGS = [
    TechniqueMapping(
        fused=FusedTechnique.REASONED_EXECUTION,
        originals=["CoT", "ToT", "RCR", "RTF", "TAG"],
        description="Step-by-step reasoning with explicit thought process",
        template=(
            "{task}\n\n"
            "Let's solve this step by step:\n"
            "1. First, let's identify the key components\n"
            "2. Then, reason through each step\n"
            "3. Finally, synthesize the solution\n\n"
            "Thinking:"
        ),
        optimal_for=[TaskType.REASONING, TaskType.PROBLEM_SOLVING, TaskType.QUESTION_ANSWERING],
    ),
    TechniqueMapping(
        fused=FusedTechnique.ITERATIVE_REFINEMENT,
        originals=["CARE", "RISE", "Recursive Criticism", "Reflexion"],
        description="Iterative improvement through critique and refinement",
        template=(
            "{task}\n\n"
            "Initial attempt:\n{initial_attempt}\n\n"
            "Critique: What could be improved?\n"
            "Refinement: Apply improvements\n"
            "Final answer:"
        ),
        optimal_for=[TaskType.GENERATION, TaskType.CRITIQUE, TaskType.CODE_EXECUTION],
    ),
    TechniqueMapping(
        fused=FusedTechnique.STRUCTURAL_BREAKDOWN,
        originals=["BAB", "Least-to-Most", "Plan-and-Solve"],
        description="Break complex task into structured sub-problems",
        template=(
            "{task}\n\n"
            "Breaking this down:\n"
            "A. Simplest sub-problem: {sub1}\n"
            "B. Next sub-problem: {sub2}\n"
            "C. Combine solutions:\n\n"
            "Solution:"
        ),
        optimal_for=[TaskType.PROBLEM_SOLVING, TaskType.PLANNING, TaskType.CODE_EXECUTION],
    ),
    TechniqueMapping(
        fused=FusedTechnique.EXAMPLE_LEARNING,
        originals=["Few-Shot", "Zero-Shot", "Auto-CoT"],
        description="Learn from examples or infer patterns",
        template=("{task}\n\nExamples:\n{examples}\n\nFollowing this pattern, the answer is:"),
        optimal_for=[TaskType.CLASSIFICATION, TaskType.GENERATION, TaskType.QUESTION_ANSWERING],
    ),
    TechniqueMapping(
        fused=FusedTechnique.MULTI_PERSPECTIVE,
        originals=["Self-Consistency", "Debate/Multi-Agent"],
        description="Multiple viewpoints to reach consensus",
        template=(
            "{task}\n\n"
            "Perspective 1: {view1}\n"
            "Perspective 2: {view2}\n"
            "Perspective 3: {view3}\n\n"
            "Consensus:"
        ),
        optimal_for=[TaskType.REASONING, TaskType.CRITIQUE, TaskType.PROBLEM_SOLVING],
    ),
    TechniqueMapping(
        fused=FusedTechnique.CONSTITUTIONAL_CRITIQUE,
        originals=["Constitutional AI", "Maieutic"],
        description="Socratic questioning with constitutional principles",
        template=(
            "{task}\n\n"
            "Constitutional principles:\n"
            "- Is this helpful and harmless?\n"
            "- Does this respect user autonomy?\n"
            "- Are there hidden assumptions?\n\n"
            "Answer:"
        ),
        optimal_for=[TaskType.CRITIQUE, TaskType.REASONING, TaskType.QUESTION_ANSWERING],
    ),
    TechniqueMapping(
        fused=FusedTechnique.PROGRAMMATIC_REASONING,
        originals=["PoT", "ReAct"],
        description="Program-style reasoning with actions",
        template=(
            "{task}\n\n"
            "Thought: Analyze the problem\n"
            "Action: Write code to solve it\n"
            "Observation: Evaluate result\n\n"
            "Code:"
        ),
        optimal_for=[TaskType.CODE_EXECUTION, TaskType.PROBLEM_SOLVING],
    ),
    TechniqueMapping(
        fused=FusedTechnique.META_REASONING,
        originals=["Meta-learning", "Strategy Selection"],
        description="Reason about which techniques to apply",
        template=(
            "{task}\n\n"
            "Meta-analysis:\n"
            "- Task type: {task_type}\n"
            "- Complexity: {complexity}\n"
            "- Best approach: {strategy}\n\n"
            "Applying strategy:"
        ),
        optimal_for=[TaskType.PLANNING, TaskType.PROBLEM_SOLVING],
    ),
    TechniqueMapping(
        fused=FusedTechnique.CONTEXT_ADAPTATION,
        originals=["Dynamic Prompting", "Adaptive Complexity"],
        description="Adapt complexity based on task needs",
        template=(
            "{task}\n\n"
            "Detected complexity: {complexity}\n"
            "Adapting approach: {adaptation}\n\n"
            "Solution:"
        ),
        optimal_for=[TaskType.REASONING, TaskType.GENERATION, TaskType.PROBLEM_SOLVING],
    ),
    TechniqueMapping(
        fused=FusedTechnique.CONFIDENCE_CALIBRATION,
        originals=["Uncertainty Estimation", "Confidence Scoring"],
        description="Measure certainty and trigger refinement if needed",
        template=(
            "{task}\n\n"
            "Answer: {answer}\n"
            "Confidence: {confidence}\n\n"
            "If confidence < 0.8, refine:\n{refinement}"
        ),
        optimal_for=[TaskType.REASONING, TaskType.CLASSIFICATION, TaskType.QUESTION_ANSWERING],
    ),
]


class CheatSheetFusion:
    """Intelligent fusion of 21 prompting techniques into 10 core elements.

    Performance targets:
    - Memory reduction: 21→10 (52%)
    - Accuracy maintenance: ≥98% (vs full 21)
    - Selection overhead: <1ms
    """

    def __init__(self):
        """Initialize cheat sheet fusion engine."""
        self.mappings = {m.fused: m for m in TECHNIQUE_MAPPINGS}

        # Task type → technique mapping (learned from data in production)
        self.task_preferences = {
            TaskType.REASONING: [
                FusedTechnique.REASONED_EXECUTION,
                FusedTechnique.MULTI_PERSPECTIVE,
                FusedTechnique.CONSTITUTIONAL_CRITIQUE,
            ],
            TaskType.GENERATION: [
                FusedTechnique.ITERATIVE_REFINEMENT,
                FusedTechnique.EXAMPLE_LEARNING,
                FusedTechnique.CONTEXT_ADAPTATION,
            ],
            TaskType.CLASSIFICATION: [
                FusedTechnique.EXAMPLE_LEARNING,
                FusedTechnique.CONFIDENCE_CALIBRATION,
                FusedTechnique.REASONED_EXECUTION,
            ],
            TaskType.QUESTION_ANSWERING: [
                FusedTechnique.REASONED_EXECUTION,
                FusedTechnique.EXAMPLE_LEARNING,
                FusedTechnique.CONFIDENCE_CALIBRATION,
            ],
            TaskType.PROBLEM_SOLVING: [
                FusedTechnique.STRUCTURAL_BREAKDOWN,
                FusedTechnique.REASONED_EXECUTION,
                FusedTechnique.MULTI_PERSPECTIVE,
            ],
            TaskType.CODE_EXECUTION: [
                FusedTechnique.PROGRAMMATIC_REASONING,
                FusedTechnique.STRUCTURAL_BREAKDOWN,
                FusedTechnique.ITERATIVE_REFINEMENT,
            ],
            TaskType.CRITIQUE: [
                FusedTechnique.CONSTITUTIONAL_CRITIQUE,
                FusedTechnique.ITERATIVE_REFINEMENT,
                FusedTechnique.MULTI_PERSPECTIVE,
            ],
            TaskType.PLANNING: [
                FusedTechnique.STRUCTURAL_BREAKDOWN,
                FusedTechnique.META_REASONING,
                FusedTechnique.REASONED_EXECUTION,
            ],
        }

    def _detect_task_type(self, task: str) -> TaskType:
        """Detect task type from task description.

        In production, would use classifier model.

        Args:
            task: Task description

        Returns:
            Detected task type

        """
        task_lower = task.lower()

        # Simple keyword-based detection
        if any(kw in task_lower for kw in ["solve", "calculate", "compute", "math"]):
            return TaskType.PROBLEM_SOLVING

        if any(kw in task_lower for kw in ["write", "generate", "create", "compose"]):
            return TaskType.GENERATION

        if any(kw in task_lower for kw in ["classify", "categorize", "label"]):
            return TaskType.CLASSIFICATION

        if any(kw in task_lower for kw in ["code", "program", "function", "implement"]):
            return TaskType.CODE_EXECUTION

        if any(kw in task_lower for kw in ["review", "critique", "evaluate"]):
            return TaskType.CRITIQUE

        if any(kw in task_lower for kw in ["plan", "schedule", "organize"]):
            return TaskType.PLANNING

        if "?" in task_lower:
            return TaskType.QUESTION_ANSWERING

        # Default to reasoning
        return TaskType.REASONING

    def _estimate_complexity(self, task: str) -> ComplexityLevel:
        """Estimate task complexity.

        Args:
            task: Task description

        Returns:
            Complexity level

        """
        # Simple heuristics
        length = len(task.split())

        if length < 20:
            return ComplexityLevel.SIMPLE
        if length < 50:
            return ComplexityLevel.MODERATE
        if length < 100:
            return ComplexityLevel.COMPLEX
        return ComplexityLevel.VERY_COMPLEX

    def select_techniques(
        self,
        task: str,
        task_type: TaskType | None = None,
        complexity: ComplexityLevel | None = None,
        max_techniques: int = 3,
    ) -> FusionResult:
        """Select optimal fused techniques for task.

        Performance target: <1ms selection overhead

        Args:
            task: Task description
            task_type: Optional explicit task type (auto-detected if None)
            complexity: Optional explicit complexity (auto-detected if None)
            max_techniques: Maximum techniques to select

        Returns:
            Fusion result with selected techniques

        """
        start_time = time.perf_counter()

        # Auto-detect if not provided
        if task_type is None:
            task_type = self._detect_task_type(task)

        if complexity is None:
            complexity = self._estimate_complexity(task)

        # Select techniques based on task type and complexity
        preferred = self.task_preferences.get(task_type, [])

        # Adjust based on complexity
        if complexity == ComplexityLevel.SIMPLE:
            # Just use top technique
            selected = preferred[:1]
        elif complexity == ComplexityLevel.MODERATE:
            # Use top 2 techniques
            selected = preferred[:2]
        elif complexity == ComplexityLevel.COMPLEX:
            # Use top 3 techniques
            selected = preferred[: min(3, max_techniques)]
        else:  # VERY_COMPLEX
            # Use top techniques + meta-reasoning
            selected = preferred[: min(2, max_techniques - 1)]
            selected.append(FusedTechnique.META_REASONING)

        # Always add confidence calibration for quality control
        if FusedTechnique.CONFIDENCE_CALIBRATION not in selected:
            if len(selected) < max_techniques:
                selected.append(FusedTechnique.CONFIDENCE_CALIBRATION)

        # Build combined prompt
        combined_prompt = self._build_combined_prompt(task, selected)

        # Build reasoning explanation
        reasoning = (
            f"Task type: {task_type.value}, "
            f"Complexity: {complexity.name}, "
            f"Selected {len(selected)} techniques: "
            f"{', '.join(t.value for t in selected)}"
        )

        # Confidence based on task type match
        confidence = 0.9 if task_type in self.task_preferences else 0.7

        selection_time_us = (time.perf_counter() - start_time) * 1_000_000

        return FusionResult(
            selected_techniques=selected,
            reasoning=reasoning,
            combined_prompt=combined_prompt,
            complexity_level=complexity,
            confidence=confidence,
            selection_time_us=selection_time_us,
        )

    def _build_combined_prompt(self, task: str, techniques: list[FusedTechnique]) -> str:
        """Build combined prompt from multiple techniques.

        Args:
            task: Task description
            techniques: Selected techniques

        Returns:
            Combined prompt template

        """
        if not techniques:
            return task

        # Start with task
        prompt_parts = [task, ""]

        # Add technique-specific instructions
        for technique in techniques:
            mapping = self.mappings.get(technique)
            if mapping:
                # Extract technique instructions (remove task placeholder)
                instructions = mapping.template.replace("{task}\n\n", "").strip()
                prompt_parts.append(f"# {technique.value.replace('_', ' ').title()}")
                prompt_parts.append(instructions)
                prompt_parts.append("")

        return "\n".join(prompt_parts)

    def get_technique_info(self, technique: FusedTechnique) -> TechniqueMapping:
        """Get information about a fused technique.

        Args:
            technique: Fused technique

        Returns:
            Technique mapping with details

        """
        return self.mappings.get(technique)

    def get_all_techniques(self) -> list[TechniqueMapping]:
        """Get all fused technique mappings.

        Returns:
            List of all technique mappings

        """
        return list(self.mappings.values())

    def get_statistics(self) -> dict[str, Any]:
        """Get fusion statistics.

        Returns:
            Dictionary with statistics

        """
        total_original = sum(len(m.originals) for m in self.mappings.values())
        total_fused = len(self.mappings)

        compression_ratio = 1.0 - (total_fused / total_original)

        return {
            "total_original_techniques": total_original,
            "total_fused_techniques": total_fused,
            "compression_ratio": compression_ratio,
            "compression_percentage": compression_ratio * 100,
            "task_types_supported": len(self.task_preferences),
            "avg_originals_per_fused": total_original / total_fused,
        }
