#!/usr/bin/env python3
"""
Merge Google Drive Knowledge with Memory System

Integrates extracted Drive content into the memory/knowledge system
alongside conversation data.

USAGE:
    python scripts/merge_drive_knowledge.py

This will:
1. Load drive_knowledge/index.json
2. Load all extracted documents
3. Create knowledge entries in memory format
4. Merge with existing memory/current.json
5. Generate updated memory snapshot
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Paths
DRIVE_KNOWLEDGE_DIR = Path(__file__).parent.parent / "drive_knowledge"
MEMORY_DIR = Path(__file__).parent.parent / "memory"
CURRENT_MEMORY = MEMORY_DIR / "current.json"


def load_drive_index() -> dict:
    """Load Google Drive extraction index."""
    index_file = DRIVE_KNOWLEDGE_DIR / "index.json"

    if not index_file.exists():
        print("❌ No Google Drive index found!")
        print("   Run: python scripts/extract_google_drive.py")
        sys.exit(1)

    with open(index_file) as f:
        return json.load(f)


def load_extracted_documents() -> list[dict]:
    """Load all extracted documents and metadata."""
    print("\n📖 Loading extracted documents...")

    docs_dir = DRIVE_KNOWLEDGE_DIR / "documents"
    metadata_dir = DRIVE_KNOWLEDGE_DIR / "metadata"
    embeddings_dir = DRIVE_KNOWLEDGE_DIR / "embeddings"

    documents = []

    for metadata_file in metadata_dir.glob("*.json"):
        file_hash = metadata_file.stem

        # Load metadata
        with open(metadata_file) as f:
            metadata = json.load(f)

        # Load document text
        doc_file = docs_dir / f"{file_hash}.txt"
        if not doc_file.exists():
            continue

        with open(doc_file) as f:
            text = f.read()

        # Load embedding if exists
        embedding = None
        embedding_file = embeddings_dir / f"{file_hash}.json"
        if embedding_file.exists():
            with open(embedding_file) as f:
                embedding = json.load(f)["embedding"]

        # Create document entry
        documents.append({"hash": file_hash, "metadata": metadata, "text": text, "embedding": embedding})

    print(f"   Loaded {len(documents)} documents")
    return documents


def convert_to_knowledge_entries(documents: list[dict]) -> list[dict]:
    """Convert Drive documents to knowledge entry format."""
    print("\n🔄 Converting to knowledge entries...")

    knowledge_entries = []

    for doc in documents:
        metadata = doc["metadata"]

        # Create knowledge entry
        entry = {
            "id": f"drive_{doc['hash']}",
            "source": "google-drive",
            "type": metadata["file_type"],
            "title": metadata["name"],
            "content": doc["text"],
            "created_at": metadata.get("created"),
            "modified_at": metadata.get("modified"),
            "metadata": {
                "drive_id": metadata["id"],
                "mime_type": metadata["mime_type"],
                "size": metadata["size"],
                "owners": metadata.get("owners", []),
                "web_link": metadata.get("web_link"),
                "word_count": metadata["word_count"],
                "text_length": metadata["text_length"],
            },
            "embedding": doc["embedding"],
            "tags": extract_tags(metadata["name"], doc["text"]),
            "indexed_at": datetime.now().isoformat(),
        }

        knowledge_entries.append(entry)

    print(f"   Created {len(knowledge_entries)} knowledge entries")
    return knowledge_entries


def extract_tags(filename: str, text: str) -> list[str]:
    """Extract relevant tags from filename and content."""
    tags = []

    # File type tags
    if filename.endswith(".pdf"):
        tags.append("pdf")
    elif filename.endswith((".epub", ".mobi")):
        tags.append("ebook")
    elif filename.endswith(".zip"):
        tags.append("archive")

    # Content-based tags (simple keyword matching)
    keywords = {
        "shadowtagai": ["shadowtagai", "kernel", "orchestration"],
        "judge": ["judge", "compliance", "governance"],
        "python": ["python", "def ", "import "],
        "typescript": ["typescript", "interface", "type "],
        "documentation": ["readme", "guide", "documentation"],
        "research": ["research", "paper", "study"],
        "code": ["function", "class", "method"],
    }

    text_lower = text.lower()[:5000]  # First 5k chars for tag extraction

    for tag, patterns in keywords.items():
        if any(pattern in text_lower for pattern in patterns):
            tags.append(tag)

    return list(set(tags))  # Deduplicate


def load_existing_memory() -> dict:
    """Load existing memory from current.json."""
    if not CURRENT_MEMORY.exists():
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "conversations": [],
            "knowledge": [],
            "shadowtagai_architecture": {},
            "llm_allocation": {},
            "jr_framework": {},
        }

    with open(CURRENT_MEMORY) as f:
        return json.load(f)


def merge_knowledge(existing: list[dict], new: list[dict]) -> list[dict]:
    """Merge new knowledge entries with existing."""
    print("\n🔀 Merging knowledge entries...")

    # Build index of existing entry IDs
    existing_ids = {entry["id"] for entry in existing}

    # Add only new entries
    added = 0
    for entry in new:
        if entry["id"] not in existing_ids:
            existing.append(entry)
            added += 1

    print(f"   Existing: {len(existing_ids)}")
    print(f"   New: {len(new)}")
    print(f"   Added: {added}")
    print(f"   Total: {len(existing)}")

    return existing


def save_updated_memory(memory: dict):
    """Save updated memory to current.json and create snapshot."""
    print("\n💾 Saving updated memory...")

    # Update timestamp
    memory["last_updated"] = datetime.now().isoformat()

    # Save to current.json
    with open(CURRENT_MEMORY, "w") as f:
        json.dump(memory, f, indent=2)

    print(f"   ✓ Saved to {CURRENT_MEMORY}")

    # Create snapshot
    snapshots_dir = MEMORY_DIR / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)

    snapshot_file = snapshots_dir / f"memory_drive_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(snapshot_file, "w") as f:
        json.dump(memory, f, indent=2)

    print(f"   ✓ Created snapshot: {snapshot_file.name}")


def generate_statistics(memory: dict):
    """Generate and print statistics."""
    print("\n" + "=" * 60)
    print("📊 Knowledge Base Statistics")
    print("=" * 60)

    knowledge = memory.get("knowledge", [])

    # Total entries
    print(f"   Total knowledge entries: {len(knowledge)}")

    # By source
    sources = {}
    for entry in knowledge:
        source = entry["source"]
        sources[source] = sources.get(source, 0) + 1

    print("\n   By source:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"      {source}: {count}")

    # By type
    types = {}
    for entry in knowledge:
        entry_type = entry["type"]
        types[entry_type] = types.get(entry_type, 0) + 1

    print("\n   By type:")
    for entry_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"      {entry_type}: {count}")

    # Total words
    total_words = sum(entry["metadata"].get("word_count", 0) for entry in knowledge)
    print(f"\n   Total words: {total_words:,}")

    # With embeddings
    with_embeddings = sum(1 for entry in knowledge if entry.get("embedding"))
    print(f"   With embeddings: {with_embeddings} ({with_embeddings / len(knowledge) * 100:.1f}%)")


def main():
    """Main execution flow."""
    print("=" * 60)
    print("Google Drive Knowledge Merger v1.0")
    print("=" * 60)

    # 1. Load Drive index
    print("\n📋 Loading Google Drive index...")
    index = load_drive_index()
    print(f"   Files extracted: {index['processed']}")
    print(f"   Total words: {sum(f['word_count'] for f in index['files']):,}")

    # 2. Load extracted documents
    documents = load_extracted_documents()

    # 3. Convert to knowledge entries
    knowledge_entries = convert_to_knowledge_entries(documents)

    # 4. Load existing memory
    print("\n📖 Loading existing memory...")
    memory = load_existing_memory()
    print(f"   Current conversations: {len(memory.get('conversations', []))}")
    print(f"   Current knowledge: {len(memory.get('knowledge', []))}")

    # 5. Merge knowledge
    if "knowledge" not in memory:
        memory["knowledge"] = []

    memory["knowledge"] = merge_knowledge(memory.get("knowledge", []), knowledge_entries)

    # 6. Save
    save_updated_memory(memory)

    # 7. Statistics
    generate_statistics(memory)

    # 8. Summary
    print("\n" + "=" * 60)
    print("✅ Merge Complete!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print(f"   1. Review {CURRENT_MEMORY}")
    print("   2. Deploy to Claude Code: python scripts/claude_code_memory_local.py")
    print("   3. Use semantic search with embeddings (if generated)")


if __name__ == "__main__":
    main()
