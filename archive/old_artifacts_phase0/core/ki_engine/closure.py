# Copyright 2026 ShadowTag AI. All rights reserved.
"""
Operational Closure Metrics — Items 6, 20: Luhmann entanglement measurement.

Measures how self-referential the KI store has become:
  closure_index = belief_pct × (avg_relations + avg_body_refs) / 100

Phases:
  - early: < 20 KIs
  - type-composition: < 60% beliefs
  - entanglement: ≥ 60% beliefs

Predictions at closure > 5: LLM classifiers degrade to ~55% accuracy.
At closure > 8: cross-agent transplant fails for 87%+ of beliefs.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from core.ki_engine.schema import KIMetadata


# Pattern to match KI ID references in body text
KI_REF_PATTERN = re.compile(r"\b(FACT|DECI|CONS|BELI|PREF|OPEN|PROC|ENTS|CONF)-\d{4}-\d{2}-\d{2}[A-Za-z0-9-]*")


@dataclass
class ToolPrediction:
    """Prediction about external tool reliability at current closure level."""

    tool: str
    status: str  # reliable, degraded, untested
    detail: str


@dataclass
class TrajectoryPoint:
    """Daily closure trajectory point."""

    date: str
    ki_count: int
    belief_count: int
    belief_pct: float
    avg_relations: float
    closure_index: float


@dataclass
class ClosureResult:
    """Result of operational closure analysis."""

    ki_count: int
    belief_count: int
    belief_pct: float
    avg_relations: float
    avg_body_refs: float
    closure_index: float
    entanglement_pct: float
    phase: str  # early, type-composition, entanglement
    by_type: dict[str, int]
    relation_types: dict[str, int]
    trajectory: list[TrajectoryPoint]
    predictions: list[ToolPrediction]


def _make_predictions(closure_index: float) -> list[ToolPrediction]:
    """Generate tooling predictions based on closure level."""
    predictions = [
        ToolPrediction(
            tool="Graph-structural metrics",
            status="reliable",
            detail="Degree, betweenness, connectivity — work at any closure level",
        )
    ]

    if closure_index < 3:
        predictions.append(
            ToolPrediction(
                tool="LLM classification (small models)",
                status="reliable",
                detail="Low self-referential density — classifiers unaffected",
            )
        )
    elif closure_index < 8:
        predictions.append(
            ToolPrediction(
                tool="LLM classification (small models)",
                status="degraded",
                detail=f"Closure {closure_index:.1f} — self-describing body text confounds classifiers (~55% accuracy)",
            )
        )
    else:
        predictions.append(
            ToolPrediction(
                tool="LLM classification (small models)",
                status="degraded",
                detail=f"Closure {closure_index:.1f} — high self-reference density, expect <50% accuracy",
            )
        )

    if closure_index < 2:
        predictions.append(
            ToolPrediction(
                tool="Cross-agent transplant",
                status="reliable",
                detail="Low entanglement — most KIs are portable",
            )
        )
    elif closure_index < 5:
        predictions.append(
            ToolPrediction(
                tool="Cross-agent transplant",
                status="degraded",
                detail="Growing entanglement — beliefs require context, facts still portable",
            )
        )
    else:
        predictions.append(
            ToolPrediction(
                tool="Cross-agent transplant",
                status="degraded",
                detail=f"Closure {closure_index:.1f} — 87%+ of beliefs predicted to fail direct transplant",
            )
        )

    return predictions


def compute_closure(
    kis: list[KIMetadata],
    ki_dir: Path | None = None,
) -> ClosureResult:
    """Compute operational closure metrics for the KI store.

    Args:
        kis: All KI metadata in the store.
        ki_dir: Optional path to KI directory for body-text reference counting.

    Returns:
        ClosureResult with all metrics.
    """
    ki_count = len(kis)

    if ki_count == 0:
        return ClosureResult(
            ki_count=0,
            belief_count=0,
            belief_pct=0.0,
            avg_relations=0.0,
            avg_body_refs=0.0,
            closure_index=0.0,
            entanglement_pct=0.0,
            phase="early",
            by_type={},
            relation_types={},
            trajectory=[],
            predictions=_make_predictions(0.0),
        )

    # Type distribution
    by_type: dict[str, int] = defaultdict(int)
    for ki in kis:
        by_type[ki.ki_type.value if hasattr(ki.ki_type, "value") else str(ki.ki_type)] += 1

    belief_count = by_type.get("belief", 0)
    belief_pct = (belief_count / ki_count) * 100

    # Relation counts
    total_relations = sum(len(ki.relations) for ki in kis)
    relation_types: dict[str, int] = defaultdict(int)
    for ki in kis:
        for rel in ki.relations:
            rt = rel.relation_type.value if hasattr(rel.relation_type, "value") else str(rel.relation_type)
            relation_types[rt] += 1

    avg_relations = total_relations / ki_count

    # Body-text reference counting (if ki_dir available)
    avg_body_refs = 0.0
    if ki_dir and ki_dir.exists():
        total_refs = 0
        refs_counted = 0
        for ki in kis:
            ki_path = ki_dir / ki.name / "artifacts"
            if not ki_path.exists():
                continue
            for artifact_file in ki_path.iterdir():
                if artifact_file.suffix in (".md", ".txt"):
                    try:
                        content = artifact_file.read_text(errors="replace")
                        refs = set(KI_REF_PATTERN.findall(content))
                        total_refs += len(refs)
                        refs_counted += 1
                    except OSError:
                        pass
        if refs_counted > 0:
            avg_body_refs = total_refs / refs_counted

    # Closure index
    closure_index = belief_pct * (avg_relations + avg_body_refs) / 100

    # Entanglement percentage
    max_refs = max(ki_count - 1, 1)
    entanglement_pct = (avg_body_refs / max_refs) * 100

    # Phase detection
    if ki_count < 20:
        phase = "early"
    elif belief_pct < 60:
        phase = "type-composition"
    else:
        phase = "entanglement"

    return ClosureResult(
        ki_count=ki_count,
        belief_count=belief_count,
        belief_pct=round(belief_pct, 2),
        avg_relations=round(avg_relations, 2),
        avg_body_refs=round(avg_body_refs, 2),
        closure_index=round(closure_index, 2),
        entanglement_pct=round(entanglement_pct, 2),
        phase=phase,
        by_type=dict(by_type),
        relation_types=dict(relation_types),
        trajectory=[],
        predictions=_make_predictions(closure_index),
    )
