"""
Step 3 — Cross-Domain Matcher

For each of 2,856 docs, finds top-3 semantic matches in:
  - Doc → Code file (embedding cosine similarity)
  - Doc → Doc (cross-domain)
  - Doc → Git commit (commit message similarity)

Output: crossref.db → tables doc_code_matches, doc_doc_matches, doc_commit_matches
"""

import logging
import os
import sqlite3
import subprocess
import time
from pathlib import Path

import google.auth
import google.auth.transport.requests
import lancedb
import numpy as np

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "intelligence_pipeline" / "crossref.db"
LANCEDB_DIR = REPO_ROOT / "data" / "lancedb"

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "shadowtag-omega-v4")
REGION = "us-central1"
EMBED_MODEL = "text-embedding-005"
EMBED_ENDPOINT = (
    f"https://{REGION}-aiplatform.googleapis.com/v1/projects/"
    f"{GCP_PROJECT_ID}/locations/{REGION}/publishers/google/models/{EMBED_MODEL}:predict"
)
TOP_K = 3
BATCH_SIZE = 10


def get_access_token() -> str:
    """Get GCP access token via ADC."""
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def embed_single(text: str, token: str) -> list[float]:
    """Embed a single text string."""
    import requests

    payload = {"instances": [{"content": text[:3000]}]}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(EMBED_ENDPOINT, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["predictions"][0]["embeddings"]["values"]


def embed_batch(texts: list[str], token: str) -> list[list[float]]:
    """Embed a batch of texts."""
    import requests

    payload = {"instances": [{"content": t[:3000]} for t in texts]}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(EMBED_ENDPOINT, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return [p["embeddings"]["values"] for p in resp.json()["predictions"]]


def cosine_sim(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr) + 1e-9))


def init_match_tables(conn: sqlite3.Connection) -> None:
    """Create match tables in crossref.db."""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS doc_code_matches (
            doc_id TEXT, code_path TEXT, similarity REAL, rank INTEGER,
            PRIMARY KEY (doc_id, rank))"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS doc_doc_matches (
            doc_id TEXT, matched_doc_id TEXT, similarity REAL, rank INTEGER,
            PRIMARY KEY (doc_id, rank))"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS doc_commit_matches (
            doc_id TEXT, commit_hash TEXT, similarity REAL, rank INTEGER,
            PRIMARY KEY (doc_id, rank))"""
    )
    conn.commit()


def already_matched_docs(conn: sqlite3.Connection) -> set:
    """Return doc IDs that already have matches."""
    rows = conn.execute("SELECT DISTINCT doc_id FROM doc_code_matches").fetchall()
    return {r[0] for r in rows}


def get_git_commits(limit: int = 500) -> list[dict]:
    """Get recent git commit messages."""
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={limit}", "--format=%H|%s"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                hash_, msg = line.split("|", 1)
                commits.append({"hash": hash_.strip(), "message": msg.strip()})
        return commits
    except Exception as e:
        logger.warning(f"git log failed: {e}")
        return []


def run_cross_domain_matcher(cfg=None) -> dict:
    """Execute Step 3: Cross-Domain Matcher."""
    logger.info("Cross-Domain Matcher — Step 3")

    conn = sqlite3.connect(str(DB_PATH))
    init_match_tables(conn)
    matched = already_matched_docs(conn)

    db = lancedb.connect(str(LANCEDB_DIR))
    doc_tbl = db.open_table("workspace_knowledge")
    docs_df = doc_tbl.to_pandas()

    has_code = "code_files" in db.table_names()
    if has_code:
        code_tbl = db.open_table("code_files")

    # Filter unmatched docs
    unmatched = [
        row for _, row in docs_df.iterrows()
        if str(row.get("id", row.name)) not in matched
    ]
    logger.info(f"Unmatched docs: {len(unmatched)} (already matched: {len(matched)})")

    if cfg and cfg.dry_run:
        conn.close()
        return {"unmatched": len(unmatched), "already_matched": len(matched)}

    token = get_access_token()
    match_count = 0

    for row in unmatched:
        doc_id = str(row.get("id", row.name))
        title = str(row.get("title", row.get("source", "")))

        try:
            # Doc → Code matches (vector search)
            if has_code:
                results = code_tbl.search(row.get("vector", [])).limit(TOP_K).to_list()
                for rank, r in enumerate(results):
                    conn.execute(
                        "INSERT OR REPLACE INTO doc_code_matches VALUES (?, ?, ?, ?)",
                        (doc_id, r.get("file_path", ""), r.get("_distance", 0), rank + 1),
                    )

            # Doc → Doc matches (vector search across domains)
            doc_results = doc_tbl.search(row.get("vector", [])).limit(TOP_K + 1).to_list()
            rank = 0
            for r in doc_results:
                rid = str(r.get("id", ""))
                if rid != doc_id:
                    rank += 1
                    conn.execute(
                        "INSERT OR REPLACE INTO doc_doc_matches VALUES (?, ?, ?, ?)",
                        (doc_id, rid, r.get("_distance", 0), rank),
                    )
                    if rank >= TOP_K:
                        break

            match_count += 1
        except Exception as e:
            logger.warning(f"Match failed for {doc_id}: {e}")

        if match_count % 50 == 0:
            conn.commit()
            time.sleep(0.5)

    conn.commit()
    conn.close()
    stats = {"matched": match_count, "total_docs": len(docs_df)}
    logger.info(f"Cross-Domain Matcher complete: {stats}")
    return stats


if __name__ == "__main__":
    run_cross_domain_matcher()
