"""
Audio Steganography Endpoints

API endpoints for audio encoding and decoding operations.
"""

import hashlib
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from shadowtag_v2.audio_stego import (
    AudioDecoder,
    AudioDecoderConfig,
    AudioEncoder,
    AudioEncoderConfig,
)
from shadowtag_v2.receipt_chain import ChainStorage, Receipt, ReceiptChain

from app.api.schemas.audio import DecodeResponse, EncodeResponse
from app.core.config import settings

router = APIRouter()


@router.post("/encode", response_model=EncodeResponse)
async def encode_audio(
    audio: UploadFile = File(..., description="Input audio file"),
    payload: UploadFile = File(..., description="Data to hide"),
    method: str = Form(default="lsb", regex="^(lsb|phase|echo|spread_spectrum)$"),
    bits_per_sample: int = Form(default=1, ge=1, le=4),
    use_encryption: bool = Form(default=True),
    create_receipt: bool = Form(default=True),
):
    """
    Encode (embed) data into an audio file.

    Args:
        audio: Input audio file
        payload: File containing data to hide
        method: Encoding method (lsb, phase, echo, spread_spectrum)
        bits_per_sample: Number of LSBs to use
        use_encryption: Enable payload encryption
        create_receipt: Create receipt chain entry

    Returns:
        Encoding statistics
    """
    # Validate audio file
    if not any(audio.filename.endswith(ext) for ext in settings.ALLOWED_AUDIO_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Allowed: {settings.ALLOWED_AUDIO_EXTENSIONS}",
        )

    # Save uploaded files
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    audio_path = upload_dir / f"input_{datetime.utcnow().timestamp()}_{audio.filename}"
    payload_data = await payload.read()

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Configure encoder
    config = AudioEncoderConfig(
        method=method,
        bits_per_sample=bits_per_sample,
        use_encryption=use_encryption,
    )

    encoder = AudioEncoder(config)

    # Encode
    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"encoded_{datetime.utcnow().timestamp()}_{audio.filename}"

    try:
        stats = encoder.encode(
            audio_path=audio_path,
            payload=payload_data,
            output_path=output_path,
        )

        # Create receipt if requested
        receipt_id = None
        if create_receipt:
            receipt_id = _create_audio_receipt("encode", audio_path, payload_data, stats, config)

        return EncodeResponse(
            success=True, output_file=str(output_path), stats=stats, receipt_id=receipt_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decode", response_model=DecodeResponse)
async def decode_audio(
    audio: UploadFile = File(..., description="Audio file with hidden data"),
    verify_hash: str | None = Form(default=None),
    create_receipt: bool = Form(default=True),
):
    """
    Decode (extract) data from an audio file.

    Args:
        audio: Audio file with embedded data
        verify_hash: Optional hash for integrity verification
        create_receipt: Create receipt chain entry

    Returns:
        Extracted payload and statistics
    """
    # Save uploaded file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    audio_path = upload_dir / f"decode_{datetime.utcnow().timestamp()}_{audio.filename}"

    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Configure decoder
    config = AudioDecoderConfig(verify_integrity=verify_hash is not None)
    decoder = AudioDecoder(config)

    try:
        payload, stats = decoder.decode(
            audio_path=audio_path,
            expected_hash=verify_hash,
        )

        # Save extracted payload
        output_dir = Path(settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"extracted_{datetime.utcnow().timestamp()}.bin"

        with open(output_path, "wb") as f:
            f.write(payload)

        # Create receipt if requested
        receipt_id = None
        if create_receipt:
            receipt_id = _create_audio_receipt("decode", audio_path, payload, stats, None)

        return DecodeResponse(
            success=True,
            payload_file=str(output_path),
            payload_size=len(payload),
            stats=stats,
            receipt_id=receipt_id,
            integrity_verified=verify_hash is not None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _create_audio_receipt(
    operation_type: str,
    audio_path: Path,
    payload: bytes,
    stats: dict,
    config: AudioEncoderConfig | None,
) -> str:
    """Create a receipt for an audio operation"""
    payload_hash = hashlib.sha256(payload).hexdigest()
    media_hash = hashlib.sha256(audio_path.read_bytes()).hexdigest()

    receipt = Receipt(
        operation_id=hashlib.sha256(
            f"{datetime.utcnow().isoformat()}_{media_hash}".encode()
        ).hexdigest()[:16],
        operation_type=operation_type,
        timestamp=datetime.utcnow().isoformat(),
        media_type="audio",
        method=stats.get("method", "lsb"),
        payload_hash=payload_hash,
        media_hash=media_hash,
        metadata=stats,
    )

    storage = ChainStorage(Path(settings.CHAIN_DB_PATH))
    chains = storage.list_chains()

    chain = storage.load_chain(chains[0]["chain_id"]) if chains else ReceiptChain()

    chain.add_receipt(receipt)
    storage.save_chain(chain)
    storage.close()

    return receipt.operation_id
