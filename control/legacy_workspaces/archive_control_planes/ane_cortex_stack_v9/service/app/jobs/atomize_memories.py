from __future__ import annotations

from typing import Any, Dict, List

from ..adapters.json_memory import JsonMemoryStore
from ..adapters.memory_atoms import insert_atom
from ..config import load_settings
from ..utils.db import pg_conn

RULE_HINTS = {
    "formatter": ("rule", "standards", "formatter"),
    "default_inference_backend": ("preference", "settings", "default_inference_backend"),
    "fallback_backend": ("preference", "settings", "fallback_backend"),
    "hydrate_before_reasoning": ("rule", "startup_contract", "hydrate_before_reasoning"),
    "ignore_codebase_as_authority": ("rule", "startup_contract", "ignore_codebase_as_authority"),
    "upgrade_codebase_from_memory": ("rule", "startup_contract", "upgrade_codebase_from_memory"),
}


def extract_candidate_atoms_from_text(text: str, repo_id: str, source_type: str, source_ref: str | None = None) -> list[dict[str, Any]]:
    atoms = []
    lower = text.lower()
    if "prettier-vscode" in lower:
        atoms.append(
            {
                "repo_id": repo_id,
                "atom_kind": "rule",
                "subject": "standards",
                "predicate": "formatter",
                "object_text": "prettier-vscode",
                "source_type": source_type,
                "source_ref": source_ref,
                "tags": ["standards"],
            }
        )
    if "default_inference_backend" in lower and "ane" in lower:
        atoms.append(
            {
                "repo_id": repo_id,
                "atom_kind": "preference",
                "subject": "settings",
                "predicate": "default_inference_backend",
                "object_text": "ane",
                "source_type": source_type,
                "source_ref": source_ref,
                "tags": ["settings"],
            }
        )
    if "fallback_backend" in lower and "metal" in lower:
        atoms.append(
            {
                "repo_id": repo_id,
                "atom_kind": "preference",
                "subject": "settings",
                "predicate": "fallback_backend",
                "object_text": "metal",
                "source_type": source_type,
                "source_ref": source_ref,
                "tags": ["settings"],
            }
        )
    if "hydrate_before_reasoning" in lower:
        atoms.append(
            {
                "repo_id": repo_id,
                "atom_kind": "rule",
                "subject": "startup_contract",
                "predicate": "hydrate_before_reasoning",
                "object_text": "True",
                "source_type": source_type,
                "source_ref": source_ref,
                "tags": ["startup"],
            }
        )
    if "ignore_codebase_as_authority" in lower:
        atoms.append(
            {
                "repo_id": repo_id,
                "atom_kind": "rule",
                "subject": "startup_contract",
                "predicate": "ignore_codebase_as_authority",
                "object_text": "True",
                "source_type": source_type,
                "source_ref": source_ref,
                "tags": ["startup"],
            }
        )
    return atoms


def atomize_jsonl_memory():
    s = load_settings()
    store = JsonMemoryStore(s.json_memory_path)
    inserted = 0
    for item in store.all():
        text = " ".join([str(item.get("subject", "")), str(item.get("summary", "")), str(item.get("body", ""))])
        atoms = extract_candidate_atoms_from_text(text, s.repo_id, "jsonl", item.get("id"))
        for atom in atoms:
            insert_atom(
                s.postgres_dsn,
                atom["repo_id"],
                atom["atom_kind"],
                atom["subject"],
                atom["predicate"],
                atom["object_text"],
                source_type=atom["source_type"],
                source_ref=atom["source_ref"],
                tags=atom["tags"],
                canonical_weight=0.7,
            )
            inserted += 1
    return {"inserted_atoms_from_jsonl": inserted}


if __name__ == "__main__":
    print(atomize_jsonl_memory())
