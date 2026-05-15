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


def ingest_document(workspace_id: int, text: str):
  pass  # Implementation omitted for brevity
