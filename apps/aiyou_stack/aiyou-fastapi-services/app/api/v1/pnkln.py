# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN API Endpoints
===================

REST API for PNKLN intelligence pipeline:
- /search: Semantic search with card-based results
- /assist: Vehicle assist endpoint with safety gates
- /mesh: Infrastructure mesh statistics
- /health: Health check
- /chain: Parallel chain execution
"""

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pnkln_intelligence.chains.parallel_chain import pnkln_parallel
from pnkln_intelligence.core.pnkln_core import (
    Nowgrep,
    get_mesh_stats,
    rerank,
    rot_retrieve,
)
from pnkln_intelligence.safety.content_safety import safety_gate
from pydantic import BaseModel, Field

# =============================================================================
# Router Setup
# =============================================================================

router = APIRouter()

# Global Nowgrep instance with sample data
_nowgrep: Nowgrep | None = None


def get_nowgrep() -> Nowgrep:
    """Get or initialize the global Nowgrep instance with sample data."""
    global _nowgrep
    if _nowgrep is None:
        _nowgrep = Nowgrep()
        # Add sample documents
        _nowgrep.add(
            [
                {
                    "id": "1",
                    "text": "Provenance video search; court-grade bundles; SOC2 exports.",
                    "category": "legal",
                },
                {
                    "id": "2",
                    "text": "Haptic try-before-buy; VR scenes; 60-120ms edge latency.",
                    "category": "retail",
                },
                {
                    "id": "3",
                    "text": "Agentic shopping rails: Book/Buy/Fix; private local fusion.",
                    "category": "commerce",
                },
                {
                    "id": "4",
                    "text": "Tower mesh: CoreWeave+Starlink; roadside LiDAR; FSD assist.",
                    "category": "automotive",
                },
                {
                    "id": "5",
                    "text": "Real-time video attestation with neural hash fingerprinting.",
                    "category": "security",
                },
                {
                    "id": "6",
                    "text": "Edge inference pipeline for autonomous vehicle perception.",
                    "category": "automotive",
                },
            ],
        )
        _nowgrep.build()
    return _nowgrep


# =============================================================================
# Pydantic Models
# =============================================================================


class SearchCard(BaseModel):
    """Card representation of a search result."""

    title: str = "pnkln"
    prov: str = "signed:true len:6"
    acts: list[str] = Field(default_factory=lambda: ["Sim", "Buy", "Book", "Export"])
    snip: str
    score: float
    id: str


class SearchResponse(BaseModel):
    """Response from search endpoint."""

    cards: list[SearchCard]
    count: int
    query: str
    query_time_ms: float


class AssistRequest(BaseModel):
    """Request for vehicle assist."""

    vin: str = Field(..., description="Vehicle Identification Number")
    sensors: list[str] = Field(default_factory=lambda: ["cam"])
    pose: list[float] = Field(default_factory=lambda: [37.6, -122.3, 15.2])
    need: str = Field(default="lane+occlusion", description="Type of assistance needed")
    note: str = Field(default="ok", description="Additional notes (checked for safety)")


class AssistResponse(BaseModel):
    """Response from vehicle assist."""

    lane: str = "ok"
    occlusion: str = "clear"
    advice: str = "maintain_speed"
    proof: str = "signed-bundle-id"
    safe: bool = True
    safety_details: dict | None = None


class MeshStatsResponse(BaseModel):
    """Infrastructure mesh statistics."""

    lat_ms: dict[str, int]
    fsd_events: dict[str, float]
    token_per_M: dict[str, float]
    throughput_gain_pct: int
    safety_gain_pct: int


class ChainRequest(BaseModel):
    """Request for parallel chain execution."""

    prompt: str = Field(..., description="Prompt or task to execute")
    store_trace: bool = Field(default=True, description="Store in ROT graph")


class ChainResponse(BaseModel):
    """Response from chain execution."""

    content: str
    plan: str
    meta: dict
    trace_id: str | None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    nowgrep_docs: int
    nowgrep_built: bool
    version: str = "0.2.0"


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    topk: int = Query(default=6, ge=1, le=20, description="Number of results"),
) -> SearchResponse:
    """Semantic search with card-based results.

    Uses Nowgrep for fast semantic search with all-MiniLM-L6-v2
    embeddings and position-aware reranking.
    """
    start_time = time.time()

    try:
        ng = get_nowgrep()
        results = ng.search(q, topk=topk)
        reranked = rerank(q, results)[:topk]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}") from e

    cards = [SearchCard(snip=r.text[:96], score=round(r.rank_score, 3), id=r.id) for r in reranked]

    query_time = (time.time() - start_time) * 1000

    return SearchResponse(
        cards=cards,
        count=len(cards),
        query=q,
        query_time_ms=round(query_time, 2),
    )


@router.post("/assist", response_model=AssistResponse)
async def assist(request: AssistRequest) -> AssistResponse:
    """Vehicle assist endpoint with safety validation.

    Provides lane and occlusion information for FSD assist,
    with safety gates on user notes.
    """
    # Run safety gate on the note field
    safety_result = safety_gate({"text": request.note})

    if not safety_result.safe:
        return AssistResponse(
            lane="blocked",
            occlusion="blocked",
            advice="safety_violation",
            proof="none",
            safe=False,
            safety_details=safety_result.to_dict(),
        )

    # Simulate assist response based on request
    occlusion = "clear"
    advice = "maintain_speed"

    if "occlusion" in request.need:
        occlusion = "left-25m"
        advice = "slow_3mps"

    return AssistResponse(
        lane="ok",
        occlusion=occlusion,
        advice=advice,
        proof=f"signed-{request.vin[:8]}",
        safe=True,
        safety_details=safety_result.to_dict(),
    )


@router.get("/mesh", response_model=MeshStatsResponse)
async def get_mesh() -> MeshStatsResponse:
    """Get infrastructure mesh statistics.

    Returns latency, FSD event rates, token costs, and
    throughput/safety gains from mesh optimization.
    """
    stats = get_mesh_stats()
    return MeshStatsResponse(**stats)


@router.post("/chain", response_model=ChainResponse)
async def run_chain(request: ChainRequest) -> ChainResponse:
    """Execute R1→R2→R3 parallel chain.

    Runs the prompt through generation, analysis, and
    finalization stages with ROT trace storage.
    """
    try:
        result = pnkln_parallel(prompt=request.prompt, store_trace=request.store_trace)
        return ChainResponse(**result.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chain execution failed: {e}") from e


@router.get("/rot/retrieve")
async def retrieve_rot(hint: str = Query(..., description="Hint to search for")) -> dict[str, Any]:
    """Retrieve ROT node by hint.

    Searches reasoning traces for a node containing the hint.
    """
    node = rot_retrieve(hint)
    if node is None:
        return {"found": False, "node": None}
    return {"found": True, "node": node}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check with Nowgrep status.

    Returns service health and Nowgrep index status.
    """
    try:
        ng = get_nowgrep()
        return HealthResponse(status="healthy", nowgrep_docs=ng.count, nowgrep_built=ng.is_built)
    except Exception as e:
        return HealthResponse(status=f"degraded: {e}", nowgrep_docs=0, nowgrep_built=False)
