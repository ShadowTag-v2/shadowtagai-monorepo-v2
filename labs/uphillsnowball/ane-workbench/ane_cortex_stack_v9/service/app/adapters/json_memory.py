# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class JsonMemoryStore:
  """
  Indexless append-only JSONL memory store.
  Each line is one memory object.
  Retrieval is linear scan by design.
  """

  def __init__(self, path: str = "./data/memory/memories.jsonl"):
    self.path = Path(path)
    self.path.parent.mkdir(parents=True, exist_ok=True)

  def append(self, memory: dict[str, Any]) -> dict[str, Any]:
    item = {
      "id": memory.get("id", str(uuid.uuid4())),
      "type": memory.get("type", "memory"),
      "subject": memory.get("subject", ""),
      "summary": memory.get("summary", ""),
      "body": memory.get("body", ""),
      "tags": memory.get("tags", []),
      "repo_id": memory.get("repo_id", "ane"),
      "created_at": memory.get("created_at", datetime.now(UTC).isoformat()),
    }
    with self.path.open("a", encoding="utf-8") as f:
      f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return item

  def all(self) -> list[dict[str, Any]]:
    if not self.path.exists():
      return []
    out = []
    with self.path.open("r", encoding="utf-8") as f:
      for line in f:
        line = line.strip()
        if not line:
          continue
        try:
          out.append(json.loads(line))
        except Exception:
          continue
    return out

  def search(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
    q = query.lower()
    scored = []
    for item in self.all():
      hay = " ".join(
        [
          str(item.get("subject", "")),
          str(item.get("summary", "")),
          str(item.get("body", "")),
          " ".join(item.get("tags", [])),
        ]
      ).lower()
      score = 0
      if q in hay:
        score += 10
      for token in query.lower().split():
        if token in hay:
          score += 1
      if score > 0:
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [i for _, i in scored[:limit]]
