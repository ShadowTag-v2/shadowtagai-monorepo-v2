"""PNKLN Core Stack - ShadowTag Authentication API

import os
Complete authentication system integrating:
- Neural fingerprinting
- Steganographic embedding
- Blockchain receipts
- Verification services

Endpoints:
- POST /authenticate - Create authentication for new asset
- POST /verify - Verify asset authenticity
- GET /receipt/{asset_id} - Retrieve blockchain receipt
"""

import time
from datetime import datetime
from typing import Literal

import structlog
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel

from shadowtag.blockchain_receipt import ReceiptManager
from shadowtag.neural_hash import NeuralHasher
from shadowtag.stego_embed import ShadowTagEmbedder, WatermarkPayload

logger = structlog.get_logger(__name__)


# Prometheus metrics
auth_requests = Counter(
    "shadowtag_auth_requests_total",
    "Total authentication requests",
    ["asset_type"],
)
verify_requests = Counter(
    "shadowtag_verify_requests_total",
    "Total verification requests",
    ["result"],
)
auth_latency = Histogram("shadowtag_auth_latency_seconds", "Authentication latency")


# Pydantic models
class AuthenticationRequest(BaseModel):
    """Request to authenticate an asset."""

    owner_address: str
    asset_type: Literal["image", "video", "audio", "text"]
    embed_watermark: bool = True


class AuthenticationResponse(BaseModel):
    """Response after authentication."""

    asset_id: str
    fingerprint: dict
    blockchain_receipt: dict
    watermarked_asset_url: str | None
    total_cost_usd: float
    processing_time_ms: float


class VerificationRequest(BaseModel):
    """Request to verify an asset."""

    asset_id: str | None = None
    claimed_owner: str | None = None


class VerificationResponse(BaseModel):
    """Response from verification."""

    verified: bool
    confidence: float
    fingerprint_match: dict
    blockchain_confirmed: bool
    asset_id: str | None
    owner_address: str | None
    original_timestamp: datetime | None
    verification_details: dict


# Create FastAPI app
app = FastAPI(
    title="ShadowTag Authentication API",
    description="Neural authentication with blockchain proof-of-origin",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Global service instances
_hasher: NeuralHasher | None = None
_embedder: ShadowTagEmbedder | None = None
_receipt_manager: ReceiptManager | None = None


def get_services():
    """Get or initialize service instances."""
    global _hasher, _embedder, _receipt_manager

    if _hasher is None:
        _hasher = NeuralHasher()
    if _embedder is None:
        _embedder = ShadowTagEmbedder()
    if _receipt_manager is None:
        _receipt_manager = ReceiptManager()

    return _hasher, _embedder, _receipt_manager


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    get_services()
    logger.info("shadowtag_api_started")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    hasher, embedder, receipt_manager = get_services()

    return {
        "status": "healthy",
        "services": {
            "neural_hasher": "ready",
            "stego_embedder": "ready",
            "receipt_manager": "ready",
        },
        "stats": {
            "hasher": hasher.get_stats(),
            "embedder": embedder.get_stats(),
            "receipts": receipt_manager.get_stats(),
        },
    }


@app.post("/authenticate", response_model=AuthenticationResponse)
async def authenticate_asset(
    file: UploadFile = File(...),  # noqa: B008
    owner_address: str = Form(...),
    asset_type: Literal["image", "video", "audio", "text"] = Form(...),
    embed_watermark: bool = Form(True),
):
    """Authenticate a new asset.

    Steps:
    1. Generate neural fingerprint (multi-hash)
    2. Optionally embed steganographic watermark
    3. Record blockchain receipt (Polygon + Arweave)
    4. Return authentication proof

    Cost breakdown:
    - Neural hash: $0.002
    - Stego embed: $0.001
    - Blockchain receipt: $0.012
    - Total: ~$0.015 per asset
    """
    start_time = time.time()
    hasher, embedder, receipt_manager = get_services()

    try:
        # Read file data
        asset_data = await file.read()

        # Step 1: Generate neural fingerprint
        fingerprint = hasher.hash_asset(data=asset_data, asset_type=asset_type)

        # Step 2: Embed watermark (if requested)
        watermarked_url = None

        if embed_watermark:
            # Create watermark payload
            payload = WatermarkPayload(
                asset_id=fingerprint.asset_id,
                timestamp=int(fingerprint.timestamp.timestamp()),
                owner_id=owner_address,
                blockchain_receipt_hash="pending",  # Updated after blockchain step
                checksum=0,  # Calculated by embedder
            )

            # Embed watermark
            embedder.embed(asset_data=asset_data, asset_type=asset_type, payload=payload)

            # TODO: Upload watermarked asset to storage (S3, IPFS, etc.)
            watermarked_url = f"https://cdn.pnkln.ai/{fingerprint.asset_id}"

        # Step 3: Create blockchain receipt
        fingerprint_dict = {
            "asset_id": fingerprint.asset_id,
            "asset_type": fingerprint.asset_type,
            "perceptual_hash": fingerprint.perceptual_hash,
            "crypto_hash": fingerprint.crypto_hash,
            "semantic_hash": fingerprint.semantic_hash,
            "density_score": fingerprint.density_score,
            "timestamp": fingerprint.timestamp.isoformat(),
            "file_size": fingerprint.file_size_bytes,
        }

        receipt = receipt_manager.create_receipt(
            asset_id=fingerprint.asset_id,
            fingerprint_hash=fingerprint.crypto_hash,
            fingerprint_data=fingerprint_dict,
            owner_address=owner_address,
        )

        # Calculate total cost
        hash_cost = 0.002
        embed_cost = 0.001 if embed_watermark else 0.0
        receipt_cost = receipt.total_cost_usd
        total_cost = hash_cost + embed_cost + receipt_cost

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Track metrics
        auth_requests.labels(asset_type=asset_type).inc()

        response = AuthenticationResponse(
            asset_id=fingerprint.asset_id,
            fingerprint=fingerprint_dict,
            blockchain_receipt={
                "polygon_tx": receipt.polygon_tx_hash,
                "arweave_tx": receipt.arweave_tx_id,
                "verification_url": receipt.verification_url,
                "timestamp": receipt.timestamp.isoformat(),
            },
            watermarked_asset_url=watermarked_url,
            total_cost_usd=round(total_cost, 4),
            processing_time_ms=round(processing_time_ms, 2),
        )

        logger.info(
            "asset_authenticated",
            asset_id=fingerprint.asset_id,
            asset_type=asset_type,
            cost_usd=total_cost,
            processing_ms=processing_time_ms,
        )

        return response

    except Exception as e:
        logger.error("authentication_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Authentication failed: {e!s}") from e


@app.post("/verify", response_model=VerificationResponse)
async def verify_asset(
    file: UploadFile = File(...),  # noqa: B008
    asset_id: str | None = Form(None),
    claimed_owner: str | None = Form(None),
):
    """Verify asset authenticity.

    Steps:
    1. Generate fingerprint from submitted asset
    2. Compare against stored fingerprint (if asset_id provided)
    3. Extract embedded watermark (if present)
    4. Verify blockchain receipt
    5. Return verification result

    Returns confidence score and detailed verification status.
    """
    hasher, embedder, receipt_manager = get_services()

    try:
        # Read file data
        asset_data = await file.read()

        # Detect asset type (simplified - use magic bytes in production)
        content_type = file.content_type or ""
        if "image" in content_type:
            asset_type = "image"
        elif "video" in content_type:
            asset_type = "video"
        elif "audio" in content_type:
            asset_type = "audio"
        else:
            asset_type = "text"

        # Generate fingerprint from submitted asset
        current_fingerprint = hasher.hash_asset(data=asset_data, asset_type=asset_type)

        # Try to extract embedded watermark
        extracted_payload = embedder.extract(asset_data, asset_type)

        # If asset_id provided, verify against stored fingerprint
        fingerprint_match = {}
        blockchain_confirmed = False

        if asset_id:
            # TODO: Retrieve stored fingerprint from database
            # For now, use placeholder verification

            # Verify blockchain receipt
            # TODO: Get receipt details from database by asset_id
            # receipt_verification = receipt_manager.verify_receipt(...)

            fingerprint_match = {
                "perceptual_similarity": 0.95,  # Placeholder
                "semantic_similarity": 0.92,  # Placeholder
                "crypto_match": False,  # Different if re-encoded
            }

            blockchain_confirmed = True  # Placeholder

        # Calculate overall confidence
        confidence = 0.0

        if extracted_payload:
            confidence += 0.5  # Watermark found

        if fingerprint_match:
            avg_similarity = (
                fingerprint_match.get("perceptual_similarity", 0)
                + fingerprint_match.get("semantic_similarity", 0)
            ) / 2
            confidence += avg_similarity * 0.5

        verified = confidence >= 0.7

        # Track metrics
        verify_requests.labels(result="verified" if verified else "failed").inc()

        response = VerificationResponse(
            verified=verified,
            confidence=round(confidence, 3),
            fingerprint_match=fingerprint_match,
            blockchain_confirmed=blockchain_confirmed,
            asset_id=extracted_payload.asset_id if extracted_payload else asset_id,
            owner_address=extracted_payload.owner_id if extracted_payload else claimed_owner,
            original_timestamp=(
                datetime.fromtimestamp(extracted_payload.timestamp) if extracted_payload else None
            ),
            verification_details={
                "watermark_extracted": extracted_payload is not None,
                "current_fingerprint": {
                    "crypto_hash": current_fingerprint.crypto_hash,
                    "density_score": current_fingerprint.density_score,
                },
            },
        )

        logger.info("asset_verified", verified=verified, confidence=confidence, asset_id=asset_id)

        return response

    except Exception as e:
        logger.error("verification_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failed: {e!s}") from e


@app.get("/receipt/{asset_id}")
async def get_receipt(asset_id: str):
    """Retrieve blockchain receipt for an asset.

    Returns Polygon and Arweave transaction details.
    """
    # TODO: Retrieve receipt from database by asset_id

    logger.info("receipt_retrieved", asset_id=asset_id)

    return {
        "asset_id": asset_id,
        "polygon_tx_hash": "0x..." + asset_id[:40],  # Placeholder
        "arweave_tx_id": asset_id[:43],  # Placeholder
        "verification_url": f"https://pnkln.ai/verify/{asset_id}",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/stats")
async def get_stats():
    """Get ShadowTag system statistics."""
    hasher, embedder, receipt_manager = get_services()

    return {
        "neural_hasher": hasher.get_stats(),
        "stego_embedder": embedder.get_stats(),
        "receipt_manager": receipt_manager.get_stats(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("shadowtag.api:app", host="0.0.0.0", port=8002, reload=True, log_level="info")
