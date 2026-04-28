# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from __future__ import annotations

import json
from pathlib import Path

from ..adapters.authority_state import AuthorityState, record_authority_event
from ..config import load_settings
from ..utils.db import pg_conn


def detect_drift():
    s = load_settings()
    authority = AuthorityState(s.authority_state_path).read()
    formatter_expected = authority.get("standards", {}).get("formatter", "")
    default_backend = authority.get("settings", {}).get("default_inference_backend", "")
    findings = []

    # VS Code settings drift
    settings_path = Path(".vscode/settings.json")
    if settings_path.exists():
        raw = settings_path.read_text(encoding="utf-8", errors="ignore")
        if formatter_expected and formatter_expected not in raw:
            findings.append(
                {
                    "rel_path": ".vscode/settings.json",
                    "drift_kind": "settings_mismatch",
                    "expected": formatter_expected,
                    "observed": raw[:500],
                    "severity": "high",
                    "suggested_fix": "Update editor.defaultFormatter to canonical formatter",
                }
            )

    # Config drift
    config_path = Path("./config/app.yaml")
    if config_path.exists():
        raw = config_path.read_text(encoding="utf-8", errors="ignore")
        if default_backend and f"default_inference_backend: {default_backend}" not in raw:
            findings.append(
                {
                    "rel_path": "config/app.yaml",
                    "drift_kind": "settings_mismatch",
                    "expected": f"default_inference_backend: {default_backend}",
                    "observed": raw[:500],
                    "severity": "high",
                    "suggested_fix": "Update config/app.yaml to match authority memory",
                }
            )

    with pg_conn(s.postgres_dsn) as conn:
        cur = conn.cursor()
        for f in findings:
            cur.execute(
                """
                INSERT INTO drift_reports (repo_id, rel_path, drift_kind, expected, observed, severity, suggested_fix)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    s.repo_id,
                    f["rel_path"],
                    f["drift_kind"],
                    f["expected"],
                    f["observed"],
                    f["severity"],
                    f["suggested_fix"],
                ),
            )
    if findings:
        record_authority_event(s.postgres_dsn, s.repo_id, "drift_detected", "repo drift", json.dumps(findings))
    return {"drifts": findings, "count": len(findings)}


if __name__ == "__main__":
    print(detect_drift())
