import os
import lancedb
import pyarrow as pa
import logging

LANCEDB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.lancedb"))

SCHEMA = pa.schema(
    [
        pa.field("vector", pa.list_(pa.float32(), 1536)),
        pa.field("filename", pa.string()),
        pa.field("content_size", pa.int32()),
        pa.field("id", pa.string()),
    ]
)


def initialize_db():
    if not os.path.exists(LANCEDB_DIR):
        os.makedirs(LANCEDB_DIR, exist_ok=True)
    db = lancedb.connect(LANCEDB_DIR)
    if "omega_vectors" not in db.table_names():
        db.create_table("omega_vectors", schema=SCHEMA)
    return db.open_table("omega_vectors")


def physical_ingest(filename: str, content_size: int):
    logging.info(f"Connecting to PyArrow LanceDB Matrix at {LANCEDB_DIR}")
    table = initialize_db()

    # Mocked 1536 dim vector for simulation since the Embedding node is remote
    # and we act sovereignly.
    dummy_vector = [0.012] * 1536

    data = [
        {
            "vector": dummy_vector,
            "filename": filename,
            "content_size": content_size,
            "id": f"doc_{filename}",
        }
    ]

    table.add(data)
    logging.info(f"PyArrow successfully committed {filename} directly into LanceDB storage matrix.")
