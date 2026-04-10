"""
Latency Histogram Widget
Inspired by Bottom's CPU graph visualization
Shows distribution of decision latencies with p50/p90/p99 markers
"""

from collections import Counter

from rich.text import Text
from textual.widgets import Static


class LatencyHistogramWidget(Static):
    """Histogram visualization of latency distribution"""

    def __init__(self, stats, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats

    def render(self) -> Text:
        if not self.stats.samples:
            return Text("Waiting for data...", style="dim")

        # Convert to ms and bucket into 10ms intervals
        latencies_ms = [s / 1000.0 for s in self.stats.samples]
        buckets = Counter(int(l // 10) * 10 for l in latencies_ms)

        if not buckets:
            return Text("No data", style="dim")

        # Calculate histogram
        max_count = max(buckets.values())
        max_bucket = max(buckets.keys())

        text = Text()
        text.append("📊 Latency Distribution (ms)\n\n", style="bold cyan")

        # Draw histogram bars
        for bucket in range(0, min(max_bucket + 20, 200), 10):
            count = buckets.get(bucket, 0)
            if count == 0 and bucket > max_bucket + 10:
                continue

            # Calculate bar width (max 40 chars)
            bar_width = int((count / max_count) * 40) if max_count > 0 else 0
            bar = "█" * bar_width

            # Color based on SLA
            if bucket < 50:
                color = "green"
            elif bucket < 75:
                color = "yellow"
            elif bucket < 90:
                color = "orange"
            else:
                color = "red"

            text.append(f"{bucket:3d}-{bucket + 9:3d}: ", style="dim")
            text.append(f"{bar} ", style=color)
            text.append(f"({count})\n", style="dim")

        # Add percentile markers
        text.append("\n", style="dim")
        text.append(f"p50: {self.stats.p50:.1f}ms | ", style="green")
        text.append(f"p90: {self.stats.p90:.1f}ms | ", style="yellow")
        text.append(f"p99: {self.stats.p99:.1f}ms", style="red" if self.stats.p99 > 90 else "green")

        return text
