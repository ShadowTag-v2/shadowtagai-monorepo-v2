# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from pathlib import Path

import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    sqlite_db: str = "./data/file_index/ane_files.db"
    lancedb_root: str = "./data/lancedb"
    postgres_dsn: str = "postgresql://postgres:postgres@localhost:5432/ane_mem"
    repo_id: str = "ane"
    repo_root: str = "./external_repos/ANE"
    json_memory_path: str = "./data/memory/memories.jsonl"
    authority_state_path: str = "./data/memory/authority-current.json"
    monorepo_manifest_path: str = "./manifests/monorepo_manifest.yaml"
    monorepo_merge_status_path: str = "./docs/MERGE_STATUS.md"
    monorepo_control_plane_path: str = "./docs/ANTIGRAVITY_CONTROL_PLANE.md"


def load_settings(path: str = "./config/app.yaml") -> Settings:
    p = Path(path)
    if not p.exists():
        return Settings()
    data = yaml.safe_load(p.read_text()) or {}
    return Settings(
        sqlite_db=data.get("paths", {}).get("sqlite_db", Settings().sqlite_db),
        lancedb_root=data.get("paths", {}).get("lancedb_root", Settings().lancedb_root),
        repo_id=data.get("repo", {}).get("repo_id", "ane"),
        repo_root=data.get("repo", {}).get("repo_root", "./external_repos/ANE"),
        json_memory_path=data.get("paths", {}).get("json_memory_path", Settings().json_memory_path),
        authority_state_path=data.get("paths", {}).get(
            "authority_state_path", Settings().authority_state_path
        ),
        monorepo_manifest_path=data.get("paths", {}).get(
            "monorepo_manifest_path", Settings().monorepo_manifest_path
        ),
        monorepo_merge_status_path=data.get("paths", {}).get(
            "monorepo_merge_status_path", Settings().monorepo_merge_status_path
        ),
        monorepo_control_plane_path=data.get("paths", {}).get(
            "monorepo_control_plane_path", Settings().monorepo_control_plane_path
        ),
    )
