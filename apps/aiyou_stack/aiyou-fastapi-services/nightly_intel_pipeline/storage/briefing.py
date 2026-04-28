# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Briefing Generator
Creates executive briefings from intelligence data

Enhanced with Gemini IntelEvent integration for:
- Structured event summaries
- Upcoming regulatory deadlines
- Jurisdiction breakdown
- High urgency alerts
"""

import json
from datetime import datetime
from pathlib import Path

import structlog

from ..config import STORAGE_CONFIG
from .database import IntelDatabase

logger = structlog.get_logger(__name__)


class BriefingGenerator:
    """Generates intelligence briefings from scored content

    Output format: Markdown with tiered recommendations
    """

    def __init__(self, db: IntelDatabase | None = None):
        self.db = db or IntelDatabase()
        self.output_path = Path(STORAGE_CONFIG["briefing_output"]["path"])
        self.output_path.mkdir(parents=True, exist_ok=True)

        logger.info("briefing_generator_initialized", output_path=str(self.output_path))

    def generate_briefing(
        self,
        date_range_start: str | None = None,
        date_range_end: str | None = None,
        include_intel_events: bool = True,
    ) -> str:
        """Generate executive briefing with IntelEvent integration

        Args:
            date_range_start: Start of date range
            date_range_end: End of date range
            include_intel_events: Include Gemini-normalized IntelEvents

        Returns:
            Path to briefing file

        """
        now = datetime.now()
        date_range_end = date_range_end or now.isoformat()
        date_range_start = date_range_start or now.replace(hour=0, minute=0, second=0).isoformat()

        # Get all scored content
        repos, papers = self.db.get_all_scores()

        # Get tier summary
        tier_summary = self.db.get_tier_summary()

        # Get IntelEvent data if enabled
        intel_events_data = None
        if include_intel_events:
            intel_events_data = self._get_intel_events_data()

        # Generate briefing content
        briefing_content = self._build_briefing(
            repos=repos,
            papers=papers,
            tier_summary=tier_summary,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            intel_events_data=intel_events_data,
        )

        # Save briefing
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        briefing_file = self.output_path / f"briefing_{timestamp}.md"
        briefing_file.write_text(briefing_content, encoding="utf-8")

        # Store briefing metadata in database
        summary = self._generate_summary(tier_summary, intel_events_data)
        self.db.store_briefing(
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            briefing_file_path=str(briefing_file),
            summary=summary,
            tier_counts=tier_summary,
        )

        logger.info(
            "briefing_generated",
            file=str(briefing_file),
            total_items=len(repos) + len(papers),
            intel_events=intel_events_data["total_events"] if intel_events_data else 0,
        )

        return str(briefing_file)

    def _get_intel_events_data(self) -> dict:
        """Gather all IntelEvent data for briefing"""
        return {
            "summary": self.db.get_intel_event_summary(),
            "total_events": self.db.get_intel_event_summary().get("total_events", 0),
            "high_urgency": self.db.get_high_urgency_events(min_urgency=0.7),
            "upcoming_deadlines": self.db.get_upcoming_effective_dates(days_ahead=90),
            "tier_1_events": self.db.get_intel_events_by_tier(1),
            "tier_2_events": self.db.get_intel_events_by_tier(2),
            "regulations": self.db.get_intel_events_by_source_type("regulation"),
        }

    def _build_briefing(
        self,
        repos: list[dict],
        papers: list[dict],
        tier_summary: dict,
        date_range_start: str,
        date_range_end: str,
        intel_events_data: dict | None = None,
    ) -> str:
        """Build briefing markdown content with IntelEvent integration"""
        parts = []

        # Header
        parts.append("# Nightly Intelligence Briefing")
        parts.append("")
        parts.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        parts.append(f"**Period:** {date_range_start} to {date_range_end}")
        parts.append("")

        # Executive Summary
        parts.append("## Executive Summary")
        parts.append("")
        total_items = sum([tier_summary.get(t, {}).get("total", 0) for t in [1, 2, 3, 4]])
        parts.append(f"**Total Intelligence Items:** {total_items}")
        parts.append(f"- GitHub Repositories: {len(repos)}")
        parts.append(f"- arXiv Papers: {len(papers)}")

        # Add IntelEvent summary if available
        if intel_events_data and intel_events_data.get("total_events", 0) > 0:
            parts.append(f"- Gemini-Normalized Events: {intel_events_data['total_events']}")
            summary = intel_events_data.get("summary", {})
            if summary.get("by_source_type"):
                source_breakdown = ", ".join(
                    [f"{k}: {v}" for k, v in summary["by_source_type"].items()],
                )
                parts.append(f"  - By source: {source_breakdown}")
        parts.append("")

        parts.append("### Tier Breakdown")
        parts.append("")
        for tier in [1, 2, 3, 4]:
            tier_data = tier_summary.get(tier, {"repositories": 0, "papers": 0, "total": 0})
            tier_names = {
                1: "Executive Review Required",
                2: "Auto-Action Approved",
                3: "Archive for Later",
                4: "Low Priority",
            }
            parts.append(f"**Tier {tier} ({tier_names[tier]}):** {tier_data['total']} items")
            parts.append(f"  - Repositories: {tier_data['repositories']}")
            parts.append(f"  - Papers: {tier_data['papers']}")
            parts.append("")

        # High Urgency Alerts (from IntelEvents)
        if intel_events_data and intel_events_data.get("high_urgency"):
            parts.append("---")
            parts.append("")
            parts.append("## HIGH URGENCY ALERTS")
            parts.append("")
            parts.append("Events requiring immediate attention (urgency score ≥ 0.7):")
            parts.append("")
            for event in intel_events_data["high_urgency"][:5]:
                parts.extend(self._format_intel_event_entry(event, urgent=True))

        # Upcoming Regulatory Deadlines
        if intel_events_data and intel_events_data.get("upcoming_deadlines"):
            parts.append("---")
            parts.append("")
            parts.append("## Upcoming Regulatory Deadlines (90 days)")
            parts.append("")
            for event in intel_events_data["upcoming_deadlines"][:10]:
                parts.append(
                    f"- **{event.get('effective_date', 'TBD')}**: {event.get('title', 'Untitled')}",
                )
                parts.append(
                    f"  - Jurisdiction: {event.get('jurisdiction', 'Unknown')} | Type: {event.get('source_type', 'Unknown')}",
                )
                if event.get("summary"):
                    parts.append(f"  - {event['summary'][:150]}...")
                parts.append("")

        # Tier 1: Executive Review Required
        parts.append("---")
        parts.append("")
        parts.append("## Tier 1: Executive Review Required")
        parts.append("")
        parts.append(
            "High-value items requiring leadership attention and strategic decision-making.",
        )
        parts.append("")

        tier1_repos = [r for r in repos if r["tier"] == 1]
        tier1_papers = [p for p in papers if p["tier"] == 1]

        if tier1_repos:
            parts.append("### GitHub Repositories")
            parts.append("")
            for repo in tier1_repos:
                parts.extend(self._format_repo_entry(repo))

        if tier1_papers:
            parts.append("### arXiv Papers")
            parts.append("")
            for paper in tier1_papers:
                parts.extend(self._format_paper_entry(paper))

        if not tier1_repos and not tier1_papers:
            parts.append("*No Tier 1 items this period.*")
            parts.append("")

        # Tier 2: Auto-Action Approved
        parts.append("---")
        parts.append("")
        parts.append("## Tier 2: Auto-Action Approved")
        parts.append("")
        parts.append("Recommended for immediate adoption or implementation.")
        parts.append("")

        tier2_repos = [r for r in repos if r["tier"] == 2]
        tier2_papers = [p for p in papers if p["tier"] == 2]

        if tier2_repos:
            parts.append("### GitHub Repositories")
            parts.append("")
            for repo in tier2_repos[:10]:  # Top 10
                parts.extend(self._format_repo_entry(repo, compact=True))
            if len(tier2_repos) > 10:
                parts.append(f"*... and {len(tier2_repos) - 10} more repositories*")
                parts.append("")

        if tier2_papers:
            parts.append("### arXiv Papers")
            parts.append("")
            for paper in tier2_papers[:10]:  # Top 10
                parts.extend(self._format_paper_entry(paper, compact=True))
            if len(tier2_papers) > 10:
                parts.append(f"*... and {len(tier2_papers) - 10} more papers*")
                parts.append("")

        # Tier 3: Archive
        parts.append("---")
        parts.append("")
        parts.append("## Tier 3: Archive for Later")
        parts.append("")
        tier3_count = tier_summary.get(3, {}).get("total", 0)
        parts.append(f"**Total Tier 3 items:** {tier3_count}")
        parts.append("*Items of moderate interest, catalogued for future reference.*")
        parts.append("")

        # Tier 4: Low Priority
        parts.append("---")
        parts.append("")
        parts.append("## Tier 4: Low Priority")
        parts.append("")
        tier4_count = tier_summary.get(4, {}).get("total", 0)
        parts.append(f"**Total Tier 4 items:** {tier4_count}")
        parts.append("*Low-priority items, minimal relevance to current objectives.*")
        parts.append("")

        # Footer
        parts.append("---")
        parts.append("")
        parts.append("## Methodology")
        parts.append("")
        parts.append("This briefing was generated by the Nightly Intel Pipeline using:")
        parts.append("- **Ethical Web Scraping:** ATP 5-19 RA-1 compliant with robots.txt respect")
        parts.append("- **JR Engine Scoring:** Purpose → Reasons → Brakes framework")
        parts.append("- **Multi-Source Intelligence:** GitHub repositories, arXiv papers")
        parts.append(
            "- **Tier Classification:** Executive (Tier 1), Auto-Action (Tier 2), Archive (Tier 3), Low (Tier 4)",
        )
        parts.append("")

        return "\n".join(parts)

    def _format_repo_entry(self, repo: dict, compact: bool = False) -> list[str]:
        """Format a repository entry for the briefing"""
        parts = []

        parts.append(f"#### {repo['repo_name']}")
        if repo.get("url"):
            parts.append(f"**URL:** {repo['url']}")
        parts.append(
            f"**Score:** {repo['total_score']:.1f} | **ATP Risk:** {repo['atp_risk_level']} | **Stars:** {repo.get('stars', 'N/A')}",
        )

        if repo.get("description"):
            parts.append(f"**Description:** {repo['description']}")

        if not compact:
            parts.append("")
            parts.append("**Evaluation:**")
            parts.append(
                f"- Purpose Alignment ({repo['purpose_alignment']:.0f}): {repo['purpose_reasoning']}",
            )
            parts.append(
                f"- Technical Merit ({repo['technical_merit']:.0f}): {repo['technical_reasoning']}",
            )
            parts.append(
                f"- Adoption Potential ({repo['adoption_potential']:.0f}): {repo['adoption_reasoning']}",
            )
            parts.append(
                f"- Risk Assessment ({repo['risk_assessment']:.0f}): {repo['risk_reasoning']}",
            )

            if repo.get("brakes"):
                import json

                brakes = json.loads(repo["brakes"])
                if brakes:
                    parts.append("")
                    parts.append("**Concerns (Brakes):**")
                    for brake in brakes:
                        parts.append(f"- {brake}")

        parts.append("")
        return parts

    def _format_paper_entry(self, paper: dict, compact: bool = False) -> list[str]:
        """Format a paper entry for the briefing"""
        parts = []

        parts.append(f"#### {paper['title']}")
        parts.append(
            f"**arXiv:** {paper['arxiv_id']} | **Score:** {paper['total_score']:.1f} | **ATP Risk:** {paper['atp_risk_level']}",
        )

        if paper.get("pdf_url"):
            parts.append(f"**PDF:** {paper['pdf_url']}")

        if paper.get("authors"):
            import json

            authors = json.loads(paper["authors"])
            if authors:
                author_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    author_str += " et al."
                parts.append(f"**Authors:** {author_str}")

        if not compact and paper.get("abstract"):
            parts.append("")
            parts.append(f"**Abstract:** {paper['abstract'][:300]}...")

        if not compact:
            parts.append("")
            parts.append("**Evaluation:**")
            parts.append(
                f"- Purpose Alignment ({paper['purpose_alignment']:.0f}): {paper['purpose_reasoning']}",
            )
            parts.append(
                f"- Technical Merit ({paper['technical_merit']:.0f}): {paper['technical_reasoning']}",
            )
            parts.append(
                f"- Adoption Potential ({paper['adoption_potential']:.0f}): {paper['adoption_reasoning']}",
            )

            if paper.get("brakes"):
                import json

                brakes = json.loads(paper["brakes"])
                if brakes:
                    parts.append("")
                    parts.append("**Concerns (Brakes):**")
                    for brake in brakes:
                        parts.append(f"- {brake}")

        parts.append("")
        return parts

    def _format_intel_event_entry(self, event: dict, urgent: bool = False) -> list[str]:
        """Format an IntelEvent entry for the briefing"""
        parts = []

        title = event.get("title", "Untitled Event")
        if urgent:
            urgency = event.get("urgency_score", 0)
            parts.append(f"#### ⚠️ {title}")
            parts.append(f"**Urgency Score:** {urgency:.2f}")
        else:
            parts.append(f"#### {title}")

        parts.append(
            f"**Source Type:** {event.get('source_type', 'Unknown')} | **Jurisdiction:** {event.get('jurisdiction', 'Global')}",
        )

        if event.get("effective_date"):
            parts.append(f"**Effective Date:** {event['effective_date']}")

        if event.get("jr_total_score"):
            parts.append(
                f"**JR Score:** {event['jr_total_score']:.1f} | **Tier:** {event.get('jr_tier', 'N/A')} | **ATP Risk:** {event.get('jr_atp_risk_level', 'N/A')}",
            )

        if event.get("summary"):
            parts.append(f"\n{event['summary']}")

        # Show impacts
        if event.get("impacts"):
            try:
                impacts = (
                    json.loads(event["impacts"])
                    if isinstance(event["impacts"], str)
                    else event["impacts"]
                )
                if impacts:
                    parts.append("\n**Business Impacts:**")
                    for imp in impacts[:3]:
                        severity = imp.get("severity", "medium").upper()
                        parts.append(f"- [{severity}] {imp.get('description', '')}")
            except (json.JSONDecodeError, TypeError):
                pass

        # Show risk tags
        if event.get("risk_tags"):
            try:
                tags = (
                    json.loads(event["risk_tags"])
                    if isinstance(event["risk_tags"], str)
                    else event["risk_tags"]
                )
                if tags:
                    parts.append(f"\n**Risk Tags:** {', '.join(tags[:5])}")
            except (json.JSONDecodeError, TypeError):
                pass

        parts.append(f"\n**Source:** {event.get('source_url', 'N/A')}")
        parts.append("")
        return parts

    def _generate_summary(self, tier_summary: dict, intel_events_data: dict | None = None) -> str:
        """Generate a brief text summary"""
        total = sum([tier_summary.get(t, {}).get("total", 0) for t in [1, 2, 3, 4]])
        tier1 = tier_summary.get(1, {}).get("total", 0)
        tier2 = tier_summary.get(2, {}).get("total", 0)

        summary = (
            f"Processed {total} intelligence items. "
            f"{tier1} require executive review (Tier 1), "
            f"{tier2} approved for auto-action (Tier 2)."
        )

        # Add IntelEvent summary
        if intel_events_data and intel_events_data.get("total_events", 0) > 0:
            high_urgency = len(intel_events_data.get("high_urgency", []))
            deadlines = len(intel_events_data.get("upcoming_deadlines", []))
            summary += f" {intel_events_data['total_events']} Gemini-normalized events"
            if high_urgency > 0:
                summary += f" ({high_urgency} high urgency)"
            if deadlines > 0:
                summary += f", {deadlines} upcoming deadlines"
            summary += "."

        return summary


# Convenience function
def generate_briefing() -> str:
    """Generate briefing from current database

    Usage:
        briefing_file = generate_briefing()
    """
    generator = BriefingGenerator()
    return generator.generate_briefing()
