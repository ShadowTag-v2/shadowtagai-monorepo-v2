import glob
import os

import lancedb
import pyarrow as pa

# LanceDB Automation Stub
# Maps semantic routing edges to the `.lancedb/` directory for zero-latency lookups.


def init_pipeline():
    print("Initiating Sovereign LanceDB Semantic Pipeline...")

    db_path = os.path.join(os.getcwd(), ".lancedb")
    db = lancedb.connect(db_path)

    # Establish default metadata table
    if "semantic_edges" not in db.table_names():
        print("Creating semantic_edges table schema.")
        schema = pa.schema([pa.field("vector", pa.list_(pa.float32(), 2)), pa.field("source", pa.string()), pa.field("text", pa.string())])
        db.create_table("semantic_edges", schema=schema)
    else:
        print("semantic_edges table operational.")

    return db


def ingest_directory(db, directory_path="."):
    """Ingest documents into LanceDB."""
    table = db.open_table("semantic_edges")
    print(f"Ingesting documents from {directory_path}...")

    docs_to_ingest = []
    for filepath in glob.glob(os.path.join(directory_path, "**/*.md"), recursive=True):
        if ".lancedb" in filepath or "node_modules" in filepath:
            continue

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
                docs_to_ingest.append(
                    {
                        "vector": [0.1, 0.2],  # Stubbed embedding, substitute with local model
                        "source": filepath,
                        "text": content[:1000],
                    }
                )
        except Exception as e:
            print(f"Failed to read {filepath}: {e}")

    if docs_to_ingest:
        table.add(docs_to_ingest)
        print(f"Successfully ingested {len(docs_to_ingest)} documents.")
    else:
        print("No documents found for ingestion.")


if __name__ == "__main__":
    db = init_pipeline()
    print("Pipeline Ready.")

    # ingest_directory(db, directory_path="./docs")
