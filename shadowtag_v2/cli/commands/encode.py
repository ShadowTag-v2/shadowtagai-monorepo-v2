# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Encode Command

Handles encoding (embedding) operations for various media types.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

app = typer.Typer()
console = Console()


@app.command("video")
def encode_video(
    input_video: Path = typer.Argument(..., help="Input video file"),
    payload_file: Path = typer.Argument(..., help="File containing data to hide"),
    output_video: Path = typer.Argument(..., help="Output video file"),
    bits_per_channel: int = typer.Option(2, "--bits", "-b", help="LSBs per channel (1-4)"),
    encrypt: bool = typer.Option(True, "--encrypt/--no-encrypt", help="Encrypt payload"),
    error_correction: bool = typer.Option(True, "--error-correction/--no-error-correction", help="Enable error correction"),
    create_receipt: bool = typer.Option(True, "--receipt/--no-receipt", help="Create receipt chain entry"),
):
    """
    Encode data into a video file
    """
    # Validate inputs
    if not input_video.exists():
        console.print(f"[red]Error: Input video not found: {input_video}[/red]")
        raise typer.Exit(1)

    if not payload_file.exists():
        console.print(f"[red]Error: Payload file not found: {payload_file}[/red]")
        raise typer.Exit(1)

    # Load payload
    payload = payload_file.read_bytes()
    console.print(f"[cyan]Payload size: {len(payload)} bytes[/cyan]")

    # Import and configure encoder
    from ...video_stego import VideoEncoder, EncoderConfig

    config = EncoderConfig(
        bits_per_channel=bits_per_channel,
        use_encryption=encrypt,
        error_correction=error_correction,
    )

    encoder = VideoEncoder(config)

    # Encode with progress
    with Progress() as progress:
        task = progress.add_task("[cyan]Encoding...", total=100)

        try:
            stats = encoder.encode(
                video_path=input_video,
                payload=payload,
                output_path=output_video,
            )

            progress.update(task, completed=100)

            console.print("[green]✓ Encoding successful![/green]")
            console.print(f"Output: {output_video}")
            console.print(f"Verification hash: {stats['verification_hash']}")

            # Create receipt if requested
            if create_receipt:
                _create_encode_receipt("video", input_video, payload, stats, config)

        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


@app.command("audio")
def encode_audio(
    input_audio: Path = typer.Argument(..., help="Input audio file"),
    payload_file: Path = typer.Argument(..., help="File containing data to hide"),
    output_audio: Path = typer.Argument(..., help="Output audio file"),
    method: str = typer.Option("lsb", "--method", "-m", help="Encoding method"),
    bits_per_sample: int = typer.Option(1, "--bits", "-b", help="LSBs per sample"),
    encrypt: bool = typer.Option(True, "--encrypt/--no-encrypt", help="Encrypt payload"),
    create_receipt: bool = typer.Option(True, "--receipt/--no-receipt", help="Create receipt chain entry"),
):
    """
    Encode data into an audio file
    """
    # Validate inputs
    if not input_audio.exists():
        console.print(f"[red]Error: Input audio not found: {input_audio}[/red]")
        raise typer.Exit(1)

    if not payload_file.exists():
        console.print(f"[red]Error: Payload file not found: {payload_file}[/red]")
        raise typer.Exit(1)

    # Load payload
    payload = payload_file.read_bytes()
    console.print(f"[cyan]Payload size: {len(payload)} bytes[/cyan]")

    # Import and configure encoder
    from ...audio_stego import AudioEncoder, AudioEncoderConfig

    config = AudioEncoderConfig(
        method=method,
        bits_per_sample=bits_per_sample,
        use_encryption=encrypt,
    )

    encoder = AudioEncoder(config)

    # Encode
    with Progress() as progress:
        task = progress.add_task("[cyan]Encoding...", total=100)

        try:
            stats = encoder.encode(
                audio_path=input_audio,
                payload=payload,
                output_path=output_audio,
            )

            progress.update(task, completed=100)

            console.print("[green]✓ Encoding successful![/green]")
            console.print(f"Output: {output_audio}")
            console.print(f"SNR: {stats['snr_db']:.2f} dB")

            if create_receipt:
                _create_encode_receipt("audio", input_audio, payload, stats, config)

        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)


def _create_encode_receipt(media_type: str, input_file: Path, payload: bytes, stats: dict, config: object):
    """Create a receipt for an encoding operation"""
    import hashlib
    from datetime import datetime, timezone
    from ...receipt_chain import ReceiptChain, Receipt, ChainStorage

    # Calculate hashes
    payload_hash = hashlib.sha256(payload).hexdigest()
    media_hash = hashlib.sha256(input_file.read_bytes()).hexdigest()

    # Create receipt
    receipt = Receipt(
        operation_id=hashlib.sha256(f"{datetime.now(timezone.utc).isoformat()}_{media_hash}".encode()).hexdigest()[:16],
        operation_type="encode",
        timestamp=datetime.now(timezone.utc).isoformat(),
        media_type=media_type,
        method=stats.get("method", "lsb"),
        payload_hash=payload_hash,
        media_hash=media_hash,
        metadata=stats,
    )

    # Load or create chain
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
