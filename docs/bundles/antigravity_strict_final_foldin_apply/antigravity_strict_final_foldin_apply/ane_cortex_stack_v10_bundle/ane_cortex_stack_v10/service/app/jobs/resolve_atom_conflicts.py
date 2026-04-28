# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from __future__ import annotations

from ..config import load_settings
from ..utils.db import pg_conn


def detect_conflicts():
    s = load_settings()
    conflicts = []
    with pg_conn(s.postgres_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT atom_id, subject, predicate, object_text, source_type, canonical_weight
            FROM memory_atoms
            WHERE repo_id = %s AND validity = 'active'
            ORDER BY subject, predicate, canonical_weight DESC, created_at DESC
            """,
            (s.repo_id,),
        )
        rows = cur.fetchall()
        seen = {}
        for atom_id, subject, predicate, object_text, source_type, canonical_weight in rows:
            key = (subject, predicate)
            if key not in seen:
                seen[key] = (atom_id, object_text, source_type, canonical_weight)
                continue
            canon_id, canon_value, canon_source, canon_weight = seen[key]
            if str(object_text) != str(canon_value):
                conflicts.append(
                    {
                        "subject": subject,
                        "predicate": predicate,
                        "canonical_atom_id": str(canon_id),
                        "conflicting_source_type": source_type,
                        "conflicting_source_ref": str(atom_id),
                        "conflicting_value": str(object_text),
                    }
                )
        for c in conflicts:
            cur.execute(
                """
                INSERT INTO atom_conflicts
                (repo_id, subject, predicate, canonical_atom_id, conflicting_source_type, conflicting_source_ref, conflicting_value)
                VALUES (%s, %s, %s, %s::uuid, %s, %s, %s)
                """,
                (
                    s.repo_id,
                    c["subject"],
                    c["predicate"],
                    c["canonical_atom_id"],
                    c["conflicting_source_type"],
                    c["conflicting_source_ref"],
                    c["conflicting_value"],
                ),
            )
    return {"conflicts_detected": len(conflicts), "conflicts": conflicts}


if __name__ == "__main__":
    print(detect_conflicts())
