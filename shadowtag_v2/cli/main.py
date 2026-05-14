# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Main CLI Application

Entry point for ShadowTag v2 command-line interface.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .commands import encode, decode, verify, chain

# Create Typer app
app = typer.Typer(
    name="shadowtag",
    help="ShadowTag v2 - Advanced Steganography Toolkit",
    add_completion=False,
)

# Create console for rich output
console = Console()

# Add subcommands
app.add_typer(encode.app, name="encode", help="Encode data into media files")
app.add_typer(decode.app, name="decode", help="Decode data from media files")
app.add_typer(verify.app, name="verify", help="Verify steganographic operations")
app.add_typer(chain.app, name="chain", help="Manage receipt chains")


@app.command()
def version():
    """Display ShadowTag version information"""
    from .. import video_stego, audio_stego, receipt_chain

    table = Table(title="ShadowTag v2 Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")

    table.add_row("CLI", "2.0.0")
    table.add_row("Video Stego", video_stego.__version__)
    table.add_row("Audio Stego", audio_stego.__version__)
    table.add_row("Receipt Chain", receipt_chain.__version__)

    console.print(table)


@app.command()
def info(media_file: Path = typer.Argument(..., help="Media file to analyze")):
    """
    Display information about a media file's steganographic capacity
    """
    if not media_file.exists():
        console.print(f"[red]Error: File not found: {media_file}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Analyzing: {media_file}[/cyan]")

    # Determine media type
    suffix = media_file.suffix.lower()

    if suffix in [".mp4", ".avi", ".mkv", ".mov"]:
        from ..video_stego import VideoEncoder, EncoderConfig

        encoder = VideoEncoder(EncoderConfig())
        capacity = encoder.estimate_capacity(media_file)

        table = Table(title=f"Video Capacity: {media_file.name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Capacity", f"{capacity['total_bytes']:,} bytes")
        table.add_row("Usable Capacity", f"{capacity['usable_bytes']:,} bytes")
        table.add_row("Recommended Max", f"{capacity['recommended_max_bytes']:,} bytes")

        console.print(table)

    elif suffix in [".mp3", ".wav", ".flac", ".ogg"]:
        console.print("[yellow]Audio capacity estimation not yet implemented[/yellow]")

    else:
        console.print(f"[red]Unsupported media type: {suffix}[/red]")
        raise typer.Exit(1)


def cli():
    """Main CLI entry point"""
    app()


if __name__ == "__main__":
    cli()
