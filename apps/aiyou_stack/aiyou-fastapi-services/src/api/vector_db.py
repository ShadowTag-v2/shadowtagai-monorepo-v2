# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os

import lancedb
import pyarrow as pa
from litellm import embedding

db = lancedb.connect(os.path.join(os.getcwd(), ".lancedb_data"))
schema = pa.schema(
    [
        pa.field("workspace_id", pa.int32()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 768)),
    ],
)
table = (
    db.create_table("workspace_knowledge", schema=schema)
    if "workspace_knowledge" not in db.table_names()
    else db.open_table("workspace_knowledge")
)


def get_gemini_embedding(text: str) -> list[float]:
    response = embedding(model="gemini/text-embedding-004", input=[text])
    return (
        response.data[0]["embedding"]
        if isinstance(response.data[0], dict)
        else response.data[0].embedding
    )


def search_workspace_knowledge(workspace_id: int, query: str) -> str:
    try:
        results = (
            table.search(get_gemini_embedding(query))
            .where(f"workspace_id = {workspace_id}")
            .limit(3)
            .to_list()
        )
        return (
            "\n---\n".join([f"Found Context:\n{r['text']}" for r in results])
            if results
            else "No internal documents found."
        )
    except Exception as e:
        return f"Internal search failed: {e!s}"
