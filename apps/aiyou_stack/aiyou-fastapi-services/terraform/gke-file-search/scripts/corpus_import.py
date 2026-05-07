#!/usr/bin/env python3
"""PNKLN CORE STACK - RAG Corpus Import Tool
==========================================
Purpose: Import policy documents from GCS into Vertex AI RAG corpora
Usage: python corpus_import.py --vertical defense --path gs://bucket/path/
"""

import argparse
import sys

from google.cloud import aiplatform
from vertexai.preview import rag


def list_corpora(project_id: str, region: str) -> None:
    """List all available RAG corpora"""
    aiplatform.init(project=project_id, location=region)

    print("\nAvailable RAG Corpora:")
    print("=" * 60)

    try:
        corpora = rag.list_corpora()
        for corpus in corpora:
            print(f"\n  Name: {corpus.display_name}")
            print(f"  ID:   {corpus.name}")
            print(f"  Description: {corpus.description}")
    except Exception as e:
        print(f"Error listing corpora: {e}", file=sys.stderr)
        raise SystemExit(1) from e


def import_files(
    project_id: str,
    region: str,
    vertical: str,
    gcs_path: str,
    chunk_size: int = 512,
    chunk_overlap: int = 100,
) -> None:
    """Import files from GCS into RAG corpus"""
    aiplatform.init(project=project_id, location=region)

    corpus_name = f"pnkln_{vertical}_policies"

    print(f"\nImporting files to corpus: {corpus_name}")
    print(f"Source: {gcs_path}")
    print("=" * 60)

    try:
        # Find the corpus
        corpora = rag.list_corpora()
        target_corpus = None

        for corpus in corpora:
            if corpus.display_name == corpus_name:
                target_corpus = corpus
                break

        if not target_corpus:
            print(f"Error: Corpus '{corpus_name}' not found", file=sys.stderr)
            print("Run: python corpus_import.py --list-corpora", file=sys.stderr)
            raise SystemExit(1)

        # Import files
        print(f"\nImporting from: {gcs_path}")
        print(f"Chunk size: {chunk_size}, Overlap: {chunk_overlap}")

        # Support both single file and directory patterns
        paths = [gcs_path]
        if gcs_path.endswith("*"):
            # Directory pattern - will import all files
            paths = [gcs_path]

        rag.import_files(
            corpus_name=target_corpus.name,
            paths=paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_embedding_requests_per_min=900,  # Rate limit
        )

        print("\n✓ Import successful!")
        print(f"  Corpus: {corpus_name}")
        print(f"  Files imported: {len(paths)}")

    except Exception as e:
        print(f"\n✗ Import failed: {e}", file=sys.stderr)
        raise SystemExit(1) from e


def query_corpus(project_id: str, region: str, vertical: str, query: str, top_k: int = 5) -> None:
    """Test query against a RAG corpus"""
    from vertexai.generative_models import GenerativeModel

    aiplatform.init(project=project_id, location=region)

    corpus_name = f"pnkln_{vertical}_policies"

    print(f"\nQuerying corpus: {corpus_name}")
    print(f"Query: {query}")
    print("=" * 60)

    try:
        # Find the corpus
        corpora = rag.list_corpora()
        target_corpus = None

        for corpus in corpora:
            if corpus.display_name == corpus_name:
                target_corpus = corpus
                break

        if not target_corpus:
            print(f"Error: Corpus '{corpus_name}' not found", file=sys.stderr)
            raise SystemExit(1)

        # Create model with RAG retrieval
        model = GenerativeModel("gemini-3.1-flash-lite-preview")

        response = model.generate_content(
            query,
            tools=[
                rag.Tool(
                    retrieval=rag.Retrieval(
                        source=rag.VertexRagStore(
                            rag_corpora=[target_corpus.name],
                        ),
                        similarity_top_k=top_k,
                    ),
                ),
            ],
        )

        print("\n✓ Query Results:")
        print(f"\nResponse:\n{response.text}\n")

        if response.candidates[0].grounding_metadata:
            print("Source Citations:")
            for i, chunk in enumerate(
                response.candidates[0].grounding_metadata.grounding_chunks,
                1,
            ):
                print(f"  [{i}] {chunk}")

    except Exception as e:
        print(f"\n✗ Query failed: {e}", file=sys.stderr)
        raise SystemExit(1) from e


def main():
    parser = argparse.ArgumentParser(
        description="Pnkln RAG Corpus Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all corpora
  python corpus_import.py --list-corpora --project pnkln-core-gke

  # Import files to defense vertical
  python corpus_import.py --vertical defense \\
    --path gs://pnkln-policy-corpus-defense/regulatory/*.pdf \\
    --project pnkln-core-gke

  # Test query
  python corpus_import.py --vertical defense \\
    --query "What are ITAR export control requirements?" \\
    --project pnkln-core-gke
        """,
    )

    parser.add_argument("--project", default="pnkln-core-gke", help="GCP project ID")
    parser.add_argument("--region", default="us-central1", help="GCP region")
    parser.add_argument("--vertical", help="Vertical name (e.g., defense, healthcare)")
    parser.add_argument("--path", help="GCS path to files (gs://bucket/path/*.pdf)")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Document chunk size (default: 512)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Chunk overlap (default: 100)",
    )
    parser.add_argument("--list-corpora", action="store_true", help="List all available corpora")
    parser.add_argument("--query", help="Test query against corpus")
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results for query (default: 5)",
    )

    args = parser.parse_args()

    # List corpora
    if args.list_corpora:
        list_corpora(args.project, args.region)
        return

    # Test query
    if args.query:
        if not args.vertical:
            parser.error("--vertical required for --query")
        query_corpus(args.project, args.region, args.vertical, args.query, args.top_k)
        return

    # Import files
    if not args.vertical or not args.path:
        parser.error("--vertical and --path required for import")

    import_files(
        args.project,
        args.region,
        args.vertical,
        args.path,
        args.chunk_size,
        args.chunk_overlap,
    )


if __name__ == "__main__":
    main()
