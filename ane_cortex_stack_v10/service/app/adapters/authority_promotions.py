# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import json
from typing import Any, Dict

from ..adapters.authority_state import AuthorityState
from ..adapters.memory_atoms import replace_authority_atoms
from ..utils.db import pg_conn


def propose_promotion(pg_dsn: str, repo_id: str, promotion_kind: str, subject: str, payload: dict[str, Any], proposed_by: str = "assistant"):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO authority_promotions (repo_id, promotion_kind, subject, payload, proposed_by) VALUES (%s, %s, %s, %s::jsonb, %s) RETURNING promotion_id",
            (repo_id, promotion_kind, subject, json.dumps(payload), proposed_by),
        )
        return str(cur.fetchone()[0])


def approve_and_apply(pg_dsn: str, repo_id: str, promotion_id: str, authority_state_path: str):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT promotion_kind, subject, payload FROM authority_promotions WHERE promotion_id = %s::uuid",
            (promotion_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"error": "promotion not found"}
        kind, subject, payload = row
        authority = AuthorityState(authority_state_path)
        state = authority.read()

        payload = payload if isinstance(payload, dict) else dict(payload)
        if kind == "setting":
            state.setdefault("settings", {}).update(payload)
        elif kind == "standard":
            state.setdefault("standards", {}).update(payload)
        elif kind == "procedure":
            procedures = state.setdefault("procedures", [])
            for item in payload.get("append", []):
                if item not in procedures:
                    procedures.append(item)
        elif kind == "snapshot":
            state.update(payload)
        else:
            state.setdefault(subject, {}).update(payload)

        authority.write(state)
        replace_authority_atoms(pg_dsn, repo_id, state)
        cur.execute(
            "UPDATE authority_promotions SET approval_status = 'applied', applied_at = now() WHERE promotion_id = %s::uuid",
            (promotion_id,),
        )
    return {"applied": promotion_id, "kind": kind, "subject": subject}
