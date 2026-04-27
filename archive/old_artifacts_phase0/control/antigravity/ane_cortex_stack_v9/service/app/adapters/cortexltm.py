from ..utils.db import pg_conn


def create_thread(dsn: str, user_id: str, title: str | None = None) -> str:
    with pg_conn(dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ltm_threads (user_id, title) VALUES (%s::uuid, %s) RETURNING id",
            (user_id, title),
        )
        return str(cur.fetchone()[0])


def add_event(
    dsn: str,
    thread_id: str,
    actor: str,
    content: str,
    meta_json: str = "{}",
    importance_score: int = 0,
):
    with pg_conn(dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ltm_events (thread_id, actor, content, meta, importance_score) VALUES (%s::uuid, %s, %s, %s::jsonb, %s) RETURNING id",
            (thread_id, actor, content, meta_json, importance_score),
        )
        return str(cur.fetchone()[0])


def get_recent_events(dsn: str, thread_id: str, limit: int = 20):
    with pg_conn(dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, actor, content FROM ltm_events WHERE thread_id = %s::uuid ORDER BY created_at DESC LIMIT %s",
            (thread_id, limit),
        )
        return [{"id": str(r[0]), "actor": r[1], "content": r[2]} for r in cur.fetchall()]


def write_summary(dsn: str, thread_id: str, summary: str, meta_json: str = "{}"):
    with pg_conn(dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE ltm_thread_summaries SET is_active = false WHERE thread_id = %s::uuid AND is_active = true",
            (thread_id,),
        )
        cur.execute(
            "INSERT INTO ltm_thread_summaries (thread_id, summary, meta, is_active) VALUES (%s::uuid, %s, %s::jsonb, true) RETURNING id",
            (thread_id, summary, meta_json),
        )
        return str(cur.fetchone()[0])


def upsert_master_memory(dsn: str, user_id: str, bucket: str, content: str, meta_json: str = "{}"):
    with pg_conn(dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ltm_master_items (user_id, bucket, content, meta) VALUES (%s::uuid, %s, %s, %s::jsonb) RETURNING id",
            (user_id, bucket, content, meta_json),
        )
        return str(cur.fetchone()[0])
