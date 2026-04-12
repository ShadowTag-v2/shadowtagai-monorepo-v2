"""
Visualization generator for briefings.

Creates charts and graphs for intelligence data:
- Tier distribution pie charts
- Source coverage bar charts
- Trend lines for metrics
- Compliance heatmaps
"""

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ChartData:
    """Data for a chart."""

    title: str
    chart_type: str  # bar, pie, line, heatmap
    data: dict
    options: dict


class BriefingVisualizer:
    """
    Generates visualizations for briefings.

    Outputs:
    - ASCII charts (terminal-friendly)
    - Matplotlib charts (PNG)
    - Plotly charts (HTML interactive)
    - Mermaid diagrams (Markdown-embeddable)
    """

    def __init__(self, output_format: str = "ascii"):
        """
        Initialize visualizer.

        Args:
            output_format: ascii, matplotlib, plotly, mermaid
        """
        self.output_format = output_format

    def generate_tier_distribution_chart(
        self,
        tier1_count: int,
        tier2_count: int,
        tier3_count: int,
    ) -> str:
        """Generate tier distribution visualization."""
        total = tier1_count + tier2_count + tier3_count

        if self.output_format == "ascii":
            return self._ascii_pie_chart(
                {
                    "Tier 1 (High)": tier1_count,
                    "Tier 2 (Med)": tier2_count,
                    "Tier 3 (Low)": tier3_count,
                },
                title="Tier Distribution",
            )
        elif self.output_format == "mermaid":
            return self._mermaid_pie_chart(
                {
                    "Tier 1": tier1_count,
                    "Tier 2": tier2_count,
                    "Tier 3": tier3_count,
                }
            )
        else:
            return f"Tier Distribution: T1={tier1_count}, T2={tier2_count}, T3={tier3_count}"

    def generate_source_coverage_chart(
        self,
        source_stats: dict[str, int],
    ) -> str:
        """Generate source coverage bar chart."""
        if self.output_format == "ascii":
            return self._ascii_bar_chart(
                source_stats,
                title="Items by Source Type",
            )
        elif self.output_format == "mermaid":
            # Mermaid bar chart
            lines = ["```mermaid", "xychart-beta", '    title "Items by Source Type"']
            lines.append("    x-axis [" + ", ".join(f'"{k}"' for k in source_stats) + "]")
            lines.append('    y-axis "Items Collected"')
            lines.append("    bar [" + ", ".join(str(v) for v in source_stats.values()) + "]")
            lines.append("```")
            return "\n".join(lines)
        else:
            return f"Source Coverage: {source_stats}"

    def generate_compliance_trend(
        self,
        compliance_history: list[dict],
    ) -> str:
        """Generate compliance trend line chart."""
        if self.output_format == "ascii":
            # Extract compliance scores
            scores = [h.get("score", 0) for h in compliance_history]
            dates = [h.get("date", "").split("T")[0] for h in compliance_history]

            return self._ascii_line_chart(
                dates,
                scores,
                title="Compliance Score Trend (7 days)",
                y_label="Score %",
            )
        elif self.output_format == "mermaid":
            # Mermaid line chart
            lines = ["```mermaid", "xychart-beta", '    title "Compliance Trend"']
            dates = [h.get("date", "").split("T")[0][-5:] for h in compliance_history]
            scores = [h.get("score", 0) for h in compliance_history]
            lines.append("    x-axis [" + ", ".join(f'"{d}"' for d in dates) + "]")
            lines.append('    y-axis "Score %" 0 --> 100')
            lines.append("    line [" + ", ".join(str(s) for s in scores) + "]")
            lines.append("```")
            return "\n".join(lines)
        else:
            return "Compliance trend chart"

    def generate_cost_breakdown(
        self,
        cost_data: dict[str, float],
    ) -> str:
        """Generate cost breakdown pie chart."""
        if self.output_format == "ascii":
            return self._ascii_pie_chart(
                cost_data,
                title="Monthly Cost Breakdown",
            )
        elif self.output_format == "mermaid":
            return self._mermaid_pie_chart(cost_data, title="Cost Breakdown")
        else:
            return f"Costs: {cost_data}"

    def _ascii_bar_chart(
        self,
        data: dict[str, int],
        title: str = "",
        max_width: int = 50,
    ) -> str:
        """Create ASCII bar chart."""
        if not data:
            return "No data"

        lines = []

        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        # Find max value for scaling
        max_value = max(data.values()) if data.values() else 1

        for label, value in sorted(data.items(), key=lambda x: -x[1]):
            # Scale bar length
            bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
            bar = "█" * bar_length

            # Format line
            lines.append(f"{label:20s} │{bar} {value:>6}")

        return "\n".join(lines)

    def _ascii_pie_chart(
        self,
        data: dict[str, int],
        title: str = "",
    ) -> str:
        """Create ASCII pie chart."""
        if not data:
            return "No data"

        lines = []

        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        total = sum(data.values())
        if total == 0:
            return "No data"

        for label, value in sorted(data.items(), key=lambda x: -x[1]):
            percentage = (value / total) * 100
            # Create visual bar
            bar_length = int(percentage / 2)  # 50 chars = 100%
            bar = "●" * bar_length

            lines.append(f"{label:20s} │{bar} {percentage:5.1f}% ({value:>5})")

        return "\n".join(lines)

    def _ascii_line_chart(
        self,
        x_values: list[str],
        y_values: list[float],
        title: str = "",
        y_label: str = "Value",
        height: int = 10,
    ) -> str:
        """Create ASCII line chart."""
        if not x_values or not y_values:
            return "No data"

        lines = []

        if title:
            lines.append(f"\n{title}")
            lines.append("=" * len(title))

        # Find min/max for scaling
        min_y = min(y_values)
        max_y = max(y_values)
        range_y = max_y - min_y if max_y != min_y else 1

        # Create chart
        for row in range(height, -1, -1):
            threshold = min_y + (range_y * row / height)
            line = f"{threshold:>6.1f} │"

            for y in y_values:
                if y >= threshold:
                    line += "●"
                else:
                    line += " "

            lines.append(line)

        # X-axis
        lines.append("       └" + "─" * len(x_values))

        # Labels (every nth label to avoid crowding)
        step = max(1, len(x_values) // 5)
        x_line = "        "
        for i, label in enumerate(x_values):
            if i % step == 0:
                x_line += label[:5].ljust(5)

        lines.append(x_line)
        lines.append(f"\n{y_label}")

        return "\n".join(lines)

    def _mermaid_pie_chart(
        self,
        data: dict[str, float],
        title: str = "Distribution",
    ) -> str:
        """Create Mermaid pie chart."""
        lines = ["```mermaid", "pie", f"    title {title}"]

        for label, value in data.items():
            lines.append(f'    "{label}" : {value}')

        lines.append("```")
        return "\n".join(lines)

    def generate_quality_scorecard(
        self,
        metrics: dict[str, float],
        targets: dict[str, float],
    ) -> str:
        """Generate visual scorecard comparing metrics to targets."""
        lines = ["\n### Quality Scorecard", ""]

        for metric, value in metrics.items():
            target = targets.get(metric, 0)
            percentage = (value / target * 100) if target > 0 else 0
            status = "✅" if value >= target else "⚠️" if value >= target * 0.8 else "❌"

            # Progress bar
            bar_length = min(50, int(percentage / 2))
            bar = "█" * bar_length

            lines.append(f"**{metric}**")
            lines.append(f"{status} {value:.1f} / {target:.1f} │{bar} {percentage:.0f}%")
            lines.append("")

        return "\n".join(lines)

    def generate_dashboard_summary(
        self,
        tier_dist: dict[str, int],
        source_stats: dict[str, int],
        compliance_score: float,
        cost_current: float,
        cost_budget: float,
    ) -> str:
        """Generate comprehensive dashboard with multiple visualizations."""
        sections = []

        # Header
        sections.append("# Intelligence Dashboard")
        sections.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

        # 1. Tier Distribution
        sections.append("## 📊 Tier Distribution")
        sections.append(
            self.generate_tier_distribution_chart(
                tier_dist.get("tier_1", 0),
                tier_dist.get("tier_2", 0),
                tier_dist.get("tier_3", 0),
            )
        )

        # 2. Source Coverage
        sections.append("\n## 📡 Source Coverage")
        sections.append(self.generate_source_coverage_chart(source_stats))

        # 3. Quality Scorecard
        sections.append("\n## ✅ Quality Metrics")
        sections.append(
            self.generate_quality_scorecard(
                {
                    "Compliance Score": compliance_score,
                    "Budget Usage": (cost_current / cost_budget * 100) if cost_budget > 0 else 0,
                },
                {
                    "Compliance Score": 95.0,
                    "Budget Usage": 100.0,
                },
            )
        )

        # 4. Cost Summary
        sections.append("\n## 💰 Cost Summary")
        sections.append(f"- **Current**: ${cost_current:.2f}")
        sections.append(f"- **Budget**: ${cost_budget:.2f}")
        sections.append(f"- **Remaining**: ${cost_budget - cost_current:.2f}")

        utilization = (cost_current / cost_budget * 100) if cost_budget > 0 else 0
        bar_length = int(utilization / 2)
        bar = "█" * bar_length

        sections.append(f"\n{bar} {utilization:.1f}%")

        return "\n".join(sections)
