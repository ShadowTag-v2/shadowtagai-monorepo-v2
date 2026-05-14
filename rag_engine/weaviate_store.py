# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import weaviate
from weaviate.classes.init import Auth

from rag_engine.base import VectorStore
from shared.config import settings
from shared.types import RetrievedChunk


class WeaviateStore(VectorStore):
    def __init__(self, collection_name: str = "MemoryChunk") -> None:
        if not settings.weaviate_url:
            raise RuntimeError("Missing Weaviate configuration")
        auth = Auth.api_key(settings.weaviate_api_key) if settings.weaviate_api_key else None
        self.client = weaviate.connect_to_custom(
            http_host=settings.weaviate_url.replace("https://", "").replace("http://", ""),
            http_secure=settings.weaviate_url.startswith("https://"),
            grpc_host=settings.weaviate_url.replace("https://", "").replace("http://", ""),
            grpc_secure=settings.weaviate_url.startswith("https://"),
            auth_credentials=auth,
        )
        self.collection = self.client.collections.get(collection_name)

    def upsert(self, namespace: str, items: list[dict]) -> None:
        with self.collection.batch.dynamic() as batch:
            for item in items:
                batch.add_object(
                    properties={
                        "namespace": namespace,
                        **item.get("metadata", {}),
                    },
                    uuid=item["id"],
                    vector=item["values"],
                )

    def query(self, namespace: str, vector: list[float], top_k: int = 8) -> list[RetrievedChunk]:
        resp = self.collection.query.near_vector(
            near_vector=vector,
            limit=top_k,
            filters=None,
            return_metadata=["distance"],
        )
        out: list[RetrievedChunk] = []
        for obj in resp.objects:
            props = obj.properties or {}
            if props.get("namespace") != namespace:
                continue
            out.append(
                RetrievedChunk(
                    id=str(obj.uuid),
                    text=props.get("text", ""),
                    score=1.0 - float(getattr(obj.metadata, "distance", 1.0)),
                    metadata=props,
                )
            )
        return out
