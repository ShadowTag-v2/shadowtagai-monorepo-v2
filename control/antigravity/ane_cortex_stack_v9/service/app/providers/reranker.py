# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations
from typing import List, Dict, Any


def rerank(query: str, items: list[dict[str, Any]], content_key: str = "content_preview") -> list[dict[str, Any]]:
    qtokens = set(query.lower().split())
    rescored = []
    for item in items:
        hay = str(item.get(content_key, "")) + " " + str(item.get("title", ""))
        score = float(item.get("score", 0.0))
        tokens = set(hay.lower().split())
        overlap = len(qtokens & tokens)
        item["score"] = score + overlap
        rescored.append(item)
    rescored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return rescored
