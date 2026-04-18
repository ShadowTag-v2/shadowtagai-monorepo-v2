import os

import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(name="finjudge", help="FinJudge: Supreme Court for Financial Risk.")
console = Console()

# Configuration
API_URL = os.getenv("FINJUDGE_API_URL", "http://localhost:8080")
CONFIG_FILE = os.path.expanduser("~/.finjudge_config")


def save_key(api_key: str):
    with open(CONFIG_FILE, "w") as f:
        f.write(api_key)
    console.print(f"[green]API Key saved to {CONFIG_FILE}[/green]")


def load_key() -> str | None:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return f.read().strip()
    return None


@app.command()
def login(api_key: str):
    """Save your FinJudge API key."""
    save_key(api_key)


@app.command()
def eval(intent: str, risk_score: float = 0.5, user: str = "cli_user"):
    """Evaluate a financial intent."""
    api_key = load_key()
    headers = {"x-api-key": api_key} if api_key else {}

    with console.status("[bold green]Consulting the Supreme Court...[/bold green]"):
        try:
            payload = {
                "request_id": "cli_req",
                "intent_nl": intent,
                "metrics": {"risk_score": risk_score},
                "context": {"user": user},
            }
            response = requests.post(f"{API_URL}/v1/judge", json=payload, headers=headers)
            response.raise_for_status()
            ruling = response.json()

            # Display Output
            risk_color = "green" if ruling["risk_level"] == "LOW" else "red"

            console.print(
                Panel(
                    f"[bold]Ruling ID:[/bold] {ruling['ruling_id']}\n"
                    f"[bold]Risk Level:[/bold] [{risk_color}]{ruling['risk_level']}[/{risk_color}]\n"
                    f"[bold]Confidence:[/bold] {ruling['confidence']:.0%}\n\n"
                    f"[italic]{ruling['decision_memo']}[/italic]",
                    title="FinJudge Ruling",
                    border_style=risk_color,
                ),
            )

            if ruling["controls_required"]:
                table = Table(title="Required Controls")
                table.add_column("Control")
                for c in ruling["controls_required"]:
                    table.add_row(c)
                console.print(table)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


@app.command()
def upgrade(email: str):
    """Get a link to upgrade to Pro."""
    api_key = load_key()
    if not api_key:
        console.print("[red]Please login first.[/red]")
        return

    try:
        headers = {"x-api-key": api_key}
        response = requests.post(
            f"{API_URL}/v1/subscribe",
            params={"email": email},
            headers=headers,
        )
        response.raise_for_status()
        url = response.json()["checkout_url"]
        console.print(f"Upgrade Link: [link={url}]{url}[/link]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    app()
