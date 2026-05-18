# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""ScholarEval — 8-dimension quality framework for research discovery validation.

Evaluates AI-generated research discoveries across 8 quality dimensions
derived from the Uphillsnowball Master architecture (Notebook 516).

Dimensions:
    1. Novelty — Is this genuinely new or restating known results?
    2. Reproducibility — Can the finding be independently verified?
    3. Statistical Rigor — Are the methods and p-values valid?
    4. Citation Grounding — Are claims supported by real references?
    5. Logical Coherence — Does the argument flow without gaps?
    6. Practical Impact — Does the finding have real-world application?
    7. Ethical Compliance — No fabrication, bias, or harmful framing?
    8. Temporal Validity — Is this based on current (non-retracted) science?
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DimensionScore:
  """Score for a single evaluation dimension.

  Attributes:
      dimension: Name of the dimension.
      score: Score from 0.0 to 1.0.
      confidence: Confidence in the score (0.0-1.0).
      evidence: Supporting evidence for the score.
      flags: Warning flags if any.
  """

  dimension: str
  score: float = 0.0
  confidence: float = 0.0
  evidence: str = ""
  flags: list[str] = field(default_factory=list)


@dataclass
class ScholarEvalResult:
  """Complete evaluation result across all 8 dimensions.

  Attributes:
      discovery_id: Unique identifier for the discovery.
      overall_score: Weighted average across all dimensions.
      dimensions: Individual dimension scores.
      passed: Whether the discovery meets minimum quality threshold.
      recommendation: Accept/Revise/Reject recommendation.
  """

  discovery_id: str
  overall_score: float = 0.0
  dimensions: list[DimensionScore] = field(default_factory=list)
  passed: bool = False
  recommendation: str = "PENDING"


# Dimension weights (must sum to 1.0)
DIMENSION_WEIGHTS = {
  "novelty": 0.15,
  "reproducibility": 0.15,
  "statistical_rigor": 0.15,
  "citation_grounding": 0.15,
  "logical_coherence": 0.10,
  "practical_impact": 0.10,
  "ethical_compliance": 0.10,
  "temporal_validity": 0.10,
}

# Minimum threshold for acceptance
ACCEPTANCE_THRESHOLD = 0.65
REVISION_THRESHOLD = 0.45


class ScholarEvaluator:
  """Evaluates research discoveries against 8 quality dimensions.

  Usage:
      evaluator = ScholarEvaluator()
      result = evaluator.evaluate(
          discovery_id="disc-001",
          text="Our study found...",
          citations=["556 U.S. 662"],
      )
      print(f"Score: {result.overall_score:.2f} — {result.recommendation}")
  """

  def __init__(self, weights: dict[str, float] | None = None):
    self._weights = weights or DIMENSION_WEIGHTS
    assert abs(sum(self._weights.values()) - 1.0) < 0.01, "Weights must sum to 1.0"

  def evaluate(
    self,
    discovery_id: str,
    text: str,
    citations: list[str] | None = None,
    methodology: str = "",
    p_values: list[float] | None = None,
  ) -> ScholarEvalResult:
    """Run the full 8-dimension evaluation.

    Args:
        discovery_id: Unique ID for this discovery.
        text: The discovery text/abstract.
        citations: List of citation strings.
        methodology: Description of methodology used.
        p_values: Statistical p-values if available.

    Returns:
        ScholarEvalResult with scores and recommendation.
    """
    dimensions = [
      self._score_novelty(text),
      self._score_reproducibility(text, methodology),
      self._score_statistical_rigor(p_values),
      self._score_citation_grounding(text, citations or []),
      self._score_logical_coherence(text),
      self._score_practical_impact(text),
      self._score_ethical_compliance(text),
      self._score_temporal_validity(text),
    ]

    overall = sum(d.score * self._weights.get(d.dimension, 0.0) for d in dimensions)

    if overall >= ACCEPTANCE_THRESHOLD:
      recommendation = "ACCEPT"
      passed = True
    elif overall >= REVISION_THRESHOLD:
      recommendation = "REVISE"
      passed = False
    else:
      recommendation = "REJECT"
      passed = False

    result = ScholarEvalResult(
      discovery_id=discovery_id,
      overall_score=overall,
      dimensions=dimensions,
      passed=passed,
      recommendation=recommendation,
    )

    logger.info(
      "ScholarEval %s: %.2f (%s) [%d dims]",
      discovery_id,
      overall,
      recommendation,
      len(dimensions),
    )

    return result

  # -- Individual dimension scorers --

  def _score_novelty(self, text: str) -> DimensionScore:
    """Score novelty based on presence of comparative language."""
    novelty_markers = [
      "novel",
      "first",
      "new",
      "unique",
      "previously unknown",
      "for the first time",
      "our contribution",
    ]
    restating_markers = [
      "well-known",
      "established",
      "as previously shown",
      "confirms prior",
      "consistent with existing",
    ]

    novel_count = sum(1 for m in novelty_markers if m.lower() in text.lower())
    restate_count = sum(1 for m in restating_markers if m.lower() in text.lower())

    if novel_count > restate_count:
      score = min(0.9, 0.5 + novel_count * 0.1)
    elif restate_count > novel_count:
      score = max(0.2, 0.5 - restate_count * 0.1)
    else:
      score = 0.5

    return DimensionScore(
      dimension="novelty",
      score=score,
      confidence=0.6,
      evidence=f"{novel_count} novelty markers, {restate_count} restatement markers",
    )

  def _score_reproducibility(self, text: str, methodology: str) -> DimensionScore:
    """Score reproducibility based on methodology detail."""
    combined = f"{text} {methodology}".lower()
    repro_markers = [
      "replicat",
      "reproduce",
      "code available",
      "data available",
      "materials and methods",
      "experimental setup",
      "protocol",
    ]
    count = sum(1 for m in repro_markers if m in combined)
    score = min(0.95, 0.3 + count * 0.15)

    return DimensionScore(
      dimension="reproducibility",
      score=score,
      confidence=0.5,
      evidence=f"{count} reproducibility markers found",
    )

  def _score_statistical_rigor(self, p_values: list[float] | None) -> DimensionScore:
    """Score statistical rigor from p-values."""
    if not p_values:
      return DimensionScore(
        dimension="statistical_rigor",
        score=0.4,
        confidence=0.3,
        evidence="No p-values provided",
        flags=["MISSING_STATISTICS"],
      )

    significant = sum(1 for p in p_values if p < 0.05)
    bonferroni_count = sum(1 for p in p_values if p < 0.05 / len(p_values))
    score = 0.3 + (significant / len(p_values)) * 0.4

    if bonferroni_count == significant:
      score += 0.2

    flags = []
    if any(p > 0.05 for p in p_values):
      flags.append("NON_SIGNIFICANT_RESULTS")

    return DimensionScore(
      dimension="statistical_rigor",
      score=min(0.95, score),
      confidence=0.8,
      evidence=f"{significant}/{len(p_values)} significant, {bonferroni_count} survive Bonferroni",
      flags=flags,
    )

  def _score_citation_grounding(
    self, text: str, citations: list[str]
  ) -> DimensionScore:
    """Score citation grounding based on citation density."""
    word_count = len(text.split())
    citation_density = len(citations) / max(word_count / 100, 1)
    score = min(0.95, 0.2 + citation_density * 0.3)

    flags = []
    if len(citations) == 0:
      flags.append("NO_CITATIONS")
      score = 0.1

    return DimensionScore(
      dimension="citation_grounding",
      score=score,
      confidence=0.7,
      evidence=f"{len(citations)} citations in {word_count} words",
      flags=flags,
    )

  def _score_logical_coherence(self, text: str) -> DimensionScore:
    """Score logical coherence based on discourse markers."""
    coherence_markers = [
      "therefore",
      "consequently",
      "thus",
      "hence",
      "because",
      "since",
      "as a result",
      "furthermore",
      "moreover",
      "in contrast",
      "however",
    ]
    count = sum(1 for m in coherence_markers if m.lower() in text.lower())
    score = min(0.9, 0.4 + count * 0.08)

    return DimensionScore(
      dimension="logical_coherence",
      score=score,
      confidence=0.5,
      evidence=f"{count} discourse markers found",
    )

  def _score_practical_impact(self, text: str) -> DimensionScore:
    """Score practical impact based on application language."""
    impact_markers = [
      "application",
      "clinical",
      "practical",
      "industry",
      "real-world",
      "deployment",
      "implementation",
      "treatment",
    ]
    count = sum(1 for m in impact_markers if m.lower() in text.lower())
    score = min(0.9, 0.3 + count * 0.12)

    return DimensionScore(
      dimension="practical_impact",
      score=score,
      confidence=0.5,
      evidence=f"{count} impact markers found",
    )

  def _score_ethical_compliance(self, text: str) -> DimensionScore:
    """Score ethical compliance — check for red flags."""
    red_flags = [
      "fabricat",
      "falsif",
      "plagiariz",
      "without consent",
      "conflict of interest",
      "undisclosed",
      "manipulated",
    ]
    flag_count = sum(1 for f in red_flags if f.lower() in text.lower())

    if flag_count > 0:
      score = max(0.1, 0.8 - flag_count * 0.2)
      flags = ["ETHICAL_RED_FLAG"]
    else:
      score = 0.8
      flags = []

    return DimensionScore(
      dimension="ethical_compliance",
      score=score,
      confidence=0.6,
      evidence=f"{flag_count} ethical red flags",
      flags=flags,
    )

  def _score_temporal_validity(self, text: str) -> DimensionScore:
    """Score temporal validity — is this based on current science?"""
    recency_markers = ["2025", "2026", "recent", "latest", "current"]
    outdated_markers = ["retracted", "withdrawn", "superseded", "obsolete"]

    recent = sum(1 for m in recency_markers if m.lower() in text.lower())
    outdated = sum(1 for m in outdated_markers if m.lower() in text.lower())

    if outdated > 0:
      score = max(0.1, 0.5 - outdated * 0.2)
      flags = ["OUTDATED_REFERENCES"]
    elif recent > 0:
      score = min(0.9, 0.6 + recent * 0.1)
      flags = []
    else:
      score = 0.5
      flags = []

    return DimensionScore(
      dimension="temporal_validity",
      score=score,
      confidence=0.4,
      evidence=f"{recent} recency, {outdated} outdated markers",
      flags=flags,
    )
