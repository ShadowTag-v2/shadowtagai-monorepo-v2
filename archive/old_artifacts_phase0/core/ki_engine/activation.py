# Copyright 2026 ShadowTagAI. All rights reserved.
"""
Spreading Activation — Items 3, 16, 19: ACT-R spreading activation for KI graphs.

Implements the memory-kernel 'wander' algorithm:
  - Base-level activation: B_i = ln(n) - 0.5·ln(t)
  - Tag-based spreading through shared tags and explicit relations
  - Collision detection: high Jaccard dissimilarity pairs that both lit up
  - sqrt-sigmoid modulation for hub preservation

Used by Dream Consolidation for:
  - Pre-consolidation collision detection (Item 16)
  - Tier 1 gate before expensive drift sessions (Item 19)
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

from core.ki_engine.schema import KIMetadata, RelationType


@dataclass
class ActivatedKI:
    """A KI with its activation level after spreading."""

    ki: KIMetadata
    activation: float
    base_level: float
    spread_component: float
    source_tags: set[str] = field(default_factory=set)
    activated_by: list[str] = field(default_factory=list)

    def __lt__(self, other: ActivatedKI) -> bool:
        return self.activation < other.activation


@dataclass
class Collision:
    """A pair of KIs from different domains that both activated.

    High Jaccard dissimilarity + both lit up = unexpected connection.
    """

    ki_a: str
    ki_b: str
    dissimilarity: float  # 1 - jaccard(tags_a, tags_b)
    activation_a: float
    activation_b: float
    shared_tags: set[str] = field(default_factory=set)
    description: str = ""


@dataclass
class ActivationResult:
    """Result of a spreading activation pass."""

    activated: list[ActivatedKI]
    collisions: list[Collision]
    steps: int
    total_energy: float


# Relation-type weights for spreading
RELATION_WEIGHTS: dict[RelationType, float] = {
    RelationType.EXTENDS: 0.9,
    RelationType.SUPPORTS: 0.7,
    RelationType.CONTRADICTS: 0.5,  # Lower — opposing, but still interesting
    RelationType.CAUSED_BY: 0.8,
    RelationType.SUPERSEDES: 0.6,
    RelationType.APPLIED_TO: 0.5,
    RelationType.RELATED: 0.4,
}


def _base_level_activation(
    citation_count: int,
    age_days: float,
    min_age: float = 0.5,
) -> float:
    """ACT-R base-level activation: B_i = ln(n) - 0.5·ln(t).

    Args:
        citation_count: Number of times this KI has been referenced.
        age_days: Age of the KI in days.
        min_age: Minimum age to avoid log(0).

    Returns:
        Base-level activation value.
    """
    n = max(1, citation_count)
    t = max(min_age, age_days)
    return math.log(n) - 0.5 * math.log(t)


def _sqrt_sigmoid(x: float) -> float:
    """sqrt-sigmoid modulation: 1/√(1 + e^(-x)).

    Compresses activation to [0.707, 1.0], preserving hub atoms.
    """
    return 1.0 / math.sqrt(1.0 + math.exp(-x))


def _jaccard_dissimilarity(set_a: set, set_b: set) -> float:
    """1 - Jaccard similarity. Returns 1.0 if no overlap, 0.0 if identical."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    intersection = set_a & set_b
    return 1.0 - len(intersection) / len(union)


def spread_activation(
    kis: list[KIMetadata],
    seed_tags: set[str] | None = None,
    seed_kis: list[str] | None = None,
    steps: int = 3,
    decay_per_step: float = 0.7,
    top_k_per_step: int = 10,
    activation_threshold: float = 0.1,
) -> ActivationResult:
    """Run spreading activation through the KI graph.

    Args:
        kis: All KIs in the store.
        seed_tags: Initial tags to seed activation from.
        seed_kis: Initial KI names to seed activation from.
        steps: Number of spreading steps.
        decay_per_step: Energy decay factor per step.
        top_k_per_step: Lateral inhibition — only top K survive each step.
        activation_threshold: Minimum activation to consider.

    Returns:
        ActivationResult with activated KIs, collisions, and diagnostics.
    """
    seed_tags = seed_tags or set()
    seed_kis = seed_kis or []

    # Build lookup structures
    ki_by_name: dict[str, KIMetadata] = {ki.name: ki for ki in kis}
    ki_by_tag: dict[str, list[str]] = defaultdict(list)
    for ki in kis:
        for tag in ki.tags:
            ki_by_tag[tag].append(ki.name)

    # Build relation graph
    relation_graph: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for ki in kis:
        for rel in ki.relations:
            weight = RELATION_WEIGHTS.get(rel.relation_type, 0.4)
            relation_graph[ki.name].append((rel.target_ki, weight))
            # Bidirectional
            relation_graph[rel.target_ki].append((ki.name, weight * 0.5))

    # Count citations (how many KIs reference each KI)
    citation_counts: dict[str, int] = defaultdict(int)
    for ki in kis:
        for rel in ki.relations:
            citation_counts[rel.target_ki] += 1

    # Phase 1: Seed activation
    activations: dict[str, float] = {}
    activated_by: dict[str, list[str]] = defaultdict(list)
    source_tags: dict[str, set[str]] = defaultdict(set)

    # Seed from tags
    for tag in seed_tags:
        for ki_name in ki_by_tag.get(tag, []):
            activations[ki_name] = activations.get(ki_name, 0) + 1.0
            source_tags[ki_name].add(tag)
            activated_by[ki_name].append(f"tag:{tag}")

    # Seed from explicit KIs
    for ki_name in seed_kis:
        if ki_name in ki_by_name:
            activations[ki_name] = activations.get(ki_name, 0) + 2.0
            activated_by[ki_name].append("seed")

    # Phase 2: Spreading steps
    for step in range(steps):
        new_activations: dict[str, float] = {}
        current_energy = decay_per_step**step

        # Sort by activation, take top K (lateral inhibition)
        sorted_active = sorted(activations.items(), key=lambda x: x[1], reverse=True)[:top_k_per_step]

        for ki_name, activation in sorted_active:
            ki = ki_by_name.get(ki_name)
            if not ki:
                continue

            # Spread through tags
            for tag in ki.tags:
                for neighbor_name in ki_by_tag.get(tag, []):
                    if neighbor_name != ki_name:
                        spread = activation * current_energy * 0.3
                        new_activations[neighbor_name] = new_activations.get(neighbor_name, 0) + spread
                        source_tags[neighbor_name].update(source_tags.get(ki_name, set()))
                        activated_by[neighbor_name].append(f"spread:{ki_name}")

            # Spread through explicit relations
            for neighbor_name, rel_weight in relation_graph.get(ki_name, []):
                spread = activation * current_energy * rel_weight
                new_activations[neighbor_name] = new_activations.get(neighbor_name, 0) + spread
                activated_by[neighbor_name].append(f"rel:{ki_name}")

        # Merge new activations
        for name, new_act in new_activations.items():
            activations[name] = activations.get(name, 0) + new_act

    # Phase 3: Apply base-level activation and modulation
    result_kis: list[ActivatedKI] = []

    for ki_name, raw_activation in activations.items():
        if raw_activation < activation_threshold:
            continue

        ki = ki_by_name.get(ki_name)
        if not ki:
            continue

        base = _base_level_activation(
            citation_count=citation_counts.get(ki_name, 0),
            age_days=ki.age_days,
        )
        modulated = _sqrt_sigmoid(base)
        final_activation = raw_activation * modulated

        result_kis.append(
            ActivatedKI(
                ki=ki,
                activation=final_activation,
                base_level=base,
                spread_component=raw_activation,
                source_tags=source_tags.get(ki_name, set()),
                activated_by=activated_by.get(ki_name, []),
            )
        )

    result_kis.sort(key=lambda a: a.activation, reverse=True)
    total_energy = sum(a.activation for a in result_kis)

    # Phase 4: Detect collisions
    collisions = detect_collisions(result_kis, dissimilarity_threshold=0.7)

    return ActivationResult(
        activated=result_kis,
        collisions=collisions,
        steps=steps,
        total_energy=total_energy,
    )


def detect_collisions(
    activated: list[ActivatedKI],
    dissimilarity_threshold: float = 0.7,
    max_pairs: int = 20,
) -> list[Collision]:
    """Find collision pairs — KIs from different domains that both activated.

    A collision is a pair where:
      - Both have activation > threshold
      - Jaccard dissimilarity of their tags > dissimilarity_threshold
      - They don't already have an explicit relation

    Args:
        activated: List of activated KIs.
        dissimilarity_threshold: Minimum Jaccard dissimilarity for a collision.
        max_pairs: Maximum number of collision pairs to return.

    Returns:
        List of Collision objects, sorted by combined activation.
    """
    collisions: list[Collision] = []

    # Only consider top-activated KIs to keep O(n²) manageable
    top = activated[:30]

    # Build set of known relations for dedup
    known_pairs: set[tuple[str, str]] = set()
    for aki in top:
        for rel in aki.ki.relations:
            pair = tuple(sorted([aki.ki.name, rel.target_ki]))
            known_pairs.add(pair)

    for i, a in enumerate(top):
        for b in top[i + 1 :]:
            pair_key = tuple(sorted([a.ki.name, b.ki.name]))
            if pair_key in known_pairs:
                continue

            tags_a = set(a.ki.tags)
            tags_b = set(b.ki.tags)
            dissim = _jaccard_dissimilarity(tags_a, tags_b)

            if dissim >= dissimilarity_threshold:
                shared = tags_a & tags_b
                collisions.append(
                    Collision(
                        ki_a=a.ki.name,
                        ki_b=b.ki.name,
                        dissimilarity=dissim,
                        activation_a=a.activation,
                        activation_b=b.activation,
                        shared_tags=shared,
                        description=(
                            f"Unexpected connection: '{a.ki.name}' and '{b.ki.name}' (dissimilarity={dissim:.2f}, shared={shared or 'none'})"
                        ),
                    )
                )

    # Sort by combined activation (most interesting first)
    collisions.sort(key=lambda c: c.activation_a + c.activation_b, reverse=True)
    return collisions[:max_pairs]
