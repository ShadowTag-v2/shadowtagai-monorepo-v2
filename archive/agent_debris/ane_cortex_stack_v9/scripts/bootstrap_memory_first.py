from service.app.config import load_settings
from service.app.adapters.authority_state import AuthorityState, persist_snapshot
from service.app.adapters.json_memory import JsonMemoryStore
from service.app.adapters.memory_atoms import replace_authority_atoms
import json

s = load_settings()
authority = AuthorityState(s.authority_state_path)
state = authority.write(
    {
        "version": 1,
        "repo_id": s.repo_id,
        "startup_contract": {"hydrate_before_reasoning": True, "ignore_codebase_as_authority": True, "upgrade_codebase_from_memory": True},
        "standards": {"formatter": "prettier-vscode", "memory_mode": "authority_first", "context_rule": "never start from old codebase state"},
        "settings": {"default_inference_backend": "ane", "fallback_backend": "metal"},
        "procedures": [
            "Load authority memory first",
            "Load latest task state second",
            "Load codebase only after memory hydration",
            "If mismatch exists, create upgrade task instead of mutating memory backward",
        ],
    }
)
persist_snapshot(s.postgres_dsn, s.repo_id, "startup", "memory-first-bootstrap", json.dumps(state), "v1")
replace_authority_atoms(s.postgres_dsn, s.repo_id, state)
JsonMemoryStore(s.json_memory_path).append(
    {
        "type": "startup_contract",
        "subject": "memory-first bootstrap",
        "summary": "Authority memory is canonical; codebase is secondary context.",
        "body": "Antigravity must hydrate from authority memory before it looks at the codebase.",
        "tags": ["bootstrap", "authority", "antigravity"],
        "repo_id": s.repo_id,
    }
)
print({"status": "bootstrapped", "authority_state_path": s.authority_state_path})
