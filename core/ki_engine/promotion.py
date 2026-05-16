# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
"""
Promotion & Conflict Detection — Items 15, 18: Automated lifecycle transitions.

Belief Promotion Pipeline:
  - Beliefs with confidence ≥ 0.9 → promote to fact
  - Emits PROMOTE event

Conflict Detection:
  - Finds KIs with contradicting relations
  - Finds KIs with overlapping content but divergent claims
  - Creates conflict atoms when detected
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.ki_engine.events import EventAction, append_event
from core.ki_engine.schema import (
  PROMOTION_THRESHOLD,
  KIMetadata,
  KIStatus,
  KIType,
  RelationType,
)


@dataclass
class PromotionResult:
  """Result of running the promotion pipeline."""

  promoted: list[str]  # KI names promoted to fact
  skipped: list[str]  # KI names below threshold
  already_facts: list[str]  # KIs already facts


@dataclass
class ConflictCandidate:
  """A potential conflict between two KIs."""

  ki_a: str
  ki_b: str
  reason: str
  overlap_tokens: set[str] = field(default_factory=set)


@dataclass
class ConflictResult:
  """Result of conflict detection."""

  detected: list[ConflictCandidate]
  created_conflicts: list[str]  # Names of newly created conflict KIs


def promote_beliefs(
  kis: list[KIMetadata],
  ki_dir: Path | None = None,
  threshold: float = PROMOTION_THRESHOLD,
  dry_run: bool = False,
) -> PromotionResult:
  """Promote beliefs with confidence ≥ threshold to facts.

  Args:
      kis: All KI metadata.
      ki_dir: Path to KI directory for event logging.
      threshold: Confidence threshold for promotion. Default: 0.9.
      dry_run: If True, don't actually modify KIs.

  Returns:
      PromotionResult with lists of promoted, skipped, and already-fact KIs.
  """
  result = PromotionResult(promoted=[], skipped=[], already_facts=[])

  for ki in kis:
    if ki.ki_type != KIType.BELIEF:
      if ki.ki_type == KIType.FACT:
        result.already_facts.append(ki.name)
      continue

    if ki.status != KIStatus.ACTIVE:
      continue

    if ki.confidence >= threshold:
      if not dry_run:
        ki.ki_type = KIType.FACT
        ki.ttl_days = None  # Facts are permanent
        ki.status = KIStatus.ACTIVE

        if ki_dir:
          append_event(
            ki_dir,
            EventAction.PROMOTE,
            ki.name,
            details={
              "from_type": "belief",
              "to_type": "fact",
              "confidence": ki.confidence,
            },
          )

      result.promoted.append(ki.name)
    else:
      result.skipped.append(ki.name)

  return result


def detect_conflicts(
  kis: list[KIMetadata],
  overlap_threshold: int = 3,
) -> ConflictResult:
  """Detect potential conflicts between KIs.

  Checks:
  1. Explicit contradicts relations
  2. High token overlap between different KIs (potential contradiction)
  3. Superseded KIs still marked active

  Args:
      kis: All KI metadata.
      overlap_threshold: Minimum shared name tokens to flag overlap.

  Returns:
      ConflictResult with detected conflicts.
  """
  candidates: list[ConflictCandidate] = []
  active = [ki for ki in kis if ki.status == KIStatus.ACTIVE]

  # Check 1: Explicit contradicts relations
  for ki in active:
    for rel in ki.relations:
      if rel.relation_type == RelationType.CONTRADICTS:
        candidates.append(
          ConflictCandidate(
            ki_a=ki.name,
            ki_b=rel.target_ki,
            reason="Explicit contradicts relation",
          )
        )

  # Check 2: High token overlap (adapted from existing dream_consolidation.py)
  names_seen: dict[str, set[str]] = {}
  for ki in active:
    tokens = set(ki.name.lower().split())
    for prev_name, prev_tokens in names_seen.items():
      overlap = tokens & prev_tokens
      if len(overlap) >= overlap_threshold:
        candidates.append(
          ConflictCandidate(
            ki_a=ki.name,
            ki_b=prev_name,
            reason=f"High name token overlap ({len(overlap)} shared tokens)",
            overlap_tokens=overlap,
          )
        )
    names_seen[ki.name] = tokens

  # Check 3: Superseded KIs still active
  superseded_targets: set[str] = set()
  for ki in active:
    for rel in ki.relations:
      if rel.relation_type == RelationType.SUPERSEDES:
        superseded_targets.add(rel.target_ki)

  for ki in active:
    if ki.name in superseded_targets:
      candidates.append(
        ConflictCandidate(
          ki_a=ki.name,
          ki_b="(superseded but active)",
          reason="KI is superseded but still marked active",
        )
      )

  # Deduplicate bidirectional conflicts
  seen_pairs: set[tuple[str, str]] = set()
  deduped: list[ConflictCandidate] = []
  for c in candidates:
    pair = tuple(sorted([c.ki_a, c.ki_b]))
    if pair not in seen_pairs:
      seen_pairs.add(pair)
      deduped.append(c)

  return ConflictResult(detected=deduped, created_conflicts=[])
