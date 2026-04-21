"""Step 2 — Codebase Embedder.

Embeds every .py / .go / .ts file in the monorepo using CodeChunker →
Vertex AI text-embedding-005 → LanceDB::code_files table.

Skips: node_modules, archive, third_party, .venv, __pycache__, build, dist
Resumes: tracks state in data/intelligence_pipeline/embedder_state.json
Runtime: ~3 hours for full monorepo (incremental is fast)
"""

import json
import logging
import os
import time
from pathlib import Path

import google.auth
import google.auth.transport.requests
import lancedb
import pyarrow as pa

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
STATE_PATH = REPO_ROOT / "data" / "intelligence_pipeline" / "embedder_state.json"
LANCEDB_DIR = REPO_ROOT / "data" / "lancedb"

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "shadowtag-omega-v4")
REGION = "us-central1"
EMBED_MODEL = "text-embedding-005"
EMBED_ENDPOINT = (
    f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT_ID}/locations/{REGION}/publishers/google/models/{EMBED_MODEL}:predict"
)

EXCLUDED_DIRS = {
    "node_modules",
    "archive",
    "third_party",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "bazel-out",
    ".git",
    ".gitnexus",
    "external_repos",
    "external_sdks",
    "reference_architectures",
    "deep-archive",
}
INCLUDED_EXTENSIONS = {".py", ".go", ".ts", ".tsx", ".js", ".jsx"}
MAX_CHUNK_SIZE = 2000  # characters per chunk


def get_access_token() -> str:
    """Get GCP access token via ADC."""
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def embed_batch(texts: list[str], token: str) -> list[list[float]]:
    """Embed a batch of text chunks via Vertex AI."""
    import requests

    payload = {
        "instances": [{"content": t[: EMBED_MODEL and 3000]} for t in texts],
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(EMBED_ENDPOINT, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    predictions = resp.json().get("predictions", [])
    return [p["embeddings"]["values"] for p in predictions]


def _should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from embedding."""
    parts = set(path.parts)
    return bool(parts & EXCLUDED_DIRS)


def collect_source_files() -> list[Path]:
    """Collect all source files eligible for embedding."""
    files = []
    for ext in INCLUDED_EXTENSIONS:
        for f in REPO_ROOT.rglob(f"*{ext}"):
            if not _should_exclude(f.relative_to(REPO_ROOT)):
                files.append(f)
    logger.info(f"Collected {len(files)} source files")
    return files


def load_state() -> dict:
    """Load embedder state (already-processed files)."""
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"processed": {}, "last_run": None}


def save_state(state: dict) -> None:
    """Save embedder state."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def get_or_create_code_table(db) -> object:
    """Get or create the code_files table in LanceDB."""
    schema = pa.schema(
        [
            pa.field("file_path", pa.string()),
            pa.field("chunk_index", pa.int32()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 768)),
        ],
    )
    if "code_files" in db.table_names():
        return db.open_table("code_files")
    return db.create_table("code_files", schema=schema)


def run_codebase_embedder(cfg=None) -> dict:
    """Execute Step 2: Codebase Embedder."""
    logger.info("Codebase Embedder — Step 2")

    db = lancedb.connect(str(LANCEDB_DIR))
    tbl = get_or_create_code_table(db)
    state = load_state()
    processed = state.get("processed", {})
    files = collect_source_files()

    # Filter already-processed
    new_files = [f for f in files if str(f) not in processed]
    logger.info(f"New files to embed: {len(new_files)} (already done: {len(processed)})")

    if cfg and cfg.dry_run:
        return {"new_files": len(new_files), "already_done": len(processed)}

    token = get_access_token()
    embedded_count = 0
    batch_texts = []
    batch_meta = []

    for fpath in new_files:
        try:
            content = fpath.read_text(errors="replace")
        except Exception:
            continue

        # Chunk the file
        chunks = [content[i : i + MAX_CHUNK_SIZE] for i in range(0, len(content), MAX_CHUNK_SIZE)]
        for idx, chunk in enumerate(chunks):
            batch_texts.append(chunk)
            batch_meta.append({"file_path": str(fpath.relative_to(REPO_ROOT)), "chunk_index": idx, "text": chunk})

            if len(batch_texts) >= 5:
                try:
                    vectors = embed_batch(batch_texts, token)
                    rows = [{**m, "vector": v} for m, v in zip(batch_meta, vectors, strict=False)]
                    tbl.add(rows)
                    embedded_count += len(rows)
                except Exception as e:
                    logger.warning(f"Embed batch failed: {e}")
                batch_texts.clear()
                batch_meta.clear()
                time.sleep(0.5)

        processed[str(fpath)] = True

    # Flush remaining
    if batch_texts:
        try:
            vectors = embed_batch(batch_texts, token)
            rows = [{**m, "vector": v} for m, v in zip(batch_meta, vectors, strict=False)]
            tbl.add(rows)
            embedded_count += len(rows)
        except Exception as e:
            logger.warning(f"Final batch failed: {e}")

    state["processed"] = processed
    state["last_run"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_state(state)

    stats = {"embedded_chunks": embedded_count, "total_files": len(files)}
    logger.info(f"Codebase Embedder complete: {stats}")
    return stats


if __name__ == "__main__":
    run_codebase_embedder()
