# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import sys

# Try importing Chroma and SentenceTransformer natively
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Dependencies missing for vector search. Run: uv pip install chromadb sentence-transformers")
    sys.exit(1)


def query_hud_vectors(query_text: str, top_k: int = 10):
    """
    Direct interface for the GCA HUD to query the 255k code chunks inside the localized ChromaDB.
    """
    db_path = os.path.abspath(".chroma_db")
    if not os.path.exists(db_path):
        print(f"❌ ChromaDB not found at {db_path}. Run reindex_monorepo.py first.")
        return

    print(f"🔍 Initializing local Vector Engine at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    # The default ChromaStore collection name in factory.py
    collection = client.get_collection(name="coryay_knowledge")

    print(f"🧠 Loading SentenceTransformer model (all-MiniLM-L6-v2) to embed query: '{query_text}'")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector = model.encode(query_text).tolist()

    print("⚡ Executing similarity search against 255,000+ local code vectors...")
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["metadatas", "documents", "distances"],
    )

    # Check if results exist
    if not results or not results["ids"] or not results["ids"][0]:
        print("🕳️ No semantic matches found.")
        return

    print("\n" + "=" * 50)
    print(f"🎯 TOP {top_k} RAG KNOWLEDGE HITS:")
    print("=" * 50)

    # Iterate through the parallel arrays
    for i in range(len(results["ids"][0])):
        match_id = results["ids"][0][i]
        distance = results["distances"][0][i]
        metadata = results["metadatas"][0][i]
        document = results["documents"][0][i] if "documents" in results and results["documents"] else "<Code snippet absent in this index format>"

        source_file = metadata.get("source", metadata.get("filename", "Unknown Source"))
        print(f"\n[{i + 1}] 📄 File: {source_file}")
        print(f"    📏 Vector Distance: {distance:.4f}")
        print(f"    🧩 Snippet:\n{document[:300]}...\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/gca_vector_search.py "your search query here"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    query_hud_vectors(query)
