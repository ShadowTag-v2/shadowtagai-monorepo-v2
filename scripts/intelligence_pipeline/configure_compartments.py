# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Dual-Stack Architecture: LanceDB Compartment Initializer
Ensures absolute isolation between internal sovereign data and external API data.

Creates two compartments:
  - workspace_knowledge (internal: Drive docs, monorepo files, session artifacts)
  - external_research  (external: web search results, API responses, scraped data)
"""

import logging
from pathlib import Path

import lancedb
import pyarrow as pa

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
LANCEDB_DIR = REPO_ROOT / "data" / "lancedb"

COMPARTMENTS = {
    "workspace_knowledge": pa.schema(
        [
            pa.field("id", pa.string()),
            pa.field("title", pa.string()),
            pa.field("source", pa.string()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 768)),
            pa.field("domain", pa.string()),
            pa.field("ingested_at", pa.string()),
        ],
    ),
    "external_research": pa.schema(
        [
            pa.field("id", pa.string()),
            pa.field("query", pa.string()),
            pa.field("source_url", pa.string()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 768)),
            pa.field("fetched_at", pa.string()),
        ],
    ),
}


def initialize_compartments() -> dict:
    """Initialize LanceDB compartments with schema enforcement."""
    db = lancedb.connect(str(LANCEDB_DIR))
    existing = set(db.table_names())
    created = []

    for name, schema in COMPARTMENTS.items():
        if name not in existing:
            db.create_table(name, schema=schema)
            logger.info(f"Created compartment: {name}")
            created.append(name)
        else:
            logger.info(f"Compartment exists: {name}")

    return {"created": created, "existing": list(existing)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = initialize_compartments()
