#!/usr/bin/env python3
"""
Judge#6 Governance Enforcement Monitor
Inspired by Bottom's architecture: https://github.com/ClementTsang/bottom

PATTERN MAPPINGS (Bottom → Judge#6):
- Bottom's CPU sparkline → Judge#6 decision latency sparkline
- Bottom's process table → Violation events table
- Bottom's update loop → Enforcement decision loop
- Bottom's p99 <50ms target → Judge#6 p99 ≤90ms SLA

USAGE:
    python3 tui/judge6_monitor.py --mode=mock    # Simulated decisions
    python3 tui/judge6_monitor.py --mode=live    # Connect to real Judge#6
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, DataTable
from textual.binding import Binding
from rich.text import Text

# Import histogram widget
try:
    from tui.widgets import LatencyHistogramWidget
except ImportError:
    # Fallback if running from project root
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from widgets import LatencyHistogramWidget


@dataclass
class DecisionMetric:
    """Single governance decision measurement"""
    timestamp: float
    latency_us: int  # microseconds
    result: str  # "PASS" | "FAIL" | "ERROR"
    violation_type: str = ""

    @property
    def latency_ms(self) -> float:
        return self.latency_us / 1000.0

    @property
    def meets_sla(self) -> bool:
        """Check if latency meets p99 ≤90ms SLA"""
        return self.latency_ms <= 90.0


class LatencyStats:
    """Bottom-style latency tracking (judge6/runtime/profiling.py + enhancements)"""

    def __init__(self, window_size: int = 1000):
        self.samples: deque[int] = deque(maxlen=window_size)
        self.violations: deque[DecisionMetric] = deque(maxlen=100)

    def record(self, metric: DecisionMetric):
        self.samples.append(metric.latency_us)
        if metric.result == "FAIL":
            self.violations.append(metric)

    def percentile(self, p: float) -> float:
        """Calculate percentile in milliseconds"""
        if not self.samples:
            return 0.0
        sorted_samples = sorted(self.samples)
        index = int(len(sorted_samples) * p)
        if index >= len(sorted_samples):
            index = len(sorted_samples) - 1
        return sorted_samples[index] / 1000.0  # Convert to ms

    @property
    def p50(self) -> float:
        return self.percentile(0.50)

    @property
    def p90(self) -> float:
        return self.percentile(0.90)

    @property
    def p99(self) -> float:
        return self.percentile(0.99)

    @property
    def sla_compliance(self) -> float:
        """Percentage of decisions meeting p99 ≤90ms SLA"""
        if not self.samples:
            return 100.0
        under_sla = sum(1 for s in self.samples if s / 1000.0 <= 90.0)
        return (under_sla / len(self.samples)) * 100.0


class MockJudge6Engine:
    """Simulated Judge#6 enforcement engine for latency testing

    Models realistic decision patterns:
    - p50: 15-25ms (fast path: cached decisions)
    - p90: 40-60ms (medium path: simple ATP_519_scan)
    - p99: 70-120ms (slow path: complex policy eval + occasional spikes)
    """

    def __init__(self):
        self.decision_count = 0
        self.patterns = [
            ("NO_PII", 0.95, (10_000, 30_000)),    # 95%: Fast path
            ("SSN_DETECTED", 0.03, (40_000, 70_000)),  # 3%: Medium path
            ("CCN_DETECTED", 0.015, (60_000, 100_000)),  # 1.5%: Slow path
            ("TIMEOUT", 0.005, (150_000, 300_000)),  # 0.5%: p99+ spikes
        ]

    async def make_decision(self) -> DecisionMetric:
        """Simulate a single governance decision"""
        import random

        # Select pattern based on probability distribution
        rand = random.random()
        cumulative = 0.0
        for pattern, prob, (min_us, max_us) in self.patterns:
            cumulative += prob
            if rand <= cumulative:
                latency_us = random.randint(min_us, max_us)
                result = "FAIL" if pattern != "NO_PII" else "PASS"

                # Simulate actual decision work
                await asyncio.sleep(latency_us / 1_000_000.0)

                self.decision_count += 1
                return DecisionMetric(
                    timestamp=time.time(),
                    latency_us=latency_us,
                    result=result,
                    violation_type=pattern if result == "FAIL" else ""
                )

        # Fallback (shouldn't reach)
        return DecisionMetric(
            timestamp=time.time(),
            latency_us=20_000,
            result="PASS",
        )


class LatencySparklineWidget(Static):
    """Bottom-style sparkline for decision latency (inspired by cpu_graph.rs)"""

    def __init__(self, stats: LatencyStats, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats
        self.history: deque[float] = deque(maxlen=60)  # 60 seconds of history

    def update_data(self):
        """Update sparkline with latest p99"""
        self.history.append(self.stats.p99)

    def render(self) -> Text:
        if not self.history:
            return Text("Waiting for data...", style="dim")

        # Determine if SLA is violated
        current_p99 = self.history[-1]
        if current_p99 > 90.0:
            color = "red bold"
            status = "⚠️  SLA VIOLATION"
        elif current_p99 > 75.0:
            color = "yellow"
            status = "⚡ Near Limit"
        else:
            color = "green"
            status = "✓ Within SLA"

        # Format display
        text = Text()
        text.append("p99 Latency: ", style="bold")
        text.append(f"{current_p99:.1f}ms ", style=color)
        text.append(f"({status})\n", style=color)
        text.append("Target: ≤90ms | ", style="dim")
        text.append(f"p50: {self.stats.p50:.1f}ms | ", style="cyan")
        text.append(f"p90: {self.stats.p90:.1f}ms", style="yellow")

        return text


class ViolationTableWidget(Static):
    """Bottom-style process table → violation events table"""

    def __init__(self, stats: LatencyStats, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats
        self.table = DataTable()

    def compose(self) -> ComposeResult:
        yield self.table

    def on_mount(self):
        self.table.add_columns("Timestamp", "Type", "Latency (ms)")
        self.table.cursor_type = "row"

    def update_data(self):
        """Refresh table with latest violations"""
        self.table.clear()
        for v in list(self.stats.violations)[-10:]:  # Last 10 violations
            timestamp = datetime.fromtimestamp(v.timestamp).strftime("%H:%M:%S")
            self.table.add_row(
                timestamp,
                v.violation_type,
                f"{v.latency_ms:.1f}"
            )


class DecisionRateWidget(Static):
    """Bottom-style metrics display"""

    def __init__(self, engine: MockJudge6Engine, stats: LatencyStats, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.stats = stats
        self.start_time = time.time()

    def render(self) -> Text:
        uptime = time.time() - self.start_time
        decisions_per_sec = self.engine.decision_count / uptime if uptime > 0 else 0

        text = Text()
        text.append("📊 Performance Metrics\n\n", style="bold cyan")
        text.append("Total Decisions: ", style="dim")
        text.append(f"{self.engine.decision_count:,}\n", style="bold")
        text.append("Decision Rate: ", style="dim")
        text.append(f"{decisions_per_sec:.1f}/sec\n", style="bold")
        text.append("Violations: ", style="dim")
        text.append(f"{len(self.stats.violations)}\n", style="bold red")
        text.append("SLA Compliance: ", style="dim")

        compliance = self.stats.sla_compliance
        if compliance >= 99.0:
            style = "bold green"
        elif compliance >= 95.0:
            style = "bold yellow"
        else:
            style = "bold red"
        text.append(f"{compliance:.1f}%", style=style)

        return text


class Judge6MonitorApp(App):
    """Judge#6 Governance Enforcement Monitor (Bottom-inspired architecture)"""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 100%;
        padding: 1;
    }

    #top-row {
        height: 8;
        margin-bottom: 1;
    }

    #latency-widget {
        border: solid $primary;
        padding: 1;
        width: 2fr;
    }

    #metrics-widget {
        border: solid $accent;
        padding: 1;
        width: 1fr;
    }

    #violation-widget {
        border: solid $warning;
        padding: 1;
    }

    #histogram-widget {
        border: solid $success;
        padding: 1;
        height: 20;
    }

    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
    }
    """

    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("r", "reset_stats", "Reset Stats"),
        Binding("p", "pause", "Pause/Resume"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, mode: str = "mock", **kwargs):
        super().__init__(**kwargs)
        self.mode = mode

        # Use factory to get the right engine
        if mode == "live":
            try:
                from tui.judge6_engine_live import RealJudge6Engine
                self.engine = RealJudge6Engine()
                self.title = "Judge#6 Monitor (LIVE)"
            except ImportError as e:
                self.notify(f"Failed to load live engine: {e}", severity="error")
                self.engine = MockJudge6Engine()
                self.mode = "mock"
                self.title = "Judge#6 Monitor (Mock - Live Failed)"
        elif mode == "edgequeue":
            try:
                from tui.judge6_engine_edgequeue import EdgeQueueEngine
                self.engine = EdgeQueueEngine()
                self.title = "Judge#6 Monitor (EdgeQueue)"
            except ImportError as e:
                self.notify(f"Failed to load EdgeQueue engine: {e}", severity="error")
                self.engine = MockJudge6Engine()
                self.mode = "mock"
                self.title = "Judge#6 Monitor (Mock - EdgeQueue Failed)"
        else:
            self.engine = MockJudge6Engine()
            self.title = "Judge#6 Monitor (Mock)"

        self.stats = LatencyStats()
        self.paused = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"⚖️  {self.title}", classes="title"),
            Horizontal(
                LatencySparklineWidget(self.stats, id="latency-widget"),
                DecisionRateWidget(self.engine, self.stats, id="metrics-widget"),
                id="top-row"
            ),
            LatencyHistogramWidget(self.stats, id="histogram-widget"),
            ViolationTableWidget(self.stats, id="violation-widget"),
            id="main-container"
        )
        yield Footer()

    def on_mount(self):
        """Start decision loop (Bottom's main loop equivalent)"""
        self.update_timer = self.set_interval(1/60, self.update_display)  # 60Hz like Bottom
        self.decision_timer = self.set_interval(0.1, self.run_decision)   # 10 decisions/sec

    async def run_decision(self):
        """Execute one governance decision (Bottom's data collection equivalent)"""
        if self.paused:
            return

        metric = await self.engine.make_decision()
        self.stats.record(metric)

    def update_display(self):
        """Redraw widgets (Bottom's immediate-mode render loop)"""
        latency_widget = self.query_one("#latency-widget", LatencySparklineWidget)
        metrics_widget = self.query_one("#metrics-widget", DecisionRateWidget)
        violation_widget = self.query_one("#violation-widget", ViolationTableWidget)

        latency_widget.update_data()
        latency_widget.refresh()
        metrics_widget.refresh()
        violation_widget.update_data()

    def action_toggle_dark(self):
        self.dark = not self.dark

    def action_reset_stats(self):
        self.stats = LatencyStats()
        self.engine.decision_count = 0
        self.notify("Stats reset")

    def action_pause(self):
        self.paused = not self.paused
        status = "Paused" if self.paused else "Resumed"
        self.notify(status)


if __name__ == "__main__":
    import sys

    mode = "mock"
    if len(sys.argv) > 1 and sys.argv[1].startswith("--mode="):
        mode = sys.argv[1].split("=")[1]

    app = Judge6MonitorApp(mode=mode)
    app.run()
