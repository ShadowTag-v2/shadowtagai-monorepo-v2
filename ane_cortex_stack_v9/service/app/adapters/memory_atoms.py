from __future__ import annotations
from typing import List, Dict, Any
from ..utils.db import pg_conn

def insert_atom(pg_dsn: str, repo_id: str, atom_kind: str, subject: str, predicate: str, object_text: str,
                source_type: str = "manual", source_ref: str | None = None, tags: list[str] | None = None,
                canonical_weight: float = 1.0, validity: str = "active"):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO memory_atoms
            (repo_id, atom_kind, subject, predicate, object_text, canonical_weight, validity, source_type, source_ref, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING atom_id
            """,
            (repo_id, atom_kind, subject, predicate, object_text, canonical_weight, validity, source_type, source_ref, tags or []),
        )
        return str(cur.fetchone()[0])

def search_atoms(pg_dsn: str, repo_id: str, query: str, limit: int = 12) -> list[dict[str, Any]]:
    tokens = [t.strip().lower() for t in query.split() if t.strip()]
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT atom_id, atom_kind, subject, predicate, object_text, canonical_weight, validity, tags
            FROM memory_atoms
            WHERE repo_id = %s
            ORDER BY canonical_weight DESC, created_at DESC
            LIMIT 200
            """,
            (repo_id,),
        )
        rows = cur.fetchall()
    scored = []
    for r in rows:
        hay = " ".join([str(r[1]), str(r[2]), str(r[3]), str(r[4]), " ".join(r[7] or [])]).lower()
        score = float(r[5] or 0.0)
        for tok in tokens:
            if tok in hay:
                score += 1.0
        if score > 0:
            scored.append({
                "id": str(r[0]),
                "atom_kind": r[1],
                "subject": r[2],
                "predicate": r[3],
                "object_text": r[4],
                "score": score,
                "validity": r[6],
                "tags": r[7] or [],
                "source": "atom",
            })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]

def atoms_from_authority(repo_id: str, authority: dict) -> list[dict]:
    atoms = []
    startup = authority.get("startup_contract", {})
    for k, v in startup.items():
        atoms.append({
            "repo_id": repo_id,
            "atom_kind": "rule",
            "subject": "startup_contract",
            "predicate": k,
            "object_text": str(v),
            "source_type": "authority",
            "tags": ["startup", "canonical"],
        })
    standards = authority.get("standards", {})
    for k, v in standards.items():
        atoms.append({
            "repo_id": repo_id,
            "atom_kind": "rule",
            "subject": "standards",
            "predicate": k,
            "object_text": str(v),
            "source_type": "authority",
            "tags": ["standards", "canonical"],
        })
    settings = authority.get("settings", {})
    for k, v in settings.items():
        atoms.append({
            "repo_id": repo_id,
            "atom_kind": "preference",
            "subject": "settings",
            "predicate": k,
            "object_text": str(v),
            "source_type": "authority",
            "tags": ["settings", "canonical"],
        })
    procedures = authority.get("procedures", [])
    for i, step in enumerate(procedures, start=1):
        atoms.append({
            "repo_id": repo_id,
            "atom_kind": "procedure_step",
            "subject": "procedures",
            "predicate": f"step_{i}",
            "object_text": str(step),
            "source_type": "authority",
            "tags": ["procedures", "canonical"],
        })
    return atoms

def replace_authority_atoms(pg_dsn: str, repo_id: str, authority: dict):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM memory_atoms WHERE repo_id = %s AND source_type = 'authority'", (repo_id,))
    inserted = 0
    for atom in atoms_from_authority(repo_id, authority):
        insert_atom(
            pg_dsn, atom["repo_id"], atom["atom_kind"], atom["subject"], atom["predicate"], atom["object_text"],
            source_type=atom["source_type"], tags=atom["tags"]
        )
        inserted += 1
    return {"authority_atoms_inserted": inserted}
