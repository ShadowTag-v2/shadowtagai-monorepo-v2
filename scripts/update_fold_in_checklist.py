#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:
    msg = "PyYAML is required. Install with: python3 -m pip install pyyaml"
    raise SystemExit(msg) from exc


TRUTHY_PRESENT_KEYS = {
    "canonical_in_monorepo",
    "canonical",
    "live",
}


BOOLEAN_FIELDS_TO_STAMP = [
    "folded_into_destination",
    "manifest_updated",
    "merge_status_updated",
    "tooling_updated",
    "final_status_stamped",
]


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_yaml(path: Path, data: Any) -> None:
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def path_exists(root: Path, rel: str | None) -> bool:
    if not rel:
        return False
    return (root / rel).exists()


def normalize_repo_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if isinstance(data, dict):
        if isinstance(data.get("repos"), list):
            return [item for item in data["repos"] if isinstance(item, dict)]
        if isinstance(data.get("repositories"), list):
            return [item for item in data["repositories"] if isinstance(item, dict)]

    msg = "Unsupported checklist schema: expected list or repos/repositories list"
    raise SystemExit(msg)


def write_back(data: Any, items: list[dict[str, Any]]) -> Any:
    if isinstance(data, list):
        return items
    if isinstance(data, dict):
        if "repos" in data and isinstance(data["repos"], list):
            data["repos"] = items
            return data
        if "repositories" in data and isinstance(data["repositories"], list):
            data["repositories"] = items
            return data
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="Update fold_in_checklist.yaml from physical reality")
    parser.add_argument("--checklist", required=True, help="Path to fold_in_checklist.yaml")
    parser.add_argument("--root", required=True, help="Canonical monorepo root")
    args = parser.parse_args()

    checklist_path = Path(args.checklist).resolve()
    root = Path(args.root).resolve()

    if not checklist_path.exists():
        msg = f"Checklist not found: {checklist_path}"
        raise SystemExit(msg)
    if not root.exists():
        msg = f"Root not found: {root}"
        raise SystemExit(msg)

    raw = load_yaml(checklist_path)
    items = normalize_repo_items(raw)

    updated = 0
    blocked = 0

    for item in items:
        item.get("repo") or item.get("name") or item.get("repository") or "unknown"
        dest = item.get("destination") or item.get("canonical_path") or item.get("path")
        status = str(item.get("status", "")).strip()

        exists = path_exists(root, dest)

        if exists:
            for field in BOOLEAN_FIELDS_TO_STAMP:
                if item.get(field) is not True:
                    item[field] = True
                    updated += 1

            if status in {"blocked", "queued_for_fold_in", "pending"}:
                item["status"] = "canonical_in_monorepo" if "reference/public-demos/" not in str(dest) else "reference_only"
                updated += 1

            item["physical_state"] = "present"
            item["blocker"] = None
        else:
            item["physical_state"] = "missing"
            if "reference/public-demos/" in str(dest):
                item["status"] = "blocked"
                item["blocker"] = "Physical path missing"
                blocked += 1

    new_data = write_back(raw, items)
    save_yaml(checklist_path, new_data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
