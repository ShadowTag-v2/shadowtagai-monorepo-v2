# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Synthesis — Aggregates research findings into actionable outputs.

Takes the raw findings from the RESEARCHING phase and produces:
  - Structured summaries with confidence scores
  - Action items extracted from findings
  - Dependency graphs between discoveries
  - Consolidated recommendation set
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """A single research finding with provenance."""

    content: str
    source: str  # MCP server or tool that produced this
    confidence: float = 0.8  # 0.0–1.0
    query: str = ""
    tags: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass
class ActionItem:
    """An actionable step extracted from research findings."""

    description: str
    priority: int = 1  # 1 = highest
    dependencies: list[str] = field(default_factory=list)
    estimated_effort: str = "unknown"
    findings_refs: list[int] = field(default_factory=list)


@dataclass
class SynthesisResult:
    """Complete synthesis output from research findings."""

    summary: str
    findings: list[Finding]
    action_items: list[ActionItem]
    recommendations: list[str]
    confidence: float = 0.0  # Average confidence across findings
    total_sources: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


def _calculate_confidence(findings: list[Finding]) -> float:
    """Calculate average confidence, weighted by source diversity."""
    if not findings:
        return 0.0

    total = sum(f.confidence for f in findings)
    avg = total / len(findings)

    # Boost confidence if findings come from multiple sources.
    unique_sources = len({f.source for f in findings})
    diversity_bonus = min(0.1 * (unique_sources - 1), 0.2)

    return min(avg + diversity_bonus, 1.0)


def _extract_action_items(findings: list[Finding]) -> list[ActionItem]:
    """Extract action items from findings based on content patterns."""
    actions: list[ActionItem] = []

    for idx, finding in enumerate(findings):
        content_lower = finding.content.lower()

        # Look for imperative patterns that suggest action.
        action_indicators = [
            "should",
            "must",
            "need to",
            "recommend",
            "consider",
            "implement",
            "add",
            "create",
            "update",
            "migrate",
            "refactor",
        ]

        for indicator in action_indicators:
            if indicator in content_lower:
                # Extract the sentence containing the indicator.
                sentences = finding.content.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower() and len(sentence.strip()) > 20:
                        actions.append(
                            ActionItem(
                                description=sentence.strip(),
                                priority=1 if indicator in ("must", "need to") else 2,
                                findings_refs=[idx],
                            )
                        )
                        break  # One action per finding per indicator.
                break  # One indicator per finding.

    # Deduplicate by description prefix (first 50 chars).
    seen_prefixes: set[str] = set()
    unique_actions: list[ActionItem] = []
    for action in actions:
        prefix = action.description[:50].lower()
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            unique_actions.append(action)

    return sorted(unique_actions, key=lambda a: a.priority)


def _generate_summary(
    findings: list[Finding],
    objective: str,
) -> str:
    """Generate a structured summary from findings."""
    if not findings:
        return f"No findings for objective: {objective}"

    # Group by source.
    by_source: dict[str, list[Finding]] = {}
    for finding in findings:
        by_source.setdefault(finding.source, []).append(finding)

    parts = [f"Research summary for: {objective}\n"]
    for source, source_findings in by_source.items():
        parts.append(f"\n## Source: {source}")
        for f in source_findings[:5]:  # Cap per source.
            confidence_marker = (
                "🟢" if f.confidence >= 0.8 else "🟡" if f.confidence >= 0.5 else "🔴"
            )
            parts.append(f"  {confidence_marker} {f.content[:200]}")
            if f.references:
                parts.append(f"    refs: {', '.join(f.references[:3])}")

    return "\n".join(parts)


def _generate_recommendations(
    findings: list[Finding],
    actions: list[ActionItem],
) -> list[str]:
    """Generate high-level recommendations from findings and actions."""
    recommendations: list[str] = []

    # High-confidence findings become recommendations.
    for finding in findings:
        if finding.confidence >= 0.9:
            recommendations.append(
                f"[HIGH CONFIDENCE] {finding.content[:150]}"
            )

    # Priority-1 actions become recommendations.
    for action in actions:
        if action.priority == 1:
            recommendations.append(
                f"[ACTION REQUIRED] {action.description[:150]}"
            )

    return recommendations[:10]  # Cap at 10 recommendations.


def synthesize_findings(
    findings: list[Finding],
    objective: str = "",
    metadata: dict[str, Any] | None = None,
) -> SynthesisResult:
    """Synthesize raw research findings into a structured result.

    Args:
        findings: List of raw findings from the RESEARCHING phase.
        objective: The original research objective.
        metadata: Additional metadata to include.

    Returns:
        SynthesisResult with summary, actions, recommendations.
    """
    confidence = _calculate_confidence(findings)
    action_items = _extract_action_items(findings)
    summary = _generate_summary(findings, objective)
    recommendations = _generate_recommendations(findings, action_items)

    result = SynthesisResult(
        summary=summary,
        findings=findings,
        action_items=action_items,
        recommendations=recommendations,
        confidence=confidence,
        total_sources=len({f.source for f in findings}),
        metadata=metadata or {},
    )

    logger.info(
        "[Synthesis] %d findings → %d actions, %d recommendations (confidence=%.2f)",
        len(findings),
        len(action_items),
        len(recommendations),
        confidence,
    )

    return result
