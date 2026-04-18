"""Example usage of the embeddings and semantic search API."""

import asyncio

import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def generate_single_embedding():
    """Generate embedding for a single text."""
    print("\n=== Single Embedding Example ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/embeddings/generate",
            json={"text": "FastAPI is a modern web framework for building APIs"},
            timeout=30.0,
        )

        result = response.json()
        print(f"Embedding dimension: {result['dimension']}")
        print(f"Model: {result['model']}")
        print(f"First 5 values: {result['embedding'][:5]}")


async def generate_batch_embeddings():
    """Generate embeddings for multiple texts."""
    print("\n=== Batch Embeddings Example ===")

    texts = [
        "Python is a programming language",
        "JavaScript is used for web development",
        "Machine learning uses neural networks",
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/embeddings/generate",
            json={"texts": texts},
            timeout=30.0,
        )

        result = response.json()
        print(f"Generated {len(result['embeddings'])} embeddings")
        print(f"Dimension: {result['dimension']}")


async def create_document_collection():
    """Create a collection and add documents."""
    print("\n=== Document Collection Example ===")

    collection_name = "tech_docs"

    async with httpx.AsyncClient() as client:
        # Create collection
        create_response = await client.post(
            f"{BASE_URL}/embeddings/collections/{collection_name}",
            json={"metadata": {"type": "technical_documentation"}},
        )
        print(f"Collection created: {create_response.json()}")

        # Add documents
        documents = [
            "FastAPI is a modern, fast web framework for building APIs with Python 3.7+",
            "React is a JavaScript library for building user interfaces",
            "Docker is a platform for developing, shipping, and running applications in containers",
            "PostgreSQL is a powerful, open source object-relational database system",
            "Redis is an in-memory data structure store used as a database and cache",
        ]

        metadata = [
            {"category": "web_framework", "language": "python"},
            {"category": "frontend", "language": "javascript"},
            {"category": "devops", "language": "go"},
            {"category": "database", "language": "c"},
            {"category": "database", "language": "c"},
        ]

        add_response = await client.post(
            f"{BASE_URL}/embeddings/collections/{collection_name}/documents",
            json={"collection_name": collection_name, "documents": documents, "metadata": metadata},
            timeout=60.0,
        )

        print(f"Added {add_response.json()['count']} documents to collection")

        return collection_name


async def semantic_search(collection_name: str):
    """Perform semantic search on a collection."""
    print("\n=== Semantic Search Example ===")

    queries = ["web development frameworks", "container technology", "data storage solutions"]

    async with httpx.AsyncClient() as client:
        for query in queries:
            print(f"\nQuery: '{query}'")

            response = await client.post(
                f"{BASE_URL}/embeddings/search",
                json={"collection_name": collection_name, "query": query, "n_results": 2},
                timeout=30.0,
            )

            results = response.json()

            for i, (doc, distance, meta) in enumerate(
                zip(results["documents"], results["distances"], results["metadata"], strict=False),
                1,
            ):
                print(f"  {i}. {doc[:80]}...")
                print(f"     Distance: {distance:.4f}")
                print(f"     Category: {meta.get('category', 'N/A')}")


async def filtered_search(collection_name: str):
    """Search with metadata filtering."""
    print("\n=== Filtered Search Example ===")

    async with httpx.AsyncClient() as client:
        # Search only in database category
        response = await client.post(
            f"{BASE_URL}/embeddings/search",
            json={
                "collection_name": collection_name,
                "query": "fast storage",
                "n_results": 3,
                "where": {"category": "database"},
            },
            timeout=30.0,
        )

        results = response.json()
        print(f"Found {len(results['documents'])} database-related results")

        for doc, meta in zip(results["documents"], results["metadata"], strict=False):
            print(f"  - {doc[:80]}...")
            print(f"    Language: {meta.get('language', 'N/A')}")


async def list_and_manage_collections():
    """List and manage collections."""
    print("\n=== Collection Management ===")

    async with httpx.AsyncClient() as client:
        # List all collections
        list_response = await client.get(f"{BASE_URL}/embeddings/collections")
        collections = list_response.json()

        print(f"Total collections: {collections['count']}")
        print(f"Collections: {collections['collections']}")


async def main():
    """Run all examples."""
    try:
        # Generate embeddings
        await generate_single_embedding()
        await generate_batch_embeddings()

        # Create collection and add documents
        collection_name = await create_document_collection()

        # Perform searches
        await semantic_search(collection_name)
        await filtered_search(collection_name)

        # Manage collections
        await list_and_manage_collections()

        print("\n✅ All embeddings examples completed successfully!")

    except httpx.ConnectError:
        print("❌ Error: Could not connect to the API server.")
        print("   Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
