# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LanceDB RAG ingestion for CounselConduit sovereign memory."""

import os

import lancedb
import pyarrow as pa

DB_PATH = os.path.join(os.getcwd(), ".lancedb_data")
db = lancedb.connect(DB_PATH)
schema = pa.schema(
    [
        pa.field("workspace_id", pa.int32()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 768)),
    ]
)


def ingest_document(_workspace_id: int, _text: str):
    """Ingest a document into the vector database."""
    pass  # Implementation follows in Phase 2
