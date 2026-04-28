# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import time

from agents.autoresearch import minions
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from agents.swarm_boss import SwarmBoss


class SwarmDashboard:
    def __init__(self, boss: SwarmBoss, autoresearch: minions = None):
        self.boss = boss
        self.autoresearch = autoresearch
        self.console = Console()
        self.layout = Layout()  # Initialize layout here

    def generate_layout(self) -> Layout:
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        self.layout["main"].split_row(Layout(name="left", ratio=1), Layout(name="right", ratio=1))
        return self.layout

    def get_governance_panel(self) -> Panel:
        """Create the Governance Layer panel (replacing Agent Roster)"""
        if not self.autoresearch:
            return Panel("Governance Layer Offline", title="Governance")

        stats = self.autoresearch.get_governance_status()

        # Metrics Table
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(justify="right")
        grid.add_row("Active Agents:", str(stats["active_agents"]))
        grid.add_row("Approved Actions:", f"[green]{stats['approved_actions']}[/green]")
        grid.add_row("Blocked Actions:", f"[red]{stats['blocked_actions']}[/red]")
        grid.add_row("Avg Viability:", f"{stats['avg_viability']}/100")

        # Recent Decisions Log
        log_text = Text()
        log_text.append("\nRecent Decisions:\n", style="bold underline")
        for entry in stats["recent_decisions"]:
            color = "green" if entry["decision"] == "APPROVED" else "red"
            # Add competitor info if available
            competitor_info = (
                f" (vs {entry.get('competitor', 'Unknown')})" if "competitor" in entry else ""
            )
            log_text.append(
                f"[{color}]{entry['agent']}: {entry['decision']} - {entry['score']}{competitor_info}[/{color}]\n",
            )

        return Panel(
            Align.center(grid),
            title="[bold yellow]Governance, feat. proprietary, 'minion' agentic swarm.[/bold yellow]",
            subtitle=log_text,
        )

    def run(self):
        self.generate_layout()
        with Live(self.layout, refresh_per_second=4):
            while True:
                # Update Boss Logic (Facade)
                self.boss.step_tlp()
                report = self.boss.get_status_report()

                # Header
                header_text = Text(
                    f"Operation GLOW UP :: {report['tlp_step']} :: KOSMOS MODE",
                    style="bold white on blue",
                    justify="center",
                )
                self.layout["header"].update(Panel(header_text))

                # Governance Panel
                # Note: We are putting the governance panel in the 'left' slot for now
                self.layout["left"].update(self.get_governance_panel())

                # Right Panel (Placeholder for future expansion or Boss status)
                self.layout["right"].update(
                    Panel("Boss Status: Active\nMonitoring Flying minion...", title="Swarm Boss"),
                )

                # Footer
                # Use Flying minion metrics if available
                viability = 0
                if self.autoresearch:
                    stats = self.autoresearch.get_governance_status()
                    viability = stats["avg_viability"]

                color = "green" if viability >= 75 else "yellow" if viability >= 60 else "red"

                footer_text = (
                    f"Global Viability: [bold {color}]{viability}/100[/bold {color}] | "
                    f"Judge Status: [bold green]ACTIVE[/bold green] | "
                    f"Revenue Focus: [bold yellow]MAXIMIZED[/bold yellow]"
                )
                self.layout["footer"].update(Panel(footer_text, style="white on black"))

                time.sleep(0.25)


if __name__ == "__main__":
    # Mock for testing
    boss = SwarmBoss()
    minion = minions()
    minion.start()
    dash = SwarmDashboard(boss, minion)
    try:
        dash.run()
    except KeyboardInterrupt:
        minion.stop()
