from __future__ import annotations
from ..config import load_settings
from ..utils.db import sqlite_conn, pg_conn
from ..retrieval.sqlite_index import chunk_text
from ..retrieval.lancedb_store import upsert_chunks


def mark_changed_files(sqlite_db: str, pg_dsn: str, repo_id: str):
    with sqlite_conn(sqlite_db) as sconn, pg_conn(pg_dsn) as pconn:
        srows = sconn.execute("SELECT doc_id, rel_path, sha256 FROM documents").fetchall()
        cur = pconn.cursor()
        changed = []
        for doc_id, rel_path, sha256 in srows:
            cur.execute("SELECT sha256 FROM changed_files_state WHERE doc_id = %s", (doc_id,))
            row = cur.fetchone()
            if row is None or row[0] != sha256:
                changed.append(doc_id)
                cur.execute(
                    "INSERT INTO changed_files_state (doc_id, repo_id, rel_path, sha256, embedding_status) VALUES (%s, %s, %s, %s, 'pending') ON CONFLICT (doc_id) DO UPDATE SET rel_path = EXCLUDED.rel_path, sha256 = EXCLUDED.sha256, embedding_status = 'pending'",
                    (doc_id, repo_id, rel_path, sha256),
                )
        return {"changed_doc_ids": changed, "count": len(changed)}


def embed_only_changed():
    s = load_settings()
    change_info = mark_changed_files(s.sqlite_db, s.postgres_dsn, s.repo_id)
    changed = set(change_info["changed_doc_ids"])
    chunks = [c for c in chunk_text(s.sqlite_db) if c["doc_id"] in changed]
    result = upsert_chunks(s.lancedb_root, chunks)
    with pg_conn(s.postgres_dsn) as conn:
        cur = conn.cursor()
        for doc_id in changed:
            cur.execute(
                "UPDATE changed_files_state SET embedding_status = 'done', last_embedded_at = now() WHERE doc_id = %s",
                (doc_id,),
            )
    return {"changed": change_info, "upsert": result}


if __name__ == "__main__":
    print(embed_only_changed())
