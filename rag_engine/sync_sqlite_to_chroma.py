# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import logging
import sqlite3

from factory import build_vector_store
from tqdm import tqdm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def transport_vectors(db_path="beads_index.sqlite"):
  """
  Mathematical transport layer bridging the 110GB SQLite Semantic Index to
  the live ChromaDB inference engine.
  """
  logger.info(f"Initializing Source: {db_path} -> Destination: ChromaStore")
  vector_store = build_vector_store()

  try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Agnostically determine the main table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    if not tables:
      logger.error("Beads index is empty or improperly formatted.")
      return

    target_table = tables[0]
    if "chunks" in tables:
      target_table = "chunks"

    logger.info(f"Identified primary index table: {target_table}")

    cur.execute(f"SELECT COUNT(*) FROM {target_table}")
    total_rows = cur.fetchone()[0]

    logger.info(f"Commencing transport of {total_rows} semantic vectors...")

    # Read the table schema to find 'text' or 'content' fields
    cur.execute(f"PRAGMA table_info({target_table})")
    columns = [col[1] for col in cur.fetchall()]

    text_col = (
      "text" if "text" in columns else "content" if "content" in columns else columns[1]
    )
    metadata_cols = [c for c in columns if c != text_col]

    cur.execute(f"SELECT * FROM {target_table}")

    batch_size = 500
    texts_batch = []
    metadatas_batch = []

    for row in tqdm(cur.fetchall(), desc="Syncing Vectors", total=total_rows):
      row_dict = dict(zip(columns, row))
      text_val = str(row_dict.pop(text_col, ""))

      if not text_val.strip():
        continue

      texts_batch.append(text_val)
      metadatas_batch.append(row_dict)

      if len(texts_batch) >= batch_size:
        vector_store.add_texts(texts=texts_batch, metadatas=metadatas_batch)
        texts_batch = []
        metadatas_batch = []

    # Flush remainder
    if texts_batch:
      vector_store.add_texts(texts=texts_batch, metadatas=metadatas_batch)

    logger.info("Vector Resonance transport complete.")

  except sqlite3.OperationalError as e:
    logger.error(f"Cannot bind to SQLite Transport Matrix: {e}")
  except Exception as e:
    logger.error(f"Unexpected architectural failure: {e}")
  finally:
    if "conn" in locals():
      conn.close()


if __name__ == "__main__":
  transport_vectors()
