# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""
Views — Item 5: Auto-generated summary views from KI store.

Generates:
  - INDEX.md — Full KI inventory with types, scores, status
  - DECISIONS.md — All active decision KIs
  - CONSTRAINTS.md — All active constraint KIs
  - HANDOFF.md — Session handoff context with top-ranked KIs
  - CONFLICTS.md — Active conflict KIs (urgent)
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from core.ki_engine.decay import rank_kis
from core.ki_engine.schema import KIMetadata, KIStatus, KIType


def render_index(kis: list[KIMetadata]) -> str:
    """Render INDEX.md — full KI inventory."""
    lines = [
        "# KI Index",
        "",
        f"> Auto-generated. {len(kis)} KIs. Last rendered: {datetime.now(UTC).isoformat()}",
        "",
        "| Name | Type | Status | Confidence | Age (d) | Tags |",
        "|------|------|--------|------------|---------|------|",
    ]

    for ki in sorted(kis, key=lambda k: k.name):
        ki_type = ki.ki_type.value if hasattr(ki.ki_type, "value") else str(ki.ki_type)
        status = ki.status.value if hasattr(ki.status, "value") else str(ki.status)
        tags = ", ".join(ki.tags[:5])
        lines.append(f"| {ki.name} | {ki_type} | {status} | {ki.confidence:.1f} | {ki.age_days:.0f} | {tags} |")

    lines.append("")
    return "\n".join(lines) + "\n"


def render_decisions(kis: list[KIMetadata]) -> str:
    """Render DECISIONS.md — active decisions only."""
    decisions = [ki for ki in kis if ki.ki_type == KIType.DECISION and ki.status == KIStatus.ACTIVE]
    ranked = rank_kis(decisions)

    lines = [
        "# Decisions",
        "",
        f"> {len(decisions)} active decisions.",
        "",
    ]

    for rki in ranked:
        ki = rki.ki
        lines.append(f"### {ki.name}")
        if ki.confidence < 1.0:
            lines.append(f"*Confidence: {ki.confidence:.1f}*")
        lines.append(f"{ki.summary}")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_constraints(kis: list[KIMetadata]) -> str:
    """Render CONSTRAINTS.md — active constraints only."""
    constraints = [ki for ki in kis if ki.ki_type == KIType.CONSTRAINT and ki.status == KIStatus.ACTIVE]
    ranked = rank_kis(constraints)

    lines = [
        "# Constraints",
        "",
        f"> {len(constraints)} active constraints.",
        "",
    ]

    for rki in ranked:
        ki = rki.ki
        lines.append(f"### {ki.name}")
        lines.append(f"{ki.summary}")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_conflicts(kis: list[KIMetadata]) -> str:
    """Render CONFLICTS.md — active conflicts (urgent)."""
    conflicts = [ki for ki in kis if ki.ki_type == KIType.CONFLICT and ki.status == KIStatus.ACTIVE]

    lines = [
        "# ⚠ Active Conflicts",
        "",
        f"> {len(conflicts)} active conflicts requiring resolution.",
        "",
    ]

    for ki in conflicts:
        lines.append(f"### {ki.name}")
        lines.append(f"{ki.summary}")
        if ki.relations:
            lines.append("**Related KIs:**")
            for rel in ki.relations:
                rt = rel.relation_type.value if hasattr(rel.relation_type, "value") else str(rel.relation_type)
                lines.append(f"  - {rel.target_ki} ({rt})")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_handoff(
    kis: list[KIMetadata],
    max_kis: int = 20,
) -> str:
    """Render HANDOFF.md — top-ranked KIs for session handoff."""
    active = [ki for ki in kis if ki.status == KIStatus.ACTIVE]
    ranked = rank_kis(active)[:max_kis]

    lines = [
        "# Session Handoff",
        "",
        f"> Top {len(ranked)} KIs for context injection. Generated: {datetime.now(UTC).isoformat()}",
        "",
    ]

    # Conflicts first (urgent)
    conflicts = [r for r in ranked if r.ki.ki_type == KIType.CONFLICT]
    if conflicts:
        lines.append("## ⚠ Active Conflicts")
        lines.append("")
        for rki in conflicts:
            lines.append(f"- **{rki.ki.name}** — {rki.ki.summary}")
        lines.append("")

    # Decisions + Constraints
    critical = [r for r in ranked if r.ki.ki_type in (KIType.DECISION, KIType.CONSTRAINT)]
    if critical:
        lines.append("## Critical Context")
        lines.append("")
        for rki in critical:
            ki_type = rki.ki.ki_type.value if hasattr(rki.ki.ki_type, "value") else str(rki.ki.ki_type)
            lines.append(f"- [{ki_type}] **{rki.ki.name}** — {rki.ki.summary}")
        lines.append("")

    # Everything else
    other = [r for r in ranked if r.ki.ki_type not in (KIType.CONFLICT, KIType.DECISION, KIType.CONSTRAINT)]
    if other:
        lines.append("## Additional Context")
        lines.append("")
        for rki in other:
            ki_type = rki.ki.ki_type.value if hasattr(rki.ki.ki_type, "value") else str(rki.ki.ki_type)
            lines.append(f"- [{ki_type}] **{rki.ki.name}** (score: {rki.score:.2f}) — {rki.ki.summary}")
        lines.append("")

    return "\n".join(lines) + "\n"


def generate_all_views(
    kis: list[KIMetadata],
    output_dir: Path,
) -> dict[str, Path]:
    """Generate all view files.

    Args:
        kis: All KIs in the store.
        output_dir: Directory to write view files to.

    Returns:
        Map of view name → file path.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    views = {
        "INDEX.md": render_index(kis),
        "DECISIONS.md": render_decisions(kis),
        "CONSTRAINTS.md": render_constraints(kis),
        "CONFLICTS.md": render_conflicts(kis),
        "HANDOFF.md": render_handoff(kis),
    }

    paths = {}
    for name, content in views.items():
        path = output_dir / name
        path.write_text(content)
        paths[name] = path

    return paths
