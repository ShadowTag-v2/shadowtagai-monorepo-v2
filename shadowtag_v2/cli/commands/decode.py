# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Decode Command

Handles decoding (extraction) operations for various media types.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress

app = typer.Typer()
console = Console()


@app.command("video")
def decode_video(
    input_video: Path = typer.Argument(..., help="Video file with hidden data"),
    output_file: Path = typer.Argument(..., help="Output file for extracted data"),
    verify_hash: str | None = typer.Option(None, "--verify", "-v", help="Expected hash for verification"),
    create_receipt: bool = typer.Option(True, "--receipt/--no-receipt", help="Create receipt chain entry"),
):
    """
    Decode (extract) data from a video file
    """
    if not input_video.exists():
        console.print(f"[red]Error: Input video not found: {input_video}[/red]")
        raise typer.Exit(1)

    from ...video_stego import VideoDecoder, DecoderConfig

    config = DecoderConfig(verify_integrity=verify_hash is not None)
    decoder = VideoDecoder(config)

    with Progress() as progress:
        task = progress.add_task("[cyan]Decoding...", total=100)

        try:
            payload, stats = decoder.decode(
                video_path=input_video,
                expected_hash=verify_hash,
            )

            progress.update(task, completed=100)

            # Save extracted payload
            output_file.write_bytes(payload)

            console.print("[green]✓ Decoding successful![/green]")
            console.print(f"Extracted {len(payload)} bytes to: {output_file}")

            if verify_hash:
                console.print("[green]✓ Integrity verified[/green]")

            if create_receipt:
                _create_decode_receipt("video", input_video, payload, stats)

        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@app.command("audio")
def decode_audio(
    input_audio: Path = typer.Argument(..., help="Audio file with hidden data"),
    output_file: Path = typer.Argument(..., help="Output file for extracted data"),
    verify_hash: str | None = typer.Option(None, "--verify", "-v", help="Expected hash for verification"),
    create_receipt: bool = typer.Option(True, "--receipt/--no-receipt", help="Create receipt chain entry"),
):
    """
    Decode (extract) data from an audio file
    """
    if not input_audio.exists():
        console.print(f"[red]Error: Input audio not found: {input_audio}[/red]")
        raise typer.Exit(1)

    from ...audio_stego import AudioDecoder, AudioDecoderConfig

    config = AudioDecoderConfig(verify_integrity=verify_hash is not None)
    decoder = AudioDecoder(config)

    with Progress() as progress:
        task = progress.add_task("[cyan]Decoding...", total=100)

        try:
            payload, stats = decoder.decode(
                audio_path=input_audio,
                expected_hash=verify_hash,
            )

            progress.update(task, completed=100)

            # Save extracted payload
            output_file.write_bytes(payload)

            console.print("[green]✓ Decoding successful![/green]")
            console.print(f"Extracted {len(payload)} bytes to: {output_file}")

            if verify_hash:
                console.print("[green]✓ Integrity verified[/green]")

            if create_receipt:
                _create_decode_receipt("audio", input_audio, payload, stats)

        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


def _create_decode_receipt(media_type: str, input_file: Path, payload: bytes, stats: dict):
    """Create a receipt for a decoding operation"""
    import hashlib
    from datetime import datetime, timezone
    from ...receipt_chain import ReceiptChain, Receipt, ChainStorage

    payload_hash = hashlib.sha256(payload).hexdigest()
    media_hash = hashlib.sha256(input_file.read_bytes()).hexdigest()

    receipt = Receipt(
        operation_id=hashlib.sha256(f"{datetime.now(timezone.utc).isoformat()}_{media_hash}".encode()).hexdigest()[:16],
        operation_type="decode",
        timestamp=datetime.now(timezone.utc).isoformat(),
        media_type=media_type,
        method=stats.get("method", "unknown"),
        payload_hash=payload_hash,
        media_hash=media_hash,
        metadata=stats,
    )

    storage = ChainStorage(Path.home() / ".shadowtag" / "chains.db")
    chains = storage.list_chains()

    if chains:
        chain = storage.load_chain(chains[0]["chain_id"])
    else:
        chain = ReceiptChain()

    chain.add_receipt(receipt)
    storage.save_chain(chain)
    storage.close()

    console.print(f"[green]✓ Receipt created: {receipt.operation_id}[/green]")
