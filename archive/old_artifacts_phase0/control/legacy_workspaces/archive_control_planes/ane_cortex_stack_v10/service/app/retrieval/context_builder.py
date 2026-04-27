from ..adapters.authority_state import AuthorityState
from ..adapters.json_memory import JsonMemoryStore
from ..adapters.memory_atoms import search_atoms
from ..utils.db import pg_conn
from .lancedb_store import search as semantic_search
from .sqlite_index import exact_search


def memory_search(pg_dsn: str, repo_id: str, limit: int = 6):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT subject, summary, memory_kind FROM semantic_memories WHERE repo_id = %s ORDER BY created_at DESC LIMIT %s", (repo_id, limit)
        )
        return [{"title": r[0], "content": r[1], "kind": r[2], "source": "postgres"} for r in cur.fetchall()]


def json_memory_search(query: str, limit: int = 6):
    store = JsonMemoryStore()
    rows = store.search(query, limit)
    return [
        {"title": r.get("subject", ""), "content": r.get("summary") or r.get("body", ""), "kind": r.get("type", "memory"), "source": "jsonl"}
        for r in rows
    ]


def task_search(pg_dsn: str, repo_id: str, limit: int = 6):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute("SELECT bead_id, title, status, summary FROM beads_tasks WHERE repo_id = %s ORDER BY updated_at DESC LIMIT %s", (repo_id, limit))
        return [{"id": r[0], "title": r[1], "status": r[2], "summary": r[3] or ""} for r in cur.fetchall()]


def build_prompt_context(query: str, authority, atoms, exact, semantic, memory, tasks):
    parts = [f"USER QUERY:\n{query}\n"]
    parts.append("AUTHORITY MEMORY (CANONICAL):")
    parts.append(str(authority))
    if atoms:
        parts.append("AUTHORITY ATOMS:")
        for a in atoms:
            parts.append(f"- [{a['atom_kind']}] {a['subject']} :: {a['predicate']} = {a['object_text']} (score={a['score']})")
    if exact:
        parts.append("EXACT HITS:")
        for r in exact:
            parts.append(f"- {r['rel_path']}: {r['body']}")
    if semantic:
        parts.append("SEMANTIC HITS:")
        for r in semantic:
            parts.append(f"- {r.get('rel_path','')}: {str(r.get('content',''))[:500]}")
    if memory:
        parts.append("MEMORY:")
        for r in memory:
            parts.append(f"- ({r.get('source','memory')}) {r['title']}: {r['content']}")
    if tasks:
        parts.append("TASKS:")
        for r in tasks:
            parts.append(f"- {r['id']} [{r['status']}] {r['title']}: {r['summary']}")
    parts.append("RULE: If codebase conflicts with AUTHORITY MEMORY or AUTHORITY ATOMS, update the codebase and preserve memory authority.")
    return "\n".join(parts)


def collect_context(sqlite_db: str, lancedb_root: str, pg_dsn: str, repo_id: str, query: str, authority_state_path: str, limit: int = 8):
    authority = AuthorityState(authority_state_path).read()
    atoms = search_atoms(pg_dsn, repo_id, query, limit=10)
    exact = exact_search(sqlite_db, query, limit)
    semantic = semantic_search(lancedb_root, query, limit)
    memory = memory_search(pg_dsn, repo_id, min(limit, 6)) + json_memory_search(query, min(limit, 4))
    tasks = task_search(pg_dsn, repo_id, min(limit, 6))
    prompt_context = build_prompt_context(query, authority, atoms, exact, semantic, memory, tasks)
    selected_ids = {
        "atoms": [a["id"] for a in atoms],
        "exact": [r["doc_id"] for r in exact],
        "semantic": [str(r.get("chunk_id")) for r in semantic],
        "memory": [r["title"] for r in memory],
        "tasks": [r["id"] for r in tasks],
    }
    return exact, semantic, memory, tasks, prompt_context, selected_ids
