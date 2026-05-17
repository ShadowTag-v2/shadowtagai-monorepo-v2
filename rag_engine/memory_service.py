# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import hashlib

from rag_engine.factory import build_vector_store


class SequentialMemoryService:
  def __init__(self, embed_fn):
    self.store = build_vector_store()
    self.embed_fn = embed_fn

  def persist_traversal(self, timeline_id: str, events: list[dict]) -> None:
    payload = []
    for event in events:
      text = event["text"]
      vec = self.embed_fn(text)
      event_id = hashlib.sha256(f"{timeline_id}:{text}".encode()).hexdigest()
      payload.append(
        {
          "id": event_id,
          "values": vec,
          "metadata": {
            "timeline_id": timeline_id,
            "text": text,
            "timestamp": event.get("timestamp"),
            "node_type": event.get("node_type", "trace"),
          },
        }
      )
    for item in payload:
      self.store.upsert(
        record_id=item["id"], vector=item["values"], metadata=item["metadata"]
      )

  def retrieve(self, timeline_id: str, query: str, top_k: int = 8):
    qv = self.embed_fn(query)
    return self.store.query(namespace=timeline_id, vector=qv, top_k=top_k)
