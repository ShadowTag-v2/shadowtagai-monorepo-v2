# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from pinecone import Pinecone

from rag_engine.base import VectorStore
from shared.config import settings
from shared.types import RetrievedChunk


class PineconeStore(VectorStore):
    def __init__(self) -> None:
        if not settings.pinecone_api_key or not settings.pinecone_index_host:
            raise RuntimeError("Missing Pinecone configuration")
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.pc.Index(host=settings.pinecone_index_host)

    def upsert(self, namespace: str, items: list[dict]) -> None:
        self.index.upsert(vectors=items, namespace=namespace)

    def query(self, namespace: str, vector: list[float], top_k: int = 8) -> list[RetrievedChunk]:
        result = self.index.query(
            namespace=namespace,
            vector=vector,
            top_k=top_k,
            include_values=False,
            include_metadata=True,
        )
        return [
            RetrievedChunk(
                id=m["id"] if isinstance(m, dict) else m.id,
                text=((m.get("metadata", {}) or {}).get("text", "") if isinstance(m, dict) else getattr(m, "metadata", {}).get("text", "")),
                score=m["score"] if isinstance(m, dict) else m.score,
                metadata=(m.get("metadata", {}) if isinstance(m, dict) else getattr(m, "metadata", {})) or {},
            )
            for m in result.matches
        ]
