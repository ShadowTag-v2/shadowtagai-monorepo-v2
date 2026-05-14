# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from shared.config import settings
from rag_engine.base import VectorStore

from rag_engine.chroma_store import ChromaStore


def build_vector_store() -> VectorStore:
    if settings.vector_backend == "chroma":
        return ChromaStore(db_dir=settings.chroma_db_dir)
    else:
        # Fallback to local zero-cost Chroma storage
        return ChromaStore(db_dir=settings.chroma_db_dir)
