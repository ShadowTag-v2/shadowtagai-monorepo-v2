# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import APIRouter

from ..config import load_settings
from ..models.contracts import SearchRequest, SearchResponse, SearchResultItem
from ..providers.reranker import rerank
from ..retrieval.context_builder import collect_context

router = APIRouter(prefix="/api")


@router.post("/search", response_model=SearchResponse)
def api_search(req: SearchRequest):
    s = load_settings()
    exact, semantic, memory, tasks, _, _ = collect_context(
        s.sqlite_db,
        s.lancedb_root,
        s.postgres_dsn,
        req.repo_id,
        req.query,
        s.authority_state_path,
        req.limit,
    )
    exact_items = [
        SearchResultItem(
            source="sqlite",
            id=r["doc_id"],
            title=r["rel_path"],
            rel_path=r["rel_path"],
            score=1.0,
            content_preview=r["body"],
        ).model_dump()
        for r in exact
    ]
    semantic_items = [
        SearchResultItem(
            source="lancedb",
            id=str(r.get("chunk_id")),
            title=r.get("title", ""),
            rel_path=r.get("rel_path"),
            score=float(r.get("_distance", 0.0) or 0.0),
            content_preview=str(r.get("content", ""))[:500],
        ).model_dump()
        for r in semantic
    ]
    memory_items = [
        SearchResultItem(
            source=r.get("source", "memory"),
            id=r["title"],
            title=r["title"],
            score=0.5,
            content_preview=r["content"],
        ).model_dump()
        for r in memory
    ]
    task_items = [
        SearchResultItem(
            source="beads",
            id=r["id"],
            title=r["title"],
            score=0.5,
            content_preview=r["summary"],
            metadata={"status": r["status"]},
        ).model_dump()
        for r in tasks
    ]
    semantic_items = rerank(req.query, semantic_items)
    memory_items = rerank(req.query, memory_items)
    return SearchResponse(
        query=req.query,
        repo_id=req.repo_id,
        exact=[SearchResultItem(**x) for x in exact_items],
        semantic=[SearchResultItem(**x) for x in semantic_items],
        memory=[SearchResultItem(**x) for x in memory_items],
        tasks=[SearchResultItem(**x) for x in task_items],
    )
