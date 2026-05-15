"""Video Steganography Endpoints

API endpoints for video encoding and decoding operations.
"""

import hashlib
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from shadowtag_v2.receipt_chain import ChainStorage, Receipt, ReceiptChain
from shadowtag_v2.video_stego import DecoderConfig, EncoderConfig, VideoDecoder, VideoEncoder

from app.api.schemas.video import CapacityResponse, DecodeResponse, EncodeResponse
from app.core.config import settings

router = APIRouter()


@router.post("/encode", response_model=EncodeResponse)
async def encode_video(
    video: UploadFile = File(..., description="Input video file"),  # noqa: B008
    payload: UploadFile = File(..., description="Data to hide"),  # noqa: B008
    bits_per_channel: int = Form(default=2, ge=1, le=4),
    use_encryption: bool = Form(default=True),
    error_correction: bool = Form(default=True),
    create_receipt: bool = Form(default=True),
):
    """Encode (embed) data into a video file.

    Args:
        video: Input video file
        payload: File containing data to hide
        bits_per_channel: Number of LSBs to use (1-4)
        use_encryption: Enable payload encryption
        error_correction: Enable error correction
        create_receipt: Create receipt chain entry

    Returns:
        Encoding statistics and verification hash

    """
    # Validate video file
    if not any(video.filename.endswith(ext) for ext in settings.ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video format. Allowed: {settings.ALLOWED_VIDEO_EXTENSIONS}",
        )

    # Save uploaded files
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    video_path = upload_dir / f"input_{datetime.utcnow().timestamp()}_{video.filename}"
    payload_path = upload_dir / f"payload_{datetime.utcnow().timestamp()}"

    with open(video_path, "wb") as f:
        f.write(await video.read())

    payload_data = await payload.read()
    with open(payload_path, "wb") as f:
        f.write(payload_data)

    # Configure encoder
    config = EncoderConfig(
        bits_per_channel=bits_per_channel,
        use_encryption=use_encryption,
        error_correction=error_correction,
    )

    encoder = VideoEncoder(config)

    # Encode
    output_dir = Path(settings.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"encoded_{datetime.utcnow().timestamp()}_{video.filename}"

    try:
        stats = encoder.encode(
            video_path=video_path,
            payload=payload_data,
            output_path=output_path,
        )

        # Create receipt if requested
        receipt_id = None
        if create_receipt:
            receipt_id = _create_video_receipt("encode", video_path, payload_data, stats, config)

        return EncodeResponse(
            success=True,
            output_file=str(output_path),
            verification_hash=stats["verification_hash"],
            stats=stats,
            receipt_id=receipt_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/decode", response_model=DecodeResponse)
async def decode_video(
    video: UploadFile = File(..., description="Video file with hidden data"),  # noqa: B008
    verify_hash: str | None = Form(default=None),
    create_receipt: bool = Form(default=True),
):
    """Decode (extract) data from a video file.

    Args:
        video: Video file with embedded data
        verify_hash: Optional hash for integrity verification
        create_receipt: Create receipt chain entry

    Returns:
        Extracted payload and statistics

    """
    # Save uploaded file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    video_path = upload_dir / f"decode_{datetime.utcnow().timestamp()}_{video.filename}"

    with open(video_path, "wb") as f:
        f.write(await video.read())

    # Configure decoder
    config = DecoderConfig(verify_integrity=verify_hash is not None)
    decoder = VideoDecoder(config)

    try:
        payload, stats = decoder.decode(
            video_path=video_path,
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
            receipt_id = _create_video_receipt("decode", video_path, payload, stats, None)

        return DecodeResponse(
            success=True,
            payload_file=str(output_path),
            payload_size=len(payload),
            stats=stats,
            receipt_id=receipt_id,
            integrity_verified=verify_hash is not None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/capacity", response_model=CapacityResponse)
async def estimate_capacity(video: UploadFile = File(..., description="Video file to analyze")):  # noqa: B008
    """Estimate the embedding capacity of a video file.

    Args:
        video: Video file to analyze

    Returns:
        Capacity estimates

    """
    # Save uploaded file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    video_path = upload_dir / f"capacity_{datetime.utcnow().timestamp()}_{video.filename}"

    with open(video_path, "wb") as f:
        f.write(await video.read())

    # Estimate capacity
    encoder = VideoEncoder()
    capacity = encoder.estimate_capacity(video_path)

    return CapacityResponse(**capacity)


def _create_video_receipt(
    operation_type: str,
    video_path: Path,
    payload: bytes,
    stats: dict,
    config: EncoderConfig | None,
) -> str:
    """Create a receipt for a video operation"""
    payload_hash = hashlib.sha256(payload).hexdigest()
    media_hash = hashlib.sha256(video_path.read_bytes()).hexdigest()

    receipt = Receipt(
        operation_id=hashlib.sha256(
            f"{datetime.utcnow().isoformat()}_{media_hash}".encode(),
        ).hexdigest()[:16],
        operation_type=operation_type,
        timestamp=datetime.utcnow().isoformat(),
        media_type="video",
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
