"""Search API endpoints"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Any

router = APIRouter()


class CreateIndexRequest(BaseModel):
    index_name: str
    documents: list[dict[str, Any]]
    content_field: str = "content"


class SearchRequest(BaseModel):
    index_name: str
    query: str
    top_k: int = 10
    filter_criteria: dict[str, Any] | None = None


class MultimodalSearchRequest(BaseModel):
    index_name: str
    query: str
    modalities: list[str] = ["text", "code"]
    top_k: int = 10


@router.post("/index")
async def create_index(request: CreateIndexRequest, req: Request):
    """Create a new Nowgrep search index"""
    search = req.app.state.search

    if not search:
        raise HTTPException(status_code=503, detail="Search service not initialized")

    result = await search.create_index(index_name=request.index_name, documents=request.documents, content_field=request.content_field)

    return result


@router.post("/search")
async def search_index(request: SearchRequest, req: Request):
    """Perform semantic search on an index"""
    search = req.app.state.search

    if not search:
        raise HTTPException(status_code=503, detail="Search service not initialized")

    result = await search.search(index_name=request.index_name, query=request.query, top_k=request.top_k, filter_criteria=request.filter_criteria)

    return result


@router.post("/multimodal-search")
async def multimodal_search(request: MultimodalSearchRequest, req: Request):
    """Perform multimodal semantic search"""
    search = req.app.state.search

    if not search:
        raise HTTPException(status_code=503, detail="Search service not initialized")

    result = await search.multimodal_search(index_name=request.index_name, query=request.query, modalities=request.modalities, top_k=request.top_k)

    return result
