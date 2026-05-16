# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Verify Command

Handles verification operations for steganographic data and receipt chains.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command("detect")
def detect(media_file: Path = typer.Argument(..., help="Media file to analyze")):
    """
    Detect if a media file contains hidden data
    """
    if not media_file.exists():
        console.print(f"[red]Error: File not found: {media_file}[/red]")
        raise typer.Exit(1)

    suffix = media_file.suffix.lower()

    if suffix in [".mp4", ".avi", ".mkv", ".mov"]:
        from ...video_stego import VideoDecoder

        decoder = VideoDecoder()
        result = decoder.detect_embedded_data(media_file)

        table = Table(title=f"Detection Results: {media_file.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Contains Hidden Data", "Yes" if result["has_embedded_data"] else "No")
        table.add_row("Confidence", f"{result['confidence']:.1%}")
        table.add_row("Suspected Method", str(result["suspected_method"]))
        table.add_row("Estimated Payload Size", f"{result['estimated_payload_size']} bytes")

        console.print(table)

    elif suffix in [".mp3", ".wav", ".flac", ".ogg"]:
        console.print("[yellow]Audio detection not yet implemented[/yellow]")

    else:
        console.print(f"[red]Unsupported media type: {suffix}[/red]")
        raise typer.Exit(1)


@app.command("integrity")
def verify_integrity(operation_id: str = typer.Argument(..., help="Operation ID to verify")):
    """
    Verify the integrity of a steganographic operation using receipt chain
    """
    from ...receipt_chain import ChainStorage

    storage = ChainStorage(Path.home() / ".shadowtag" / "chains.db")

    # Search for receipt
    receipts = storage.search_receipts(operation_id=operation_id)

    if not receipts:
        console.print(f"[red]No receipt found for operation: {operation_id}[/red]")
        raise typer.Exit(1)

    receipt_data = receipts[0]

    table = Table(title=f"Receipt: {operation_id}")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    for key, value in receipt_data.items():
        if key != "id":
            table.add_row(key, str(value))

    console.print(table)

    # Verify chain integrity
    chain = storage.load_chain(receipt_data["chain_id"])
    is_valid = chain.verify_chain()

    if is_valid:
        console.print("[green]✓ Chain integrity verified[/green]")
    else:
        console.print("[red]✗ Chain integrity check failed[/red]")

    storage.close()
