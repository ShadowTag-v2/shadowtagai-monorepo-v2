# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import json
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any, Dict

from ..utils.db import pg_conn


class AuthorityState:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "version": 1,
                "repo_id": "ane",
                "startup_contract": {},
                "standards": {},
                "settings": {},
                "procedures": [],
                "last_updated": None,
            }
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {
                "version": 1,
                "repo_id": "ane",
                "startup_contract": {},
                "standards": {},
                "settings": {},
                "procedures": [],
                "last_updated": None,
            }

    def write(self, data: dict[str, Any]) -> dict[str, Any]:
        data["last_updated"] = datetime.now(UTC).isoformat()
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return data

    def update_section(self, section: str, payload: Any) -> dict[str, Any]:
        state = self.read()
        state[section] = payload
        return self.write(state)


def persist_snapshot(pg_dsn: str, repo_id: str, authority_kind: str, subject: str, content_json: str, version_tag: str | None = None):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE authority_snapshots SET is_active = false WHERE repo_id = %s AND authority_kind = %s AND subject = %s",
            (repo_id, authority_kind, subject),
        )
        cur.execute(
            "INSERT INTO authority_snapshots (repo_id, authority_kind, subject, content, version_tag, is_active) VALUES (%s, %s, %s, %s::jsonb, %s, true)",
            (repo_id, authority_kind, subject, content_json, version_tag),
        )


def record_authority_event(pg_dsn: str, repo_id: str, event_type: str, subject: str, body_json: str):
    with pg_conn(pg_dsn) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO authority_events (repo_id, event_type, subject, body) VALUES (%s, %s, %s, %s::jsonb)",
            (repo_id, event_type, subject, body_json),
        )
