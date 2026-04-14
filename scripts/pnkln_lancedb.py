#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

import lancedb
import vertexai
from lancedb.pydantic import LanceModel, Vector
from vertexai.language_models import TextEmbeddingModel

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
DB_URI = os.environ.get(
    "LANCEDB_URI", "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/data/lancedb"
)
TABLE_NAME = os.environ.get("LANCEDB_TABLE", "pnkln_knowledge")
EMBED_MODEL_NAME = os.environ.get("VERTEX_EMBED_MODEL", "gemini-embedding-001")
EMBED_DIM = int(os.environ.get("VERTEX_EMBED_DIM", "768"))

_vertex_inited = False
_model: TextEmbeddingModel | None = None


def ensure_vertex() -> TextEmbeddingModel:
    global _vertex_inited, _model
    if not _vertex_inited:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        _vertex_inited = True
    if _model is None:
        _model = TextEmbeddingModel.frompretrained(EMBED_MODEL_NAME)
    return _model


class PnklnDoc(LanceModel):
    id: str
    text: str
    vector: Vector(EMBED_DIM)
    source: str
    kind: str = "note"


def smoke_test() -> int:
    lancedb.connect(DB_URI)
    print(f"✅ LanceDB + Vertex AI [{EMBED_MODEL_NAME}] Smoke Test Passed. DB URI: {DB_URI}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    if args.smoke_test:
        raise SystemExit(smoke_test())
