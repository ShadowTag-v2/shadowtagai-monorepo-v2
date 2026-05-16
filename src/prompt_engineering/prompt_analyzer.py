# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Prompt Analyzer.

Analyzes prompts for quality metrics and provides optimization suggestions.
"""

import re
from dataclasses import dataclass


@dataclass
class AnalysisReport:
  """Prompt analysis report."""

  token_estimate: int
  word_count: int
  sentence_count: int
  avg_sentence_length: float
  complexity_score: float  # 0.0 (simple) to 1.0 (complex)
  clarity_score: float  # 0.0 (unclear) to 1.0 (clear)
  suggestions: list[str]
  estimated_cost_usd: float
  estimated_response_time_sec: float


class PromptAnalyzer:
  """Analyzes prompts for quality and efficiency."""

  # Token cost per 1M tokens (approximate, model-dependent)
  TOKEN_COST_INPUT = 3.00 / 1_000_000  # $3 per 1M input tokens (Gemini 2.0)
  TOKEN_COST_OUTPUT = 15.00 / 1_000_000  # $15 per 1M output tokens

  def __init__(self, model: str = "gemini-2.0-pro"):
    """
    Initialize analyzer.

    Args:
        model: Target model for cost/performance estimates
    """
    self.model = model

  def analyze(self, prompt: str, expected_output_tokens: int = 1000) -> AnalysisReport:
    """
    Analyze prompt quality and provide optimization suggestions.

    Args:
        prompt: The prompt text to analyze
        expected_output_tokens: Expected length of model response

    Returns:
        AnalysisReport with metrics and suggestions
    """
    # Basic metrics
    words = prompt.split()
    word_count = len(words)
    token_estimate = int(word_count * 1.3)  # Rough approximation

    sentences = [s.strip() for s in re.split(r"[.!?]+", prompt) if s.strip()]
    sentence_count = len(sentences)
    avg_sentence_length = word_count / max(sentence_count, 1)

    # Complexity score (based on avg sentence length and word variety)
    unique_words = len(set(word.lower() for word in words))
    lexical_diversity = unique_words / max(word_count, 1)

    complexity_score = min(
      1.0,
      (
        (avg_sentence_length / 30) * 0.5  # Long sentences = complex
        + (1 - lexical_diversity) * 0.5  # Low diversity = repetitive/simple
      ),
    )

    # Clarity score (based on structure and directness)
    clarity_score = self._calculate_clarity(prompt, avg_sentence_length)

    # Cost estimate
    input_cost = token_estimate * self.TOKEN_COST_INPUT
    output_cost = expected_output_tokens * self.TOKEN_COST_OUTPUT
    total_cost = input_cost + output_cost

    # Response time estimate (very rough)
    estimated_time = (token_estimate + expected_output_tokens) / 100  # ~100 tokens/sec

    # Generate suggestions
    suggestions = self._generate_suggestions(
      prompt, word_count, avg_sentence_length, complexity_score, clarity_score
    )

    return AnalysisReport(
      token_estimate=token_estimate,
      word_count=word_count,
      sentence_count=sentence_count,
      avg_sentence_length=avg_sentence_length,
      complexity_score=complexity_score,
      clarity_score=clarity_score,
      suggestions=suggestions,
      estimated_cost_usd=total_cost,
      estimated_response_time_sec=estimated_time,
    )

  def _calculate_clarity(self, prompt: str, avg_sentence_length: float) -> float:
    """Calculate clarity score (0.0 to 1.0)."""
    score = 1.0

    # Penalize very long sentences
    if avg_sentence_length > 30:
      score -= 0.3
    elif avg_sentence_length > 20:
      score -= 0.1

    # Reward structure
    has_sections = bool(re.search(r"^\s*[A-Z]+:", prompt, re.MULTILINE))
    if has_sections:
      score += 0.1

    # Reward lists
    has_lists = bool(re.search(r"^\s*[-*•\d+\.]\s", prompt, re.MULTILINE))
    if has_lists:
      score += 0.1

    # Penalize passive voice (rough heuristic)
    passive_indicators = [" is ", " are ", " was ", " were ", " been ", " being "]
    passive_count = sum(prompt.count(p) for p in passive_indicators)
    if passive_count > len(prompt.split()) * 0.1:
      score -= 0.2

    return max(0.0, min(1.0, score))

  def _generate_suggestions(
    self,
    prompt: str,
    word_count: int,
    avg_sentence_length: float,
    complexity_score: float,
    clarity_score: float,
  ) -> list[str]:
    """Generate optimization suggestions."""
    suggestions = []

    # Word count
    if word_count > 500:
      suggestions.append(
        f"Prompt is long ({word_count} words). Consider reducing to <300 for faster responses and lower costs (KERNEL: Keep it Simple)"
      )

    # Sentence length
    if avg_sentence_length > 30:
      suggestions.append(
        f"Average sentence length is high ({avg_sentence_length:.1f} words). Break into shorter sentences for better clarity"
      )

    # Complexity
    if complexity_score > 0.7:
      suggestions.append(
        "High complexity detected. Simplify language and structure for better results"
      )

    # Clarity
    if clarity_score < 0.5:
      suggestions.append(
        "Low clarity score. Add section headers (CONTEXT, TASK, CONSTRAINTS, OUTPUT) and use bullet points (KERNEL: Logical Structure)"
      )

    # Check for KERNEL violations
    if not self._has_verification_criteria(prompt):
      suggestions.append(
        "No verification criteria found. Add explicit success criteria (KERNEL: Easy to Verify)"
      )

    if self._has_temporal_references(prompt):
      suggestions.append(
        "Temporal references detected ('current', 'latest'). Use specific versions/dates for reproducibility (KERNEL: Reproducible Results)"
      )

    if not self._has_constraints(prompt):
      suggestions.append(
        "No constraints specified. Add what NOT to do, limits, and bounds (KERNEL: Explicit Constraints)"
      )

    # If no suggestions, provide positive feedback
    if not suggestions:
      suggestions.append(
        "Prompt looks well-structured! Consider validating with KernelValidator for detailed KERNEL compliance check"
      )

    return suggestions

  def _has_verification_criteria(self, prompt: str) -> bool:
    """Check if prompt has verification criteria."""
    keywords = ["verify", "validate", "check", "ensure", "success criteria"]
    return any(kw in prompt.lower() for kw in keywords)

  def _has_temporal_references(self, prompt: str) -> bool:
    """Check for temporal references."""
    temporal = ["current", "latest", "recent", "modern", "new"]
    return any(t in prompt.lower() for t in temporal)

  def _has_constraints(self, prompt: str) -> bool:
    """Check for explicit constraints."""
    keywords = ["constraint", "must", "should not", "avoid", "limit", "maximum"]
    return any(kw in prompt.lower() for kw in keywords)

  def compare_prompts(
    self, prompt1: str, prompt2: str, labels: list[str] | None = None
  ) -> dict:
    """
    Compare two prompts side-by-side.

    Args:
        prompt1: First prompt
        prompt2: Second prompt
        labels: Optional labels for prompts (default: ["Prompt 1", "Prompt 2"])

    Returns:
        Comparison report dictionary
    """
    if labels is None:
      labels = ["Prompt 1", "Prompt 2"]

    analysis1 = self.analyze(prompt1)
    analysis2 = self.analyze(prompt2)

    return {
      "labels": labels,
      "prompts": [prompt1, prompt2],
      "analyses": [analysis1, analysis2],
      "comparison": {
        "token_difference": analysis2.token_estimate - analysis1.token_estimate,
        "cost_difference_usd": analysis2.estimated_cost_usd
        - analysis1.estimated_cost_usd,
        "time_difference_sec": analysis2.estimated_response_time_sec
        - analysis1.estimated_response_time_sec,
        "clarity_improvement": analysis2.clarity_score - analysis1.clarity_score,
        "complexity_change": analysis2.complexity_score - analysis1.complexity_score,
      },
      "winner": self._determine_winner(analysis1, analysis2, labels),
    }

  def _determine_winner(
    self, a1: AnalysisReport, a2: AnalysisReport, labels: list[str]
  ) -> str:
    """Determine which prompt is better overall."""
    # Score based on clarity, simplicity (low complexity), and efficiency
    score1 = a1.clarity_score + (1 - a1.complexity_score) - (a1.token_estimate / 1000)
    score2 = a2.clarity_score + (1 - a2.complexity_score) - (a2.token_estimate / 1000)

    if score2 > score1:
      return f"{labels[1]} (better clarity and efficiency)"
    elif score1 > score2:
      return f"{labels[0]} (better clarity and efficiency)"
    else:
      return "Tie"
