# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Judge Architecture verdict formatter.

Produces human-readable summaries and Obsidian-compatible reports.
"""

from __future__ import annotations


from pnkln.governance.judge_architecture.models import DecisionStatus, JudgeVerdict


class VerdictFormatter:
    """Format JudgeVerdict instances into human-readable reports."""

    @staticmethod
    def to_summary(verdict: JudgeVerdict) -> str:
        """One-line summary of verdict."""
        icon = "✅" if verdict.status == DecisionStatus.APPROVED else "❌"
        return f"{icon} [{verdict.decision_id}] {verdict.status.value}: {verdict.reason}"

    @staticmethod
    def to_markdown(verdict: JudgeVerdict) -> str:
        """Full Obsidian-compatible markdown report."""
        lines = [
            f"# Judge Verdict: {verdict.decision_id}",
            "",
            f"**Status**: {verdict.status.value}",
            f"**IQ Level**: {verdict.iq_level}",
            f"**Processing Time**: {verdict.processing_time_ms:.1f}ms",
            "",
            "## Reason",
            verdict.reason,
        ]

        if verdict.blockers:
            lines.extend(["", "## Blockers"])
            for b in verdict.blockers:
                lines.append(f"- ❌ {b}")

        if verdict.warnings:
            lines.extend(["", "## Warnings"])
            for w in verdict.warnings:
                lines.append(f"- ⚠️ {w}")

        if verdict.next_actions:
            lines.extend(["", "## Next Actions"])
            for a in verdict.next_actions:
                lines.append(f"- [ ] {a}")

        return "\n".join(lines)


__all__ = ["VerdictFormatter"]
