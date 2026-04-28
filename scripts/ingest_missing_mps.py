# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

from sentence_transformers import SentenceTransformer

# Ensure the monorepo root is in the absolute Python path
sys.path.append(os.path.abspath("."))
from rag_engine.memory_service import SequentialMemoryService

TARGET_THREADS = [
    os.path.abspath("tools/legacy/vscode_backups/molten-universe"),
    os.path.abspath("tools/legacy/vscode_backups/deep-aurora"),
]


def get_files_recursively(directory):
    if not os.path.exists(directory):
        return []
    if os.path.isfile(directory):
        return [directory]
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if ".git" in root or ".venv" in root or "__pycache__" in root:
                continue
            if not file.endswith((".md", ".json", ".txt", ".py", ".ts", ".code-workspace", ".csv")):
                continue
            file_paths.append(os.path.join(root, file))
    return file_paths


def chunk_text(text: str, chunk_size: int = 1000):
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


def execute_ingestion() -> None:
    # Force MPS on Apple Silicon
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2", device="mps")
    except Exception:
        model = SentenceTransformer("all-MiniLM-L6-v2")

    def local_embed_fn(text: str):
        return model.encode(text).tolist()

    memory = SequentialMemoryService(embed_fn=local_embed_fn)

    total_files = 0
    total_chunks = 0

    for thread in TARGET_THREADS:
        files = get_files_recursively(thread)

        for file in files:
            try:
                with open(file, encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            chunks = chunk_text(content)
            events = [
                {
                    "text": chunk,
                    "timestamp": "legacy_ingest_patch",
                    "node_type": "legacy_thread_docs",
                }
                for chunk in chunks
            ]
            memory.persist_traversal(timeline_id="global_monorepo", events=events)
            total_chunks += len(chunks)
            total_files += 1


if __name__ == "__main__":
    execute_ingestion()
