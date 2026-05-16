# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Chain Command

Manages receipt chains for audit trails and verification.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command("list")
def list_chains():
    """
    List all receipt chains
    """
    from ...receipt_chain import ChainStorage

    storage = ChainStorage(Path.home() / ".shadowtag" / "chains.db")
    chains = storage.list_chains()

    if not chains:
        console.print("[yellow]No chains found[/yellow]")
        return

    table = Table(title="Receipt Chains")
    table.add_column("Chain ID", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Updated", style="green")
    table.add_column("Blocks", style="magenta")
    table.add_column("Valid", style="yellow")

    for chain in chains:
        table.add_row(
            chain["chain_id"],
            chain["created_at"][:19],
            chain["updated_at"][:19],
            str(chain["block_count"]),
            "✓" if chain["is_valid"] else "✗",
        )

    console.print(table)
    storage.close()


@app.command("show")
def show_chain(chain_id: str = typer.Argument(..., help="Chain ID to display")):
    """
    Display detailed information about a chain
    """
    from ...receipt_chain import ChainStorage

    storage = ChainStorage(Path.home() / ".shadowtag" / "chains.db")
    chain = storage.load_chain(chain_id)

    if not chain:
        console.print(f"[red]Chain not found: {chain_id}[/red]")
        raise typer.Exit(1)

    summary = chain.get_chain_summary()

    # Print summary
    table = Table(title=f"Chain Summary: {chain_id}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in summary.items():
        if key not in ["operation_types", "media_types"]:
            table.add_row(key, str(value))

    console.print(table)

    # Print operation types
    if summary.get("operation_types"):
        console.print("\n[cyan]Operation Types:[/cyan]")
        for op_type, count in summary["operation_types"].items():
            console.print(f"  {op_type}: {count}")

    # Print media types
    if summary.get("media_types"):
        console.print("\n[cyan]Media Types:[/cyan]")
        for media_type, count in summary["media_types"].items():
            console.print(f"  {media_type}: {count}")

    storage.close()


@app.command("export")
def export_chain(
    chain_id: str = typer.Argument(..., help="Chain ID to export"),
    output_file: Path = typer.Argument(..., help="Output JSON file"),
):
    """
    Export a chain to JSON file
    """
    from ...receipt_chain import ChainStorage

    storage = ChainStorage(Path.home() / ".shadowtag" / "chains.db")

    if storage.export_chain_to_file(chain_id, output_file):
        console.print(f"[green]✓ Chain exported to: {output_file}[/green]")
    else:
        console.print(f"[red]Chain not found: {chain_id}[/red]")
        raise typer.Exit(1)

    storage.close()


@app.command("import")
def import_chain(input_file: Path = typer.Argument(..., help="JSON file to import")):
    """
    Import a chain from JSON file
    """
    if not input_file.exists():
        console.print(f"[red]File not found: {input_file}[/red]")
        raise typer.Exit(1)

    from ...receipt_chain import ChainStorage

    storage = ChainStorage(Path.home() / ".shadowtag" / "chains.db")

    try:
        chain_id = storage.import_chain_from_file(input_file)
        console.print(f"[green]✓ Chain imported: {chain_id}[/green]")
    except ValueError as e:
        console.print(f"[red]Import failed: {e}[/red]")
        raise typer.Exit(1)

    storage.close()


@app.command("verify")
def verify_chain(chain_id: str = typer.Argument(..., help="Chain ID to verify")):
    """
    Verify the cryptographic integrity of a chain
    """
    from ...receipt_chain import ChainStorage, ChainVerifier

    storage = ChainStorage(Path.home() / ".shadowtag" / "chains.db")
    chain = storage.load_chain(chain_id)

    if not chain:
        console.print(f"[red]Chain not found: {chain_id}[/red]")
        raise typer.Exit(1)

    verifier = ChainVerifier()
    result = verifier.verify_chain(chain)

    if result.is_valid:
        console.print(f"[green]✓ Chain {chain_id} is valid[/green]")
    else:
        console.print(f"[red]✗ Chain {chain_id} is invalid[/red]")

    if result.errors:
        console.print("\n[red]Errors:[/red]")
        for error in result.errors:
            console.print(f"  • {error}")

    if result.warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            console.print(f"  • {warning}")

    # Print details
    if result.details:
        console.print("\n[cyan]Details:[/cyan]")
        for key, value in result.details.items():
            console.print(f"  {key}: {value}")

    storage.close()
