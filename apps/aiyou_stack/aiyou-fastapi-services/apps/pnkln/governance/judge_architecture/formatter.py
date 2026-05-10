"""JudgeVerdictFormatter: ASCII Art Verdict Display
=================================================

Extracted from layers.py monolith per Rich Hickey doctrine.
"""

from .models import DecisionStatus, JudgeVerdict


class JudgeVerdictFormatter:
    """Format Judge verdicts as beautiful ASCII art for CLI display."""

    @staticmethod
    def format(verdict: JudgeVerdict) -> str:
        """Format verdict as ASCII art."""
        status_symbol = {
            DecisionStatus.APPROVED: "✅",
            DecisionStatus.DEFERRED: "⚠️",
            DecisionStatus.REJECTED: "⛔",
            DecisionStatus.PENDING: "⏳",
        }

        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            f"║ JUDGE VERDICT: {verdict.status.value:<44}║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║ Decision ID: {verdict.decision_id:<47}║",
            f"║ Status: {status_symbol[verdict.status]} {verdict.status.value:<48}║",
            f"║ Reason: {verdict.reason:<50}║",
            f"║ IQ Level: {verdict.iq_level:<48}║",
            f"║ Processing Time: {verdict.processing_time_ms:.0f}ms{' ' * (40 - len(str(int(verdict.processing_time_ms))))}║",
        ]

        if verdict.blockers:
            lines.append("╠═══════════════════════════════════════════════════════════╣")
            lines.append("║ BLOCKERS:                                                 ║")
            for blocker in verdict.blockers:
                lines.append(f"║ ├─ {blocker[:53]:<54}║")

        if verdict.warnings:
            lines.append("╠═══════════════════════════════════════════════════════════╣")
            lines.append("║ WARNINGS:                                                 ║")
            for warning in verdict.warnings:
                lines.append(f"║ ├─ {warning[:53]:<54}║")

        if verdict.next_actions:
            lines.append("╠═══════════════════════════════════════════════════════════╣")
            lines.append("║ NEXT ACTIONS:                                             ║")
            for action in verdict.next_actions[:3]:  # Show max 3
                lines.append(f"║ ├─ {action[:53]:<54}║")

        lines.append("╚═══════════════════════════════════════════════════════════╝")

        return "\n".join(lines)
