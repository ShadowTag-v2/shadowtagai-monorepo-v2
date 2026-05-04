#!/usr/bin/env python3
"""Legal Evidence Query Interface.

Queries the ChromaDB knowledge graph populated by evidence_pipeline.py.
"""

import logging
import sys
from pathlib import Path

# Third-party imports
try:
    import chromadb
except ImportError:
    print("Missing dependency: chromadb. Run: pip install chromadb")
    raise SystemExit(1)

# Configuration
DB_PATH = Path("data/legal_knowledge_graph")


def query_evidence(query_text: str, n_results: int = 3):
    """Query the legal knowledge graph."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run 'src/pnkln/ingestion/evidence_pipeline.py' first.")
        return

    try:
        # Initialize Client
        client = chromadb.PersistentClient(path=str(DB_PATH))
        collection = client.get_collection(name="legal_briefs")

        print(f"\n🔎 Searching for: '{query_text}'...")

        # Query
        results = collection.query(query_texts=[query_text], n_results=n_results)

        # Display Results
        if not results["ids"][0]:
            print("No matches found.")
            return

        print(f"\n--- Top {len(results['ids'][0])} Matches ---")
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i]
            doc_snippet = results["documents"][0][i][:200].replace("\n", " ")

            print(f"\n📄 Match #{i + 1}")
            print(f"   Title:    {meta.get('title', 'Unknown')}")
            print(f"   Category: {meta.get('category', 'Unknown')}")
            print(f"   Date:     {meta.get('capture_date', 'Unknown')}")
            print(f"   Hash:     {meta.get('evidence_hash', 'Unknown')[:8]}...")
            print(f"   Evidence: {meta.get('evidence_file', 'Unknown')}")
            print(f"   Snippet:  {doc_snippet}...")
            print("-" * 40)

    except Exception as e:
        print(f"Query failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    if len(sys.argv) > 1:
        query_text = " ".join(sys.argv[1:])
        query_evidence(query_text)
    else:
        print("Legal Evidence Query Tool")
        print("Usage: python scripts/query_legal_evidence.py 'your search query'")

        while True:
            try:
                user_input = input("\n🔎 Enter query (or 'q' to quit): ").strip()
                if user_input.lower() in ("q", "quit", "exit"):
                    break
                if user_input:
                    query_evidence(user_input)
            except KeyboardInterrupt:
                break
