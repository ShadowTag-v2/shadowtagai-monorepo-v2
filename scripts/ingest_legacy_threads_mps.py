import os
import sys

from sentence_transformers import SentenceTransformer

# Ensure the monorepo root is in the absolute Python path
sys.path.append(os.path.abspath("."))
from rag_engine.memory_service import SequentialMemoryService

# The explicitly requested threads that have been copied into our monorepo or mapped
TARGET_THREADS = [
    os.path.abspath("tools/legacy/vscode_backups/molten-universe"),
    os.path.abspath("tools/legacy/vscode_backups/deep-aurora"),
    os.path.abspath("tools/legacy/ShadowTag.code-workspace"),
    os.path.abspath("tools/legacy/ShadowTag-v2.code-workspace"),
    os.path.abspath("drive_knowledge/documents"),
    os.path.abspath("docs/legacy_shadowtag_v2"),
]


def get_files_recursively(directory):
    """Pickle Rick: Ruthlessly hunt down every file in the directory structure."""
    if not os.path.exists(directory):
        print(f"⚠️ [Pickle Rick Warning]: Target missing {directory}")
        return []

    if os.path.isfile(directory):
        return [directory]

    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            # Skip obvious binaries or massive git folders
            if ".git" in root or ".venv" in root or "__pycache__" in root:
                continue
            if not file.endswith((".md", ".json", ".txt", ".py", ".ts", ".code-workspace", ".csv")):
                continue
            file_paths.append(os.path.join(root, file))
    return file_paths


def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    """Slice data like a scalpel."""
    chunks = []
    paragraphs = text.split("\n\n")
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return [c for c in chunks if c.strip()]


def execute_ingestion():
    print("🥒 [PICKLE RICK PROTOCOL] Initiating...")
    print("⚡ Utilizing Apple Silicon ANE (mps) for ruthless vector math acceleration.")

    # Force MPS on Apple Silicon
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2", device="mps")
        print("✅ MPS Backend Activated.")
    except Exception as e:
        print(f"⚠️ Could not load MPS backend, falling back to CPU. ({e})")
        model = SentenceTransformer("all-MiniLM-L6-v2")

    def local_embed_fn(text: str):
        return model.encode(text).tolist()

    memory = SequentialMemoryService(embed_fn=local_embed_fn)

    total_files_ingested = 0
    total_chunks = 0

    for thread in TARGET_THREADS:
        print(f"\n🔍 Sweeping Thread: {thread}")
        files = get_files_recursively(thread)
        print(f"   => Found {len(files)} target files.")

        for file in files:
            try:
                with open(file, encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                # Silently skip unreadable files (ruthless efficiency)
                continue

            chunks = chunk_text(content)
            events = []
            for chunk in chunks:
                events.append({"text": chunk, "timestamp": "legacy_ingest", "node_type": "legacy_thread_docs"})

            # Persist to Chroma via Memory Service (using the file path as timeline_id to keep it scoped or global)
            memory.persist_traversal(timeline_id="global_monorepo", events=events)
            total_chunks += len(chunks)
            total_files_ingested += 1

    print("\n================================================")
    print("🥒 PICKLE RICK RUTHLESS ANE MERGE COMPLETE 🥒")
    print(f"Total Threads Processed : {len(TARGET_THREADS)}")
    print(f"Total Files Ingested    : {total_files_ingested}")
    print(f"Total Vector Chunks     : {total_chunks}")
    print("Vector Graph Updated. The intelligence is now ONE.")
    print("================================================")


if __name__ == "__main__":
    execute_ingestion()
