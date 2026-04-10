"""Data Operations API endpoints"""

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class StoreEmbeddingsRequest(BaseModel):
    embedding_id: str
    embeddings: list[float]
    metadata: dict[str, Any] | None = None


class SaveAdapterRequest(BaseModel):
    adapter_id: str
    adapter_weights: dict[str, Any]
    metadata: dict[str, Any] | None = None


@router.post("/embeddings")
async def store_embeddings(request: StoreEmbeddingsRequest, req: Request):
    """Store embeddings in Hive storage"""
    dataops = req.app.state.dataops

    if not dataops:
        raise HTTPException(status_code=503, detail="DataOps service not initialized")

    result = await dataops.store_embeddings(
        embedding_id=request.embedding_id, embeddings=request.embeddings, metadata=request.metadata
    )

    return result


@router.get("/embeddings/{embedding_id}")
async def retrieve_embeddings(embedding_id: str, req: Request):
    """Retrieve embeddings from Hive storage"""
    dataops = req.app.state.dataops

    if not dataops:
        raise HTTPException(status_code=503, detail="DataOps service not initialized")

    result = await dataops.retrieve_embeddings(embedding_id)

    if not result:
        raise HTTPException(status_code=404, detail="Embeddings not found")

    return result


@router.post("/adapters")
async def save_adapter(request: SaveAdapterRequest, req: Request):
    """Save MoE-CL adapter weights"""
    dataops = req.app.state.dataops

    if not dataops:
        raise HTTPException(status_code=503, detail="DataOps service not initialized")

    result = await dataops.save_adapter(
        adapter_id=request.adapter_id,
        adapter_weights=request.adapter_weights,
        metadata=request.metadata,
    )

    return result


@router.get("/adapters/{adapter_id}")
async def load_adapter(adapter_id: str, req: Request):
    """Load MoE-CL adapter weights"""
    dataops = req.app.state.dataops

    if not dataops:
        raise HTTPException(status_code=503, detail="DataOps service not initialized")

    result = await dataops.load_adapter(adapter_id)

    if not result:
        raise HTTPException(status_code=404, detail="Adapter not found")

    return result


@router.get("/metrics")
async def get_storage_metrics(req: Request):
    """Get storage service metrics"""
    dataops = req.app.state.dataops

    if not dataops:
        raise HTTPException(status_code=503, detail="DataOps service not initialized")

    metrics = await dataops.get_storage_metrics()
    return metrics
