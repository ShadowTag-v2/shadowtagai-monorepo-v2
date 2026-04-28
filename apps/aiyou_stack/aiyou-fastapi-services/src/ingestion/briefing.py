# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AM Briefing Generator - Morning Intelligence Summary.

Generates daily briefings from collected and classified intelligence:
- Executive summary
- Top Tier 1 items
- Trending topics
- Source coverage
- Anomalies and alerts
"""

import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from .tiers import ClassifiedItem, DataTier
from .visualizer import BriefingVisualizer

logger = logging.getLogger(__name__)


@dataclass
class BriefingSection:
    """A section of the briefing."""

    title: str
    content: str
    priority: int  # 1=highest


@dataclass
class DailyBriefing:
    """Daily AM briefing."""

    date: datetime
    sections: list[BriefingSection]
    metadata: dict

    # Statistics
    total_items: int
    tier_1_items: int
    tier_2_items: int
    tier_3_items: int
    sources_covered: int

    def to_markdown(self, include_visualizations: bool = True) -> str:
        """Convert briefing to markdown format."""
        md = "# Daily Intelligence Briefing\n"
        md += f"**Date**: {self.date.strftime('%Y-%m-%d %A')}\n\n"

        # Stats
        md += "## Summary Statistics\n\n"
        md += f"- **Total Items Collected**: {self.total_items}\n"
        md += f"- **Tier 1 (High Value)**: {self.tier_1_items}\n"
        md += f"- **Tier 2 (Medium Value)**: {self.tier_2_items}\n"
        md += f"- **Tier 3 (Low Value)**: {self.tier_3_items}\n"
        md += f"- **Sources Covered**: {self.sources_covered}\n\n"

        # Add visualizations if enabled
        if include_visualizations and "visualizations" in self.metadata:
            md += "## 📊 Visualizations\n\n"
            for viz in self.metadata["visualizations"]:
                md += f"{viz}\n\n"

        # Sections
        for section in sorted(self.sections, key=lambda s: s.priority):
            md += f"## {section.title}\n\n"
            md += f"{section.content}\n\n"

        return md


class BriefingGenerator:
    """Generates daily AM briefings from intelligence data.

    Features:
    - Executive summary
    - Top Tier 1 items
    - Trending topics
    - Source coverage analysis
    - Alerts and anomalies
    """

    def __init__(
        self,
        max_tier1_items: int = 10,
        max_trending_topics: int = 5,
        enable_visualizations: bool = True,
        visualization_format: str = "mermaid",
    ):
        self.max_tier1_items = max_tier1_items
        self.max_trending_topics = max_trending_topics
        self.enable_visualizations = enable_visualizations
        self.visualizer = (
            BriefingVisualizer(output_format=visualization_format)
            if enable_visualizations
            else None
        )

    async def generate_briefing(
        self,
        classified_items: list[ClassifiedItem],
        source_stats: dict,
        compliance_stats: dict,
    ) -> DailyBriefing:
        """Generate a daily briefing.

        Args:
            classified_items: Classified intelligence items
            source_stats: Statistics from source collection
            compliance_stats: Ethics/compliance statistics

        Returns:
            DailyBriefing ready for delivery

        """
        logger.info(f"Generating briefing for {len(classified_items)} items...")

        # Separate by tier
        tier1_items = [i for i in classified_items if i.tier == DataTier.TIER_1]
        tier2_items = [i for i in classified_items if i.tier == DataTier.TIER_2]
        tier3_items = [i for i in classified_items if i.tier == DataTier.TIER_3]

        sections = []

        # 1. Executive Summary
        sections.append(
            self._generate_executive_summary(tier1_items, tier2_items, tier3_items, source_stats),
        )

        # 2. Top Tier 1 Items
        if tier1_items:
            sections.append(self._generate_top_items(tier1_items))

        # 3. Trending Topics
        sections.append(self._generate_trending_topics(classified_items))

        # 4. Source Coverage
        sections.append(self._generate_source_coverage(source_stats))

        # 5. Compliance Report
        sections.append(self._generate_compliance_report(compliance_stats))

        # 6. Alerts (if any)
        alerts = self._generate_alerts(tier1_items, source_stats, compliance_stats)
        if alerts:
            sections.append(alerts)

        # Generate visualizations if enabled
        visualizations = []
        if self.visualizer:
            # Tier distribution chart
            tier_chart = self.visualizer.generate_tier_distribution_chart(
                len(tier1_items),
                len(tier2_items),
                len(tier3_items),
            )
            visualizations.append(tier_chart)

            # Source coverage chart
            coverage_by_type = source_stats.get("coverage_by_type", {})
            source_chart_data = {
                k: v.get("items_collected", 0) for k, v in coverage_by_type.items()
            }
            if source_chart_data:
                source_chart = self.visualizer.generate_source_coverage_chart(source_chart_data)
                visualizations.append(source_chart)

        briefing = DailyBriefing(
            date=datetime.now(),
            sections=sections,
            metadata={
                "generation_time": datetime.now().isoformat(),
                "version": "1.0",
                "visualizations": visualizations,
            },
            total_items=len(classified_items),
            tier_1_items=len(tier1_items),
            tier_2_items=len(tier2_items),
            tier_3_items=len(tier3_items),
            sources_covered=source_stats.get("sources_crawled_today", 0),
        )

        logger.info("✓ Briefing generated successfully")
        return briefing

    def _generate_executive_summary(
        self,
        tier1_items: list[ClassifiedItem],
        tier2_items: list[ClassifiedItem],
        tier3_items: list[ClassifiedItem],
        source_stats: dict,
    ) -> BriefingSection:
        """Generate executive summary."""
        total = len(tier1_items) + len(tier2_items) + len(tier3_items)

        content = f"Collected **{total} intelligence items** from "
        content += f"**{source_stats.get('sources_crawled_today', 0)} sources** "
        content += "during the nightly ingestion run.\n\n"

        if tier1_items:
            content += f"**{len(tier1_items)} high-value items** (Tier 1) identified, "
            content += "representing timely, relevant, and credible intelligence. "
        else:
            content += (
                "⚠️ **No Tier 1 items** identified. Consider adjusting collection criteria.\n\n"
            )

        # Quality assessment
        quality_pct = (len(tier1_items) / total * 100) if total > 0 else 0
        if quality_pct >= 20:
            content += f"\n✓ **Quality Score**: {quality_pct:.1f}% - Good signal-to-noise ratio."
        elif quality_pct >= 10:
            content += f"\n⚠ **Quality Score**: {quality_pct:.1f}% - Moderate quality."
        else:
            content += f"\n❌ **Quality Score**: {quality_pct:.1f}% - Low quality, mostly noise."

        return BriefingSection(
            title="Executive Summary",
            content=content,
            priority=1,
        )

    def _generate_top_items(self, tier1_items: list[ClassifiedItem]) -> BriefingSection:
        """Generate top Tier 1 items section."""
        # Sort by relevance score
        sorted_items = sorted(
            tier1_items,
            key=lambda i: i.scores.relevance,
            reverse=True,
        )[: self.max_tier1_items]

        content = "### Highest-Priority Intelligence\n\n"

        for i, item in enumerate(sorted_items, 1):
            source = item.content.get("source", "unknown")
            title = item.content.get("content", "")[:100]
            relevance = item.scores.relevance
            url = item.content.get("url", "")

            content += f"**{i}. {title}**\n"
            content += f"   - Source: {source}\n"
            content += f"   - Relevance: {relevance:.2f}\n"
            content += f"   - Reasons: {', '.join(item.reasons)}\n"
            if url:
                content += f"   - URL: {url}\n"
            content += "\n"

        return BriefingSection(
            title="Top Intelligence Items",
            content=content,
            priority=2,
        )

    def _generate_trending_topics(self, items: list[ClassifiedItem]) -> BriefingSection:
        """Extract and report trending topics."""
        # Extract keywords from Tier 1 and Tier 2 items
        keywords = []
        for item in items:
            if item.tier in [DataTier.TIER_1, DataTier.TIER_2]:
                content = item.content.get("content", "").lower()
                # Simple keyword extraction (production would use NLP)
                words = content.split()
                keywords.extend([w for w in words if len(w) > 5])

        # Count frequencies
        topic_counts = Counter(keywords).most_common(self.max_trending_topics)

        content = "### Most Discussed Topics\n\n"

        if topic_counts:
            for topic, count in topic_counts:
                content += f"- **{topic}**: {count} mentions\n"
        else:
            content += "No significant trending topics identified.\n"

        return BriefingSection(
            title="Trending Topics",
            content=content,
            priority=3,
        )

    def _generate_source_coverage(self, source_stats: dict) -> BriefingSection:
        """Generate source coverage report."""
        content = "### Coverage by Source Type\n\n"

        coverage = source_stats.get("coverage_by_type", {})

        for source_type, stats in coverage.items():
            enabled = stats.get("enabled", 0)
            items = stats.get("items_collected", 0)
            errors = stats.get("errors", 0)

            content += f"- **{source_type.title()}**: "
            content += f"{items} items from {enabled} source(s)"

            if errors > 0:
                content += f" ⚠️ {errors} error(s)"

            content += "\n"

        return BriefingSection(
            title="Source Coverage",
            content=content,
            priority=4,
        )

    def _generate_compliance_report(self, compliance_stats: dict) -> BriefingSection:
        """Generate ethical compliance report."""
        content = "### Ethical Compliance\n\n"

        allowed = compliance_stats.get("allowed", 0)
        total = compliance_stats.get("total_checks", 0)
        robots_blocked = compliance_stats.get("blocked_by_robots_txt", 0)
        rate_blocked = compliance_stats.get("blocked_by_rate_limit", 0)

        if total > 0:
            content += f"- **Compliance Rate**: {allowed / total * 100:.1f}%\n"
            content += f"- **Blocked by robots.txt**: {robots_blocked}\n"
            content += f"- **Blocked by rate limits**: {rate_blocked}\n"
            content += f"- **Total checks**: {total}\n"

            if allowed / total >= 0.9:
                content += "\n✓ **Excellent compliance** with ethical guidelines."
            else:
                content += "\n⚠️ High blocking rate may indicate aggressive crawling."
        else:
            content += "No compliance data available.\n"

        return BriefingSection(
            title="Compliance Report",
            content=content,
            priority=5,
        )

    def _generate_alerts(
        self,
        tier1_items: list[ClassifiedItem],
        source_stats: dict,
        compliance_stats: dict,
    ) -> BriefingSection | None:
        """Generate alerts for anomalies."""
        alerts = []

        # Check for low Tier 1 count
        if len(tier1_items) < 5:
            alerts.append("⚠️ Low Tier 1 item count - review collection criteria")

        # Check for source failures
        errors_by_source = source_stats.get("errors_by_source", {})
        if errors_by_source:
            failing_sources = [s for s, e in errors_by_source.items() if e > 3]
            if failing_sources:
                alerts.append(f"⚠️ Multiple failures: {', '.join(failing_sources)}")

        # Check compliance issues
        total = compliance_stats.get("total_checks", 0)
        blocked = compliance_stats.get("blocked_by_robots_txt", 0)
        if total > 0 and blocked / total > 0.3:
            alerts.append("⚠️ High robots.txt blocking rate - review crawl permissions")

        if not alerts:
            return None

        content = "\n".join(alerts)

        return BriefingSection(
            title="⚠️ Alerts & Anomalies",
            content=content,
            priority=0,  # Highest priority
        )
