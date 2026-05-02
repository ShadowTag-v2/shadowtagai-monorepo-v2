"""PNKLN Core Stack - ShadowTag-v4 Platform API

import os
AI-curated social video platform with:
- AI-presumed feed ranking (not engagement-based)
- ShadowTag integration for verified content
- Judge 6 validation before publication
- Energy-based content scoring

Endpoints:
- GET /feed - Get personalized AI-ranked feed
- POST /upload - Upload and publish content
- GET /item/{item_id} - Get single content item
- POST /verify/{item_id} - Verify content authenticity
"""

from datetime import datetime
from typing import Literal

import structlog
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel
from shadowtag_v4.ranking_engine import ContentItem, FeedRankingEngine

from ingestion.classification.tier_classifier import IngestedItem, TierClassifier
from shadowtag.blockchain_receipt import ReceiptManager
from shadowtag.neural_hash import NeuralHasher
from validation.judge6 import Judge6Validator, ValidationStatus

logger = structlog.get_logger(__name__)


# Prometheus metrics
feed_requests = Counter("ShadowTag-v2_feed_requests_total", "Total feed requests")
upload_requests = Counter("ShadowTag-v2_upload_requests_total", "Total upload requests", ["status"])
feed_latency = Histogram("ShadowTag-v2_feed_latency_seconds", "Feed generation latency")


# Pydantic models
class ContentMetadata(BaseModel):
    """Metadata for content item."""

    title: str
    description: str | None = None
    tags: list[str] = []
    category: str | None = None


class FeedRequest(BaseModel):
    """Request for personalized feed."""

    max_items: int = 50
    diversity_factor: float = 0.8
    include_tiers: list[int] = [1, 2, 3]
    verified_only: bool = False


class FeedResponse(BaseModel):
    """Response containing feed items."""

    items: list[dict]
    total: int
    avg_rank: float
    generation_time_ms: float


class UploadRequest(BaseModel):
    """Request to upload content."""

    content_type: Literal["image", "video", "audio"]
    metadata: ContentMetadata
    owner_address: str
    auto_verify: bool = True


class UploadResponse(BaseModel):
    """Response after content upload."""

    item_id: str
    validation_status: str
    shadow_tag_receipt: dict | None
    ai_rank: float | None
    published: bool
    processing_time_ms: float


# Create FastAPI app
app = FastAPI(
    title="ShadowTag-v4 Platform API",
    description="AI-curated social platform with verified content",
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
_ranking_engine: FeedRankingEngine | None = None
_classifier: TierClassifier | None = None
_validator: Judge6Validator | None = None
_hasher: NeuralHasher | None = None
_receipt_manager: ReceiptManager | None = None

# In-memory content store (replace with database in production)
_content_store: dict[str, ContentItem] = {}


def get_services():
    """Get or initialize service instances."""
    global _ranking_engine, _classifier, _validator, _hasher, _receipt_manager

    if _ranking_engine is None:
        _ranking_engine = FeedRankingEngine()
    if _classifier is None:
        _classifier = TierClassifier()
    if _validator is None:
        _validator = Judge6Validator()
    if _hasher is None:
        _hasher = NeuralHasher()
    if _receipt_manager is None:
        _receipt_manager = ReceiptManager()

    return _ranking_engine, _classifier, _validator, _hasher, _receipt_manager


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    get_services()
    logger.info("ShadowTag-v2_api_started")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    ranker, classifier, validator, hasher, receipts = get_services()

    return {
        "status": "healthy",
        "services": {
            "ranking_engine": "ready",
            "classifier": "ready",
            "validator": "ready",
            "shadow_tag": "ready",
        },
        "content_count": len(_content_store),
        "stats": {
            "ranker": ranker.get_stats(),
            "classifier": classifier.get_stats(),
            "validator": validator.get_stats(),
        },
    }


@app.post("/feed", response_model=FeedResponse)
async def get_feed(request: FeedRequest):
    """Get AI-ranked personalized feed.

    Returns content ranked by:
    - Energy-based neural models
    - Latent density scores
    - Novelty/uniqueness
    - NOT by engagement (likes, views, followers)
    """
    import time

    start_time = time.time()

    ranker, _, _, _, _ = get_services()

    # Get candidate items from content store
    candidates = list(_content_store.values())

    # Filter by tier if requested
    if request.include_tiers:
        candidates = [item for item in candidates if item.tier_score.tier in request.include_tiers]

    # Filter verified-only if requested
    if request.verified_only:
        candidates = [item for item in candidates if item.verified]

    # Generate feed
    feed_items = ranker.generate_feed(
        candidate_items=candidates,
        max_items=request.max_items,
        diversity_factor=request.diversity_factor,
    )

    # Convert to response format
    items_data = [
        {
            "item_id": item.item_id,
            "title": item.source_item.title,
            "content_preview": (item.source_item.content[:200] if item.source_item.content else ""),
            "source": item.source_item.source,
            "author": item.source_item.author,
            "published_at": item.published_at.isoformat(),
            "ai_rank": item.ai_presumed_rank,
            "energy_score": item.energy_score,
            "density_score": item.density_score,
            "novelty_score": item.novelty_score,
            "tier": item.tier_score.tier,
            "verified": item.verified,
            "url": item.source_item.url,
        }
        for item in feed_items
    ]

    avg_rank = (
        sum(item.ai_presumed_rank for item in feed_items) / len(feed_items) if feed_items else 0.0
    )

    generation_time_ms = (time.time() - start_time) * 1000

    # Track metrics
    feed_requests.inc()

    response = FeedResponse(
        items=items_data,
        total=len(feed_items),
        avg_rank=round(avg_rank, 4),
        generation_time_ms=round(generation_time_ms, 2),
    )

    logger.info(
        "feed_generated",
        item_count=len(feed_items),
        avg_rank=avg_rank,
        latency_ms=generation_time_ms,
    )

    return response


@app.post("/upload", response_model=UploadResponse)
async def upload_content(
    file: UploadFile = File(...),  # noqa: B008
    content_type: Literal["image", "video", "audio"] = Form(...),
    title: str = Form(...),
    description: str | None = Form(None),
    owner_address: str = Form(...),
    auto_verify: bool = Form(True),
):
    """Upload and publish content to ShadowTag-v4.

    Pipeline:
    1. Classify content (Tier 1/2/3)
    2. Validate with Judge 6
    3. Authenticate with ShadowTag (if auto_verify)
    4. Rank with AI engine
    5. Publish to feed
    """
    import time

    start_time = time.time()

    ranker, classifier, validator, hasher, receipt_manager = get_services()

    try:
        # Read file data
        content_data = await file.read()

        # Step 1: Create IngestedItem
        ingested_item = IngestedItem(
            id=f"ShadowTag-v2_{hash(content_data)}",
            source="ShadowTag-v2_upload",
            title=title,
            content=description,
            url=f"https://shadowtag_v4.com/content/{hash(content_data)}",
            published_at=datetime.utcnow(),
            author=owner_address,
            metadata={"content_type": content_type, "file_size": len(content_data)},
        )

        # Step 2: Classify into tier
        tier_score = await classifier.classify(ingested_item)

        # Step 3: Validate with Judge 6
        validation_result = await validator.validate(ingested_item, tier_score)

        # Check if validation passed
        if validation_result.status == ValidationStatus.BLOCKED:
            upload_requests.labels(status="blocked").inc()

            return UploadResponse(
                item_id=ingested_item.id,
                validation_status=validation_result.status.value,
                shadow_tag_receipt=None,
                ai_rank=None,
                published=False,
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
            )

        # Step 4: ShadowTag authentication (if auto_verify and passed validation)
        shadow_tag_receipt = None
        fingerprint = None

        if auto_verify and validation_result.status == ValidationStatus.PASSED:
            # Generate neural fingerprint
            fingerprint = hasher.hash_asset(data=content_data, asset_type=content_type)

            # Create blockchain receipt
            receipt = receipt_manager.create_receipt(
                asset_id=fingerprint.asset_id,
                fingerprint_hash=fingerprint.crypto_hash,
                fingerprint_data={
                    "asset_id": fingerprint.asset_id,
                    "crypto_hash": fingerprint.crypto_hash,
                    "density_score": fingerprint.density_score,
                },
                owner_address=owner_address,
            )

            shadow_tag_receipt = {
                "polygon_tx": receipt.polygon_tx_hash,
                "arweave_tx": receipt.arweave_tx_id,
                "verification_url": receipt.verification_url,
            }

        # Step 5: Create ContentItem and rank
        content_item = ContentItem(
            item_id=ingested_item.id,
            source_item=ingested_item,
            tier_score=tier_score,
            shadow_tag_fingerprint=fingerprint,
            energy_score=0.0,  # Filled by ranker
            density_score=fingerprint.density_score if fingerprint else 0.0,
            novelty_score=0.0,  # Filled by ranker
            quality_score=0.0,  # Filled by ranker
            ai_presumed_rank=0.0,  # Filled by ranker
            published_at=datetime.utcnow(),
            verified=auto_verify and shadow_tag_receipt is not None,
        )

        # Rank the item
        ranked_item = ranker.rank_item(content_item)

        # Step 6: Publish to content store (if passed validation)
        published = validation_result.status == ValidationStatus.PASSED

        if published:
            _content_store[ranked_item.item_id] = ranked_item

        processing_time_ms = (time.time() - start_time) * 1000

        # Track metrics
        upload_requests.labels(status=validation_result.status.value).inc()

        response = UploadResponse(
            item_id=ranked_item.item_id,
            validation_status=validation_result.status.value,
            shadow_tag_receipt=shadow_tag_receipt,
            ai_rank=ranked_item.ai_presumed_rank if published else None,
            published=published,
            processing_time_ms=round(processing_time_ms, 2),
        )

        logger.info(
            "content_uploaded",
            item_id=ranked_item.item_id,
            validation_status=validation_result.status.value,
            ai_rank=ranked_item.ai_presumed_rank,
            published=published,
            verified=ranked_item.verified,
        )

        return response

    except Exception as e:
        logger.error("upload_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {e!s}") from e


@app.get("/item/{item_id}")
async def get_item(item_id: str):
    """Get single content item by ID."""
    if item_id not in _content_store:
        raise HTTPException(status_code=404, detail="Item not found")

    item = _content_store[item_id]

    return {
        "item_id": item.item_id,
        "title": item.source_item.title,
        "content": item.source_item.content,
        "author": item.source_item.author,
        "published_at": item.published_at.isoformat(),
        "ai_rank": item.ai_presumed_rank,
        "energy_score": item.energy_score,
        "density_score": item.density_score,
        "novelty_score": item.novelty_score,
        "quality_score": item.quality_score,
        "tier": item.tier_score.tier,
        "verified": item.verified,
        "shadow_tag": (
            {
                "fingerprint_hash": item.shadow_tag_fingerprint.crypto_hash,
                "density_score": item.shadow_tag_fingerprint.density_score,
            }
            if item.shadow_tag_fingerprint
            else None
        ),
    }


@app.post("/verify/{item_id}")
async def verify_item(item_id: str):
    """Verify content authenticity via ShadowTag."""
    if item_id not in _content_store:
        raise HTTPException(status_code=404, detail="Item not found")

    item = _content_store[item_id]

    if not item.shadow_tag_fingerprint:
        return {"verified": False, "reason": "No ShadowTag fingerprint available"}

    return {
        "verified": item.verified,
        "fingerprint": {
            "asset_id": item.shadow_tag_fingerprint.asset_id,
            "crypto_hash": item.shadow_tag_fingerprint.crypto_hash,
            "density_score": item.shadow_tag_fingerprint.density_score,
            "timestamp": item.shadow_tag_fingerprint.timestamp.isoformat(),
        },
        "blockchain": "Polygon + Arweave",
        "verification_url": f"https://pnkln.ai/verify/{item.shadow_tag_fingerprint.asset_id}",
    }


@app.get("/stats")
async def get_stats():
    """Get ShadowTag-v4 platform statistics."""
    ranker, classifier, validator, hasher, receipts = get_services()

    # Calculate tier distribution
    tiers = [item.tier_score.tier for item in _content_store.values()]
    tier_counts = {1: tiers.count(1), 2: tiers.count(2), 3: tiers.count(3)}

    # Calculate verification rate
    verified_count = sum(1 for item in _content_store.values() if item.verified)
    verification_rate = verified_count / len(_content_store) if _content_store else 0.0

    return {
        "total_content": len(_content_store),
        "verified_content": verified_count,
        "verification_rate_pct": round(verification_rate * 100, 1),
        "tier_distribution": tier_counts,
        "ranking_engine": ranker.get_stats(),
        "classifier": classifier.get_stats(),
        "validator": validator.get_stats(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("shadowtag_v4.api:app", host="0.0.0.0", port=8003, reload=True, log_level="info")
