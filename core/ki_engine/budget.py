# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""
Token Budget Recall — Item 4: Token-budget-aware KI injection.

Implements two-pass reservation system from memory-kernel:
  Pass 1: Reserve guaranteed slots for critical types (constraint, decision, conflict)
  Pass 2: Fill remaining budget with ranked KIs

Ensures agent context windows aren't overloaded with KI content.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.ki_engine.decay import RankedKI, rank_kis
from core.ki_engine.schema import KIMetadata, KIType


# Estimated tokens per KI (name + summary + context)
AVG_TOKENS_PER_KI = 80

# Type reservations: guaranteed minimum slots per type
DEFAULT_TYPE_RESERVATIONS: dict[KIType, int] = {
    KIType.CONSTRAINT: 5,  # Always include constraints
    KIType.DECISION: 5,  # Always include decisions
    KIType.CONFLICT: 3,  # Always include active conflicts
    KIType.FACT: 3,  # Include key facts
}

# Classification filter — SECRET and PERSONAL never injected into shared context
EXCLUDED_CLASSIFICATIONS = {"secret", "personal"}


@dataclass
class BudgetResult:
    """Result of token-budgeted recall."""

    selected: list[RankedKI]
    reserved: list[RankedKI]  # KIs selected via type reservation
    ranked: list[RankedKI]  # KIs selected via general ranking
    total_tokens: int
    budget: int
    overflow_count: int  # KIs that didn't fit


def estimate_tokens(ki: KIMetadata) -> int:
    """Estimate token count for a KI's context representation."""
    chars = len(ki.name) + len(ki.summary)
    for tag in ki.tags:
        chars += len(tag) + 2
    # Rough: 1 token ≈ 4 chars
    return max(20, chars // 4)


def token_budget_recall(
    kis: list[KIMetadata],
    max_tokens: int = 8000,
    keyword_boosts: dict[str, float] | None = None,
    type_reservations: dict[KIType, int] | None = None,
    exclude_expired: bool = True,
    exclude_archived: bool = True,
) -> BudgetResult:
    """Select KIs within a token budget using two-pass reservation.

    Pass 1 (reservation): Guarantee minimum slots for critical types.
    Pass 2 (fill): Rank remaining KIs and fill until budget is exhausted.

    Args:
        kis: All available KIs.
        max_tokens: Maximum context token budget.
        keyword_boosts: Optional keyword match boosts by KI name.
        type_reservations: Override default type reservations.
        exclude_expired: Skip expired KIs.
        exclude_archived: Skip archived KIs.

    Returns:
        BudgetResult with selected KIs within budget.
    """
    reservations = type_reservations or DEFAULT_TYPE_RESERVATIONS

    # Pre-filter
    candidates = []
    for ki in kis:
        # Skip non-active
        if exclude_archived and ki.status.value in ("archived", "superseded"):
            continue
        if exclude_expired and ki.is_expired:
            continue
        # Skip private classifications
        if ki.classification.value in EXCLUDED_CLASSIFICATIONS:
            continue
        candidates.append(ki)

    # Rank all candidates
    all_ranked = rank_kis(candidates, keyword_boosts)

    # Pass 1: Type reservations
    reserved: list[RankedKI] = []
    reserved_names: set[str] = set()
    tokens_used = 0

    for ki_type, min_count in reservations.items():
        type_ranked = [r for r in all_ranked if r.ki.ki_type == ki_type and r.ki.name not in reserved_names]
        for rki in type_ranked[:min_count]:
            est = estimate_tokens(rki.ki)
            if tokens_used + est <= max_tokens:
                reserved.append(rki)
                reserved_names.add(rki.ki.name)
                tokens_used += est

    # Pass 2: Fill remaining budget with top-ranked non-reserved
    general: list[RankedKI] = []
    for rki in all_ranked:
        if rki.ki.name in reserved_names:
            continue
        est = estimate_tokens(rki.ki)
        if tokens_used + est <= max_tokens:
            general.append(rki)
            tokens_used += est
        else:
            break  # Budget exhausted

    selected = reserved + general
    # Re-sort by score
    selected.sort(key=lambda r: r.score, reverse=True)

    overflow = len(all_ranked) - len(reserved) - len(general)

    return BudgetResult(
        selected=selected,
        reserved=reserved,
        ranked=general,
        total_tokens=tokens_used,
        budget=max_tokens,
        overflow_count=max(0, overflow),
    )
