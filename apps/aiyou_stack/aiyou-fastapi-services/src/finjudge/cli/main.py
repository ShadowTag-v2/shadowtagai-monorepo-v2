"""
FinJudge CLI - Main Command Interface
"""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from ..core.pure_judge import PureJudge
from ..models.judge import JudgeRequest, JudgeRuling

console = Console()


@click.group()
@click.version_option(version="0.2.0", prog_name="finjudge")
def cli():
    """
    FinJudge - Supreme Court Clerk for Financial Decisions

    Pure judge layer for risk classification using ATP 5-19 framework.

    Examples:
        finjudge eval decision.json
        finjudge eval decision.json -o ruling.json
        finjudge eval decision.json --format table
    """
    pass


@cli.command()
@click.argument("decision_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Save ruling to JSON file")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table", "summary"], case_sensitive=False),
    default="summary",
    help="Output format (json/table/summary)",
)
@click.option("--pretty/--no-pretty", default=True, help="Pretty print JSON output")
def eval(decision_file: Path, output: Path | None, format: str, pretty: bool):
    """
    Evaluate a financial decision using FinJudge

    Reads a decision JSON file, calls the Pure Judge engine, and displays
    the risk assessment ruling.

    DECISION_FILE: Path to JSON file containing JudgeRequest

    Examples:

        # Basic evaluation with summary output
        finjudge eval burn_rate_decision.json

        # Save full ruling to file
        finjudge eval trade_decision.json -o ruling.json

        # Display as table
        finjudge eval decision.json --format table
    """
    try:
        # Load decision file
        with open(decision_file) as f:
            decision_data = json.load(f)

        console.print(f"\n[bold blue]Loading decision from:[/bold blue] {decision_file}")

        # Parse request
        try:
            request = JudgeRequest(**decision_data)
        except Exception as e:
            console.print("[bold red]Error:[/bold red] Invalid decision file format")
            console.print(f"[red]{str(e)}[/red]")
            sys.exit(1)

        # Initialize judge
        console.print("[bold blue]Initializing Pure Judge engine...[/bold blue]")
        judge = PureJudge(version="v0.2.0")

        # Judge the decision
        console.print("[bold blue]Judging decision...[/bold blue]\n")
        ruling = judge.judge(request)

        # Display ruling
        if format == "json":
            _display_json(ruling, pretty)
        elif format == "table":
            _display_table(ruling)
        else:  # summary
            _display_summary(ruling)

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                json.dump(ruling.model_dump(mode="json"), f, indent=2, default=str)
            console.print(f"\n[bold green]✓[/bold green] Ruling saved to: {output}")

        # Exit code based on disposition
        exit_code = _get_exit_code(ruling)
        sys.exit(exit_code)

    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] File not found: {decision_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print("[bold red]Error:[/bold red] Invalid JSON in decision file")
        console.print(f"[red]{str(e)}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


def _display_json(ruling: JudgeRuling, pretty: bool):
    """Display ruling as JSON"""
    ruling_json = ruling.model_dump_json(indent=2 if pretty else None)

    if pretty:
        syntax = Syntax(ruling_json, "json", theme="monokai", line_numbers=False)
        console.print(syntax)
    else:
        console.print(ruling_json)


def _display_table(ruling: JudgeRuling):
    """Display ruling as formatted table"""

    # Risk Matrix Table
    risk_table = Table(
        title="Risk Matrix (ATP 5-19)", show_header=True, header_style="bold magenta"
    )
    risk_table.add_column("Metric", style="cyan", width=20)
    risk_table.add_column("Value", style="green")

    risk_table.add_row("Probability Class", ruling.risk_matrix.probability_class.value)
    risk_table.add_row("Severity Class", ruling.risk_matrix.severity_class.value)
    risk_table.add_row("Risk Level", f"[bold]{ruling.risk_matrix.risk_level.value}[/bold]")
    risk_table.add_row("Rationale", ruling.risk_matrix.rationale_summary)

    console.print(risk_table)
    console.print()

    # Recommendation Table
    rec_table = Table(title="Recommendation", show_header=True, header_style="bold magenta")
    rec_table.add_column("Aspect", style="cyan", width=20)
    rec_table.add_column("Details", style="yellow")

    rec_table.add_row("Disposition", f"[bold]{ruling.recommendation.disposition.value}[/bold]")

    if ruling.recommendation.required_controls:
        controls_text = "\n".join(f"• {c}" for c in ruling.recommendation.required_controls)
        rec_table.add_row("Required Controls", controls_text)

    if ruling.recommendation.time_boundaries:
        tb = ruling.recommendation.time_boundaries
        rec_table.add_row("Re-review If", tb.re_review_if)
        rec_table.add_row("Reassess In", f"{tb.reassess_in_days} days")

    console.print(rec_table)
    console.print()

    # Key Metrics Table
    if ruling.numeric_overview.key_metrics:
        metrics_table = Table(title="Key Metrics", show_header=True, header_style="bold magenta")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green", justify="right")

        for key, value in ruling.numeric_overview.key_metrics.items():
            metrics_table.add_row(key, str(value))

        metrics_table.add_row(
            "Primary Risk Driver", ruling.numeric_overview.primary_risk_driver, style="bold"
        )

        console.print(metrics_table)


def _display_summary(ruling: JudgeRuling):
    """Display ruling as formatted summary"""

    # Header
    risk_color = {"EXTREME": "red", "HIGH": "yellow", "MODERATE": "blue", "LOW": "green"}.get(
        ruling.risk_matrix.risk_level.value, "white"
    )

    console.print(
        Panel.fit(
            f"[bold {risk_color}]{ruling.risk_matrix.risk_level.value} RISK[/bold {risk_color}]\n"
            f"ATP 5-19 Classification: {ruling.risk_matrix.probability_class.value}-{ruling.risk_matrix.severity_class.value}\n"
            f"Disposition: [bold]{ruling.recommendation.disposition.value}[/bold]",
            title=f"Decision: {ruling.decision_id}",
            border_style=risk_color,
        )
    )

    console.print()

    # Explanation
    console.print("[bold underline]Summary:[/bold underline]")
    console.print(ruling.explanation_nl.short_summary)
    console.print()

    console.print("[bold underline]Details:[/bold underline]")
    for bullet in ruling.explanation_nl.detail_bullets:
        console.print(f"  • {bullet}")
    console.print()

    # Required Controls
    if ruling.recommendation.required_controls:
        console.print("[bold underline]Required Controls:[/bold underline]")
        for control in ruling.recommendation.required_controls:
            console.print(f"  [yellow]→[/yellow] {control}")
        console.print()

    # Time Boundaries
    if ruling.recommendation.time_boundaries:
        tb = ruling.recommendation.time_boundaries
        console.print("[bold underline]Time Boundaries:[/bold underline]")
        console.print(f"  • Re-review if: {tb.re_review_if}")
        console.print(f"  • Reassess in: {tb.reassess_in_days} days")
        console.print()

    # Audit Trail
    console.print(f"[dim]Judge Version: {ruling.judge_version}[/dim]")
    console.print(f"[dim]Timestamp: {ruling.timestamp}[/dim]")
    console.print(f"[dim]Input Hash: {ruling.audit_trail.input_hash[:16]}...[/dim]")


def _get_exit_code(ruling: JudgeRuling) -> int:
    """Get exit code based on ruling disposition"""
    from ..models.judge import Disposition

    exit_codes = {
        Disposition.APPROVE: 0,
        Disposition.MODIFY: 1,
        Disposition.ESCALATE: 2,
        Disposition.REJECT: 3,
    }

    return exit_codes.get(ruling.recommendation.disposition, 0)


@cli.command()
def demo():
    """
    Run demo evaluation with sample decision

    Demonstrates FinJudge with a pre-loaded burn rate increase scenario.
    """
    from uuid import uuid4

    from ..models.judge import (
        Actor,
        ActorRole,
        DecisionContext,
        Exposure,
        Flags,
        Metrics,
        Objective,
        TimeHorizon,
    )

    console.print("\n[bold blue]FinJudge Demo: Burn Rate Increase Scenario[/bold blue]\n")

    # Create sample decision
    request = JudgeRequest(
        decision_id=f"demo_{uuid4().hex[:8]}",
        module="financial_runway_monitor",
        actor=Actor(role=ActorRole.CFO, org_unit="Finance", jurisdiction="US"),
        intent_nl="Approve hiring 3 engineers, increasing monthly burn from $180k to $240k",
        context=DecisionContext(
            time_horizon=TimeHorizon.LONG_TERM,
            objective=Objective.ALPHA,
            constraints=["max_12mo_runway"],
        ),
        metrics=Metrics(
            exposure=Exposure(notional=720000.0, pct_aum=33.3, leverage_ratio=1.0),
            custom={
                "current_burn": 180000,
                "proposed_burn": 240000,
                "runway_months_current": 18,
                "runway_months_proposed": 13.5,
                "pct_increase": 33.3,
            },
        ),
        flags=Flags(policy_flags=["approaching_12mo_runway_threshold"]),
    )

    console.print("[bold]Scenario:[/bold] CFO wants to hire 3 engineers (+$60k/mo burn)")
    console.print("[bold]Current Runway:[/bold] 18 months")
    console.print("[bold]Proposed Runway:[/bold] 13.5 months")
    console.print("[bold]Risk:[/bold] Approaching 12-month threshold\n")

    # Judge
    judge = PureJudge(version="v0.2.0")
    ruling = judge.judge(request)

    # Display
    _display_summary(ruling)


@cli.command()
@click.argument("decision_file", type=click.Path(exists=True, path_type=Path))
def validate(decision_file: Path):
    """
    Validate decision JSON file format

    Checks that the decision file conforms to JudgeRequest schema without
    actually judging it.

    DECISION_FILE: Path to JSON file to validate
    """
    try:
        with open(decision_file) as f:
            decision_data = json.load(f)

        # Try to parse
        request = JudgeRequest(**decision_data)

        console.print(f"[bold green]✓[/bold green] Valid decision file: {decision_file}")
        console.print(f"\n[bold]Decision ID:[/bold] {request.decision_id}")
        console.print(f"[bold]Module:[/bold] {request.module}")
        console.print(f"[bold]Actor:[/bold] {request.actor.role.value} ({request.actor.org_unit})")
        console.print(f"[bold]Intent:[/bold] {request.intent_nl}")

    except json.JSONDecodeError as e:
        console.print(f"[bold red]✗[/bold red] Invalid JSON: {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Validation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
