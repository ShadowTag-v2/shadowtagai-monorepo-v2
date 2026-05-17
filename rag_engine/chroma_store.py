# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import logging

import chromadb

from rag_engine.base import VectorStore
from shared.types import RetrievedChunk


class ChromaStore(VectorStore):
  """
  Zero-Cost Local Vector Database using ChromaDB.
  Runs entirely on-device, storing files mathematically to disk at no cost.
  """

  def __init__(self, db_dir: str, collection_name: str = "coryay_knowledge"):
    self.logger = logging.getLogger("ChromaStore")
    self.db_dir = db_dir
    self.collection_name = collection_name

    # Initialize Persistent Local Storage
    self.client = chromadb.PersistentClient(path=self.db_dir)
    self.collection = self.client.get_or_create_collection(name=self.collection_name)
    self.logger.info(f"ChromaDB local vector engine initialized at {self.db_dir}")

  def upsert(self, record_id: str, vector: list[float], metadata: dict) -> None:
    self.collection.upsert(ids=[record_id], embeddings=[vector], metadatas=[metadata])
    self.logger.debug(f"Upserted local vector {record_id} into ChromaDB")

  def query(
    self, vector: list[float], top_k: int = 5, filters: dict | None = None, **kwargs
  ) -> list[RetrievedChunk]:
    # Discard unsupported namespace/timeline kwargs that Pinecone used
    results = self.collection.query(
      query_embeddings=[vector],
      n_results=top_k,
      where=filters if filters else None,
      include=["metadatas"],
    )

    chunks = []
    if results and results["ids"] and results["ids"][0]:
      for i, result_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i] if results["metadatas"] else {}

        # Assume a default similarity score of 1.0 since distance isn't automatically normalized
        # (Chroma usually returns L2 distances, not straight cosine similarity unless configured)
        # But for interface matching we pass float(1.0).

        text_content = meta.get("text", "")
        chunks.append(
          RetrievedChunk(id=result_id, text=text_content, score=1.0, metadata=meta)
        )
    return chunks
