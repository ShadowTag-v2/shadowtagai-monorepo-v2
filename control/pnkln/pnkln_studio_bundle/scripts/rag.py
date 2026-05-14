# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Minimal RAG: build embeddings matrix (NPY) + metadata, and answer queries with cosine."""

from __future__ import annotations
from typing import Any
import json
import numpy as np
from .vertex import embedding, gemini

_em = embedding()
_gm = gemini()


def build(items: list[dict[str, Any]], np_out: str, meta_out: str) -> None:
    vecs, meta = [], []
    for it in items:
        e = _em.get_embeddings([it["t"]])[0].values
        vecs.append(np.array(e, dtype=np.float32))
        meta.append({"k": it["k"], "t": it["t"]})
    np.save(np_out, np.stack(vecs, 0))
    with open(meta_out, "w", encoding="utf-8") as f:
        json.dump(meta, f, separators=(",", ":"))


def query(q: str, np_path: str, meta_path: str, top: int = 3) -> str:
    V = np.load(np_path)
    M = json.load(open(meta_path))
    e = np.array(_em.get_embeddings([q])[0].values, dtype=np.float32)
    scores = []
    for i in range(len(M)):
        vi = V[i]
        s = float(vi.dot(e) / ((np.linalg.norm(vi) * np.linalg.norm(e)) or 1e-9))
        scores.append((i, s))
    scores.sort(key=lambda x: x[1], reverse=True)
    ctx = "\n".join(M[i]["t"] for i, _ in scores[:top])
    return _gm.generate_content(["Use context to answer.\n", ctx, "\nQ:", q]).text
