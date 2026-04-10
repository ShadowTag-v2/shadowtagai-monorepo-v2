from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    source: str
    id: str
    title: str
    rel_path: str | None = None
    score: float = 0.0
    content_preview: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    query: str
    repo_id: str = "ane"
    limit: int = 8


class SearchResponse(BaseModel):
    query: str
    repo_id: str
    exact: list[SearchResultItem]
    semantic: list[SearchResultItem]
    memory: list[SearchResultItem]
    tasks: list[SearchResultItem]


class ContextRequest(BaseModel):
    query: str
    repo_id: str = "ane"


class ContextResponse(BaseModel):
    query: str
    repo_id: str
    prompt_context: str
    selected_ids: dict[str, list[str]]
