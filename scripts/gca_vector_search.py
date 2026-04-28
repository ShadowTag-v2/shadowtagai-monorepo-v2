# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

# Try importing Chroma and SentenceTransformer natively
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    sys.exit(1)


def query_hud_vectors(query_text: str, top_k: int = 10) -> None:
    """Direct interface for the GCA HUD to query the 255k code chunks inside the localized ChromaDB."""
    db_path = os.path.abspath(".chroma_db")
    if not os.path.exists(db_path):
        return

    client = chromadb.PersistentClient(path=db_path)
    # The default ChromaStore collection name in factory.py
    collection = client.get_collection(name="coryay_knowledge")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector = model.encode(query_text).tolist()

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["metadatas", "documents", "distances"],
    )

    # Check if results exist
    if not results or not results["ids"] or not results["ids"][0]:
        return

    # Iterate through the parallel arrays
    for i in range(len(results["ids"][0])):
        results["ids"][0][i]
        results["distances"][0][i]
        metadata = results["metadatas"][0][i]
        results["documents"][0][i] if results.get("documents") else "<Code snippet absent in this index format>"

        metadata.get("source", metadata.get("filename", "Unknown Source"))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    query_hud_vectors(query)
