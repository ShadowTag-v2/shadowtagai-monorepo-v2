# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Session Memory Compaction — P3.3 Implementation.

Ported from: compact/sessionMemoryCompact.ts
Reference: AGNT STATE B Spec P3.3

Scoring: score = recency*0.4 + relevance*0.35 + frequency*0.25
"""

from __future__ import annotations

import json
import logging
import math
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

RECENCY_WEIGHT = 0.4
RELEVANCE_WEIGHT = 0.35
FREQUENCY_WEIGHT = 0.25
DEFAULT_THRESHOLD = 0.3
RECENCY_HALF_LIFE_HOURS = 72
MAX_COLD_ARCHIVE_SIZE = 50
DEDUP_SIMILARITY_THRESHOLD = 0.7


@dataclass
class SessionMemory:
  """A single memory entry for scoring."""

  id: str
  content: str
  summary: str = ""
  created_at: float = 0.0
  last_accessed: float = 0.0
  access_count: int = 1
  tags: list[str] = field(default_factory=list)
  source: str = "session"
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoredMemory:
  """A memory with its computed score."""

  memory: SessionMemory
  score: float = 0.0
  recency_score: float = 0.0
  relevance_score: float = 0.0
  frequency_score: float = 0.0
  is_duplicate: bool = False
  duplicate_of: str = ""


@dataclass
class CompactionReport:
  """Report from a session memory compaction run."""

  memories_scored: int = 0
  memories_kept: int = 0
  memories_archived: int = 0
  duplicates_merged: int = 0
  score_distribution: dict[str, int] = field(default_factory=dict)
  elapsed_ms: float = 0.0


class MemoryScorer:
  """Scores and partitions session memories for compaction."""

  def __init__(self, half_life_hours: float = RECENCY_HALF_LIFE_HOURS) -> None:
    self._half_life_s = half_life_hours * 3600

  def score_memories(
    self, memories: list[SessionMemory], current_context: str = ""
  ) -> list[ScoredMemory]:
    now = time.time()
    ctx_tokens = self._tokenize(current_context)
    scored = []
    for mem in memories:
      rec = self._recency(mem.last_accessed, now)
      rel = self._relevance(mem, ctx_tokens)
      freq = self._frequency(mem.access_count)
      composite = (
        RECENCY_WEIGHT * rec + RELEVANCE_WEIGHT * rel + FREQUENCY_WEIGHT * freq
      )
      scored.append(
        ScoredMemory(
          memory=mem,
          score=round(composite, 4),
          recency_score=round(rec, 4),
          relevance_score=round(rel, 4),
          frequency_score=round(freq, 4),
        )
      )
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored

  def find_duplicates(self, scored: list[ScoredMemory]) -> list[ScoredMemory]:
    token_sets = [set(self._tokenize(s.memory.content)) for s in scored]
    for i in range(len(scored)):
      if scored[i].is_duplicate:
        continue
      for j in range(i + 1, len(scored)):
        if scored[j].is_duplicate:
          continue
        sim = self._jaccard(token_sets[i], token_sets[j])
        if sim >= DEDUP_SIMILARITY_THRESHOLD:
          scored[j].is_duplicate = True
          scored[j].duplicate_of = scored[i].memory.id
    return scored

  def partition(self, scored: list[ScoredMemory], threshold: float = DEFAULT_THRESHOLD):
    keep = [s for s in scored if not s.is_duplicate and s.score >= threshold]
    archive = [s for s in scored if s.is_duplicate or s.score < threshold]
    return keep, archive

  def _recency(self, last_accessed: float, now: float) -> float:
    if last_accessed <= 0:
      return 0.0
    age = max(0, now - last_accessed)
    return math.pow(2, -age / self._half_life_s)

  def _relevance(self, mem: SessionMemory, ctx_tokens: list[str]) -> float:
    if not ctx_tokens:
      return 0.5 if mem.tags else 0.3
    mem_tokens = set(self._tokenize(mem.content))
    mem_tokens.update(t.lower() for t in mem.tags)
    ctx_set = set(ctx_tokens)
    return len(mem_tokens & ctx_set) / len(ctx_set) if ctx_set else 0.3

  def _frequency(self, count: int) -> float:
    return min(1.0, math.log(count + 1) / 4.62)

  def _tokenize(self, text: str) -> list[str]:
    if not text:
      return []
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    stop = {
      "the",
      "a",
      "an",
      "is",
      "are",
      "was",
      "were",
      "in",
      "on",
      "at",
      "to",
      "for",
      "of",
      "and",
      "or",
      "not",
      "with",
      "this",
      "that",
      "it",
      "be",
      "has",
      "had",
      "have",
      "do",
      "does",
      "will",
      "would",
      "could",
      "should",
      "may",
      "can",
      "from",
      "by",
      "as",
      "but",
      "if",
    }
    return [t for t in tokens if t not in stop and len(t) > 1]

  def _jaccard(self, a: set, b: set) -> float:
    if not a and not b:
      return 1.0
    if not a or not b:
      return 0.0
    return len(a & b) / len(a | b)


def archive_memories(to_archive: list[ScoredMemory], cold_dir: Path) -> int:
  """Write archived memories to cold storage JSONL."""
  if not to_archive:
    return 0
  cold_dir.mkdir(parents=True, exist_ok=True)
  archive_file = cold_dir / "cold_memories.jsonl"
  existing = 0
  if archive_file.exists():
    with open(archive_file) as f:
      existing = sum(1 for _ in f)
  slots = MAX_COLD_ARCHIVE_SIZE - existing
  to_write = to_archive[: max(0, slots)]
  if not to_write:
    return 0
  with open(archive_file, "a") as f:
    for sm in to_write:
      f.write(
        json.dumps(
          {
            "id": sm.memory.id,
            "summary": sm.memory.summary or sm.memory.content[:200],
            "score": sm.score,
            "archived_at": time.time(),
            "source": sm.memory.source,
            "is_duplicate": sm.is_duplicate,
            "duplicate_of": sm.duplicate_of,
          }
        )
        + "\n"
      )
  return len(to_write)
