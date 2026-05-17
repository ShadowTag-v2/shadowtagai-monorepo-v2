# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from abc import ABC, abstractmethod

from shared.types import RetrievedChunk


class VectorStore(ABC):
  @abstractmethod
  def upsert(self, namespace: str, items: list[dict]) -> None:
    raise NotImplementedError

  @abstractmethod
  def query(
    self, namespace: str, vector: list[float], top_k: int = 8
  ) -> list[RetrievedChunk]:
    raise NotImplementedError
