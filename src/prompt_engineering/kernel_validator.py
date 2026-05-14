# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
KERNEL Framework Validator

Validates prompts against the KERNEL framework principles:
- K: Keep it Simple
- E: Easy to Verify
- R: Reproducible Results
- N: Narrow Scope
- E: Explicit Constraints
- L: Logical Structure
"""

from dataclasses import dataclass
from typing import List, Dict
import re


@dataclass
class KernelScore:
    """Individual KERNEL principle score."""

    principle: str
    score: float  # 0.0 to 1.0
    passed: bool
    feedback: list[str]
    recommendations: list[str]


@dataclass
class ValidationResult:
    """Overall KERNEL validation result."""

    overall_score: float  # 0.0 to 1.0
    passed: bool
    principle_scores: dict[str, KernelScore]
    summary: str
    token_estimate: int


class KernelValidator:
    """Validates prompts against KERNEL framework."""

    # Temporal keywords that violate Reproducible principle
    TEMPORAL_KEYWORDS = [
        "current",
        "latest",
        "recent",
        "modern",
        "new",
        "upcoming",
        "today",
        "now",
        "this year",
        "contemporary",
        "cutting-edge",
        "state-of-the-art",
        "trending",
    ]

    # Vague quality terms that violate Easy to Verify
    VAGUE_QUALITY_TERMS = [
        "better",
        "improve",
        "optimize",
        "enhance",
        "clean",
        "professional",
        "engaging",
        "user-friendly",
        "nice",
        "good",
        "quality",
        "efficient",
    ]

    # Structure section keywords
    STRUCTURE_SECTIONS = ["context", "task", "constraint", "output", "format", "input", "verify", "requirement"]

    def __init__(self, strict: bool = False):
        """
        Initialize validator.

        Args:
            strict: If True, require higher scores to pass (0.8 vs 0.6)
        """
        self.strict = strict
        self.pass_threshold = 0.8 if strict else 0.6

    def validate(self, prompt: str) -> ValidationResult:
        """
        Validate prompt against all KERNEL principles.

        Args:
            prompt: The prompt text to validate

        Returns:
            ValidationResult with scores and recommendations
        """
        scores = {}

        # Validate each principle
        scores["K"] = self._validate_keep_it_simple(prompt)
        scores["E1"] = self._validate_easy_to_verify(prompt)
        scores["R"] = self._validate_reproducible(prompt)
        scores["N"] = self._validate_narrow_scope(prompt)
        scores["E2"] = self._validate_explicit_constraints(prompt)
        scores["L"] = self._validate_logical_structure(prompt)

        # Calculate overall score
        overall = sum(s.score for s in scores.values()) / len(scores)
        passed = all(s.passed for s in scores.values())

        # Generate summary
        summary = self._generate_summary(overall, passed, scores)

        # Estimate tokens (rough approximation)
        token_estimate = len(prompt.split()) * 1.3

        return ValidationResult(overall_score=overall, passed=passed, principle_scores=scores, summary=summary, token_estimate=int(token_estimate))

    def _validate_keep_it_simple(self, prompt: str) -> KernelScore:
        """Validate K: Keep it Simple."""
        feedback = []
        recommendations = []
        score = 1.0

        # Check length (should be concise)
        word_count = len(prompt.split())
        if word_count > 500:
            score -= 0.3
            feedback.append(f"Prompt is verbose ({word_count} words)")
            recommendations.append("Reduce to <300 words; focus on one clear goal")
        elif word_count > 300:
            score -= 0.1
            feedback.append(f"Prompt is somewhat long ({word_count} words)")

        # Check for run-on sentences
        sentences = prompt.split(".")
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if avg_sentence_length > 30:
            score -= 0.2
            feedback.append("Sentences are too long (complex structure)")
            recommendations.append("Break into shorter, clearer sentences")

        # Check for clear goal statement
        goal_indicators = ["task:", "goal:", "objective:", "write", "create", "analyze"]
        has_goal = any(indicator in prompt.lower() for indicator in goal_indicators)
        if not has_goal:
            score -= 0.3
            feedback.append("No clear goal statement found")
            recommendations.append("Start with explicit task/goal statement")
        else:
            feedback.append("Clear goal statement present")

        return KernelScore(
            principle="K - Keep it Simple",
            score=max(0, score),
            passed=score >= self.pass_threshold,
            feedback=feedback,
            recommendations=recommendations,
        )

    def _validate_easy_to_verify(self, prompt: str) -> KernelScore:
        """Validate E: Easy to Verify."""
        feedback = []
        recommendations = []
        score = 1.0

        # Check for vague quality terms
        vague_found = [term for term in self.VAGUE_QUALITY_TERMS if term in prompt.lower()]
        if vague_found:
            score -= 0.3 * min(len(vague_found) / 3, 1.0)
            feedback.append(f"Vague quality terms found: {', '.join(vague_found[:3])}")
            recommendations.append("Replace with measurable criteria (e.g., '3 examples', '<50 lines')")

        # Check for verification/success criteria
        verification_keywords = ["verify", "validate", "success", "criteria", "check", "ensure", "must", "should"]
        has_verification = any(kw in prompt.lower() for kw in verification_keywords)
        if not has_verification:
            score -= 0.4
            feedback.append("No verification criteria found")
            recommendations.append("Add explicit success criteria or verification steps")
        else:
            feedback.append("Verification criteria present")

        # Check for quantifiable requirements
        has_numbers = bool(re.search(r"\d+", prompt))
        if not has_numbers:
            score -= 0.2
            feedback.append("No quantifiable requirements (numbers)")
            recommendations.append("Add specific quantities (e.g., 'include 3 examples')")

        return KernelScore(
            principle="E - Easy to Verify",
            score=max(0, score),
            passed=score >= self.pass_threshold,
            feedback=feedback,
            recommendations=recommendations,
        )

    def _validate_reproducible(self, prompt: str) -> KernelScore:
        """Validate R: Reproducible Results."""
        feedback = []
        recommendations = []
        score = 1.0

        # Check for temporal references
        temporal_found = [kw for kw in self.TEMPORAL_KEYWORDS if kw in prompt.lower()]
        if temporal_found:
            score -= 0.4 * min(len(temporal_found) / 3, 1.0)
            feedback.append(f"Temporal references found: {', '.join(temporal_found[:3])}")
            recommendations.append("Replace with specific versions/dates (e.g., 'Python 3.11', '2024 data')")
        else:
            feedback.append("No temporal references detected")

        # Check for version specifications
        version_pattern = r"(v?\d+\.\d+|version \d+|python \d|node \d)"
        has_versions = bool(re.search(version_pattern, prompt.lower()))
        if not has_versions:
            score -= 0.2
            feedback.append("No version specifications found")
            recommendations.append("Specify exact versions/dates for reproducibility")

        return KernelScore(
            principle="R - Reproducible Results",
            score=max(0, score),
            passed=score >= self.pass_threshold,
            feedback=feedback,
            recommendations=recommendations,
        )

    def _validate_narrow_scope(self, prompt: str) -> KernelScore:
        """Validate N: Narrow Scope."""
        feedback = []
        recommendations = []
        score = 1.0

        # Check for multiple deliverables
        deliverable_keywords = ["and", "also", "additionally", "plus", "as well as"]
        conjunction_count = sum(prompt.lower().count(kw) for kw in deliverable_keywords)
        if conjunction_count > 5:
            score -= 0.4
            feedback.append(f"Many conjunctions ({conjunction_count}), suggests multiple goals")
            recommendations.append("Split into separate prompts, one goal each")

        # Check for common multi-goal patterns
        multi_goal_patterns = [
            r"(write|create|build).*(and|also).*(write|create|build)",
            r"(code|implementation).*(and|also).*(test|documentation)",
            r"(api|backend).*(and|also).*(frontend|ui)",
        ]
        for pattern in multi_goal_patterns:
            if re.search(pattern, prompt.lower()):
                score -= 0.3
                feedback.append("Multiple goals detected (code + tests + docs)")
                recommendations.append("Use prompt chaining: separate prompts for each deliverable")
                break

        # Check for single primary verb
        action_verbs = ["write", "create", "build", "analyze", "design", "implement", "generate", "develop"]
        verb_count = sum(1 for verb in action_verbs if verb in prompt.lower())
        if verb_count > 2:
            score -= 0.2
            feedback.append(f"Multiple action verbs ({verb_count}), may lack focus")

        return KernelScore(
            principle="N - Narrow Scope", score=max(0, score), passed=score >= self.pass_threshold, feedback=feedback, recommendations=recommendations
        )

    def _validate_explicit_constraints(self, prompt: str) -> KernelScore:
        """Validate E: Explicit Constraints."""
        feedback = []
        recommendations = []
        score = 1.0

        # Check for constraint keywords
        constraint_keywords = ["constraint", "requirement", "must", "should not", "avoid", "do not", "maximum", "minimum", "limit", "only", "no"]
        constraint_count = sum(prompt.lower().count(kw) for kw in constraint_keywords)

        if constraint_count == 0:
            score -= 0.5
            feedback.append("No explicit constraints found")
            recommendations.append("Add constraints section: what NOT to do, limits, forbidden patterns")
        elif constraint_count < 3:
            score -= 0.2
            feedback.append("Few constraints specified")
            recommendations.append("Add more constraints for clarity")
        else:
            feedback.append(f"Good constraint coverage ({constraint_count} constraint keywords)")

        # Check for technical constraints
        tech_constraints = ["line", "function", "library", "dependency", "time", "memory", "size", "length"]
        has_tech_constraints = any(tc in prompt.lower() for tc in tech_constraints)
        if not has_tech_constraints:
            score -= 0.2
            feedback.append("No technical constraints (code limits, performance)")
            recommendations.append("Add technical bounds (e.g., '<50 lines', 'pandas only')")

        return KernelScore(
            principle="E - Explicit Constraints",
            score=max(0, score),
            passed=score >= self.pass_threshold,
            feedback=feedback,
            recommendations=recommendations,
        )

    def _validate_logical_structure(self, prompt: str) -> KernelScore:
        """Validate L: Logical Structure."""
        feedback = []
        recommendations = []
        score = 1.0

        # Check for section headers
        sections_found = [s for s in self.STRUCTURE_SECTIONS if s + ":" in prompt.lower() or s.upper() in prompt]

        if len(sections_found) == 0:
            score -= 0.5
            feedback.append("No structured sections found")
            recommendations.append("Use sections: CONTEXT, TASK, CONSTRAINTS, OUTPUT")
        elif len(sections_found) < 3:
            score -= 0.2
            feedback.append(f"Only {len(sections_found)} sections found")
            recommendations.append("Add missing sections for complete structure")
        else:
            feedback.append(f"Good structure: {len(sections_found)} sections present")

        # Check for clear formatting (bullets, numbers)
        has_bullets = bool(re.search(r"^\s*[-*•]", prompt, re.MULTILINE))
        has_numbers = bool(re.search(r"^\s*\d+\.", prompt, re.MULTILINE))

        if not (has_bullets or has_numbers):
            score -= 0.2
            feedback.append("No list formatting (bullets/numbers)")
            recommendations.append("Use bullets or numbered lists for clarity")

        return KernelScore(
            principle="L - Logical Structure",
            score=max(0, score),
            passed=score >= self.pass_threshold,
            feedback=feedback,
            recommendations=recommendations,
        )

    def _generate_summary(self, overall: float, passed: bool, scores: dict[str, KernelScore]) -> str:
        """Generate human-readable summary."""
        status = "PASSED" if passed else "NEEDS IMPROVEMENT"

        failing = [name for name, score in scores.items() if not score.passed]

        summary = f"KERNEL Validation: {status}\n"
        summary += f"Overall Score: {overall:.1%}\n\n"

        if failing:
            summary += f"Failing Principles: {', '.join(failing)}\n"
        else:
            summary += "All principles passed!\n"

        return summary
