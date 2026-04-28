# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json

from ..utils.db import pg_conn, sqlite_conn


def sync_doc_registry(sqlite_db: str, pg_dsn: str, repo_id: str):
    with sqlite_conn(sqlite_db) as sconn, pg_conn(pg_dsn) as pconn:
        srows = sconn.execute("SELECT doc_id, rel_path, kind, sha256 FROM documents").fetchall()
        cur = pconn.cursor()
        cur.execute(
            "INSERT INTO repos (repo_id, name, repo_root, default_branch) VALUES (%s, %s, %s, %s) ON CONFLICT (repo_id) DO NOTHING",
            (repo_id, repo_id.upper(), "./external_repos/ANE", "main"),
        )
        count = 0
        for doc_id, rel_path, kind, sha256 in srows:
            cur.execute(
                "INSERT INTO doc_registry (doc_id, repo_id, rel_path, canonical_kind, sha256) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (doc_id) DO UPDATE SET rel_path=EXCLUDED.rel_path, canonical_kind=EXCLUDED.canonical_kind, sha256=EXCLUDED.sha256, updated_at=now()",
                (doc_id, repo_id, rel_path, kind, sha256),
            )
            count += 1
    return {"synced_doc_registry": count}


def mirror_beads_tasks(pg_dsn: str, repo_id: str, tasks: list[dict]):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        count = 0
        for t in tasks:
            cur.execute(
                "INSERT INTO beads_tasks (bead_id, repo_id, title, status, priority, assignee, parent_bead_id, depends_on, summary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s) ON CONFLICT (bead_id) DO UPDATE SET title=EXCLUDED.title, status=EXCLUDED.status, priority=EXCLUDED.priority, assignee=EXCLUDED.assignee, parent_bead_id=EXCLUDED.parent_bead_id, depends_on=EXCLUDED.depends_on, summary=EXCLUDED.summary, updated_at=now()",
                (
                    t["bead_id"],
                    repo_id,
                    t["title"],
                    t.get("status", "open"),
                    t.get("priority"),
                    t.get("assignee"),
                    t.get("parent_bead_id"),
                    json.dumps(t.get("depends_on", [])),
                    t.get("summary"),
                ),
            )
            count += 1
    return {"mirrored_beads_tasks": count}
