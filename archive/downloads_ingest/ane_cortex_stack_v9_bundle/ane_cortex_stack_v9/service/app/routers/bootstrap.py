# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import APIRouter
import json
from ..config import load_settings
from ..adapters.authority_state import AuthorityState, record_authority_event
from ..adapters.cortexltm import create_thread, add_event, write_summary
from ..adapters.memory_atoms import replace_authority_atoms

router = APIRouter(prefix="/api")

@router.get("/bootstrap")
def bootstrap():
    s = load_settings()
    state = AuthorityState(s.authority_state_path).read()
    return {
        "repo_id": s.repo_id,
        "authority": state,
        "startup_instruction": (
            "Hydrate from authority memory first. "
            "Treat codebase as a target to update, not the source of truth for standards/settings."
        ),
    }

@router.post("/bootstrap/seed")
def seed_bootstrap():
    s = load_settings()
    state = AuthorityState(s.authority_state_path)
    payload = state.write({
        "version": 1,
        "repo_id": s.repo_id,
        "startup_contract": {
            "mode": "memory_first",
            "ignore_codebase_as_authority": True,
            "hydrate_before_reasoning": True
        },
        "standards": {
            "formatter": "prettier-vscode",
            "memory_rule": "authority memory is canonical",
            "upgrade_rule": "memory updates codebase, codebase does not override memory"
        },
        "settings": {
            "default_inference_backend": "ane",
            "fallback_backend": "metal"
        },
        "procedures": [
            "At session start load authority-current.json",
            "Then read latest authority snapshots",
            "Then read recent tasks and current thread summary",
            "Only then inspect codebase"
        ]
    })
    replace_authority_atoms(s.postgres_dsn, s.repo_id, payload)
    record_authority_event(
        s.postgres_dsn, s.repo_id, "startup_hydration", "seed bootstrap", json.dumps(payload)
    )
    thread_id = create_thread(s.postgres_dsn, "00000000-0000-0000-0000-000000000001", "bootstrap seed")
    add_event(s.postgres_dsn, thread_id, "assistant", "Seeded memory-first bootstrap contract.")
    write_summary(s.postgres_dsn, thread_id, "Memory-first bootstrap contract is active.")
    return {"status": "seeded", "authority": payload}
