#!/usr/bin/env python3
"""Atomic Thread Manager
CRUD operations for OPORD-based atomic threads.
"""

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "docs" / "templates"
THREADS_DIR = PROJECT_ROOT / "docs" / "threads"
CONTEXT_INDEX = PROJECT_ROOT / "docs" / "CONTEXT_INDEX.json"


@dataclass
class ThreadMetadata:
    """Thread metadata structure."""

    thread_id: str
    tier: str  # FREE | FLASH | PRO
    created: str
    status: str  # ACTIVE | COMPLETE | BLOCKED
    parent: str | None
    insert_type: str  # PROMPT | BUGFIX | OPTIMIZE | GENERAL
    summary: str = ""


class AtomicThreadManager:
    """Manage atomic thread lifecycle."""

    def __init__(self) -> None:
        THREADS_DIR.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()

    def _load_index(self) -> dict:
        if CONTEXT_INDEX.exists():
            with open(CONTEXT_INDEX) as f:
                return json.load(f)
        return {
            "threads": {},
            "next_id": 1,
            "stats": {
                "total_created": 0,
                "total_completed": 0,
                "by_tier": {"FREE": 0, "FLASH": 0, "PRO": 0},
            },
        }

    def _save_index(self) -> None:
        with open(CONTEXT_INDEX, "w") as f:
            json.dump(self.index, f, indent=2)

    def _get_next_id(self) -> str:
        thread_id = f"ATOMIC-{self.index['next_id']:03d}"
        self.index["next_id"] += 1
        return thread_id

    def create(
        self,
        tier: str = "FREE",
        insert_type: str = "GENERAL",
        parent: str | None = None,
        mission: str = "",
        situation: str = "",
    ) -> str:
        thread_id = self._get_next_id()
        created = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        with open(TEMPLATES_DIR / "ATOMIC_THREAD_TEMPLATE.md") as f:
            template = f.read()

        template = template.replace("ATOMIC-XXX", thread_id)
        template = template.replace("tier: FREE | FLASH | PRO", f"tier: {tier}")
        template = template.replace("YYYY-MM-DD HH:MM UTC", created)
        template = template.replace("status: ACTIVE | COMPLETE | BLOCKED", "status: ACTIVE")
        template = template.replace("parent: null | ATOMIC-XXX", f"parent: {parent or 'null'}")
        template = template.replace("insert_type: PROMPT | BUGFIX | OPTIMIZE | GENERAL", f"insert_type: {insert_type}")

        if mission:
            template = template.replace("[One sentence: Action verb + object + outcome]", mission)

        if situation:
            template = template.replace("[One paragraph: What is broken/missing/needed? Be specific.]", situation)

        if insert_type != "GENERAL":
            insert_file = TEMPLATES_DIR / "inserts" / f"{insert_type}_INSERT.md"
            if insert_file.exists():
                with open(insert_file) as f:
                    insert_content = f.read()
                template = template.replace("<!-- Include appropriate insert based on insert_type -->", insert_content)

        thread_file = THREADS_DIR / f"{thread_id}.md"
        with open(thread_file, "w") as f:
            f.write(template)

        metadata = ThreadMetadata(
            thread_id=thread_id,
            tier=tier,
            created=created,
            status="ACTIVE",
            parent=parent,
            insert_type=insert_type,
            summary=mission,
        )
        self.index["threads"][thread_id] = asdict(metadata)
        self.index["stats"]["total_created"] += 1
        self.index["stats"]["by_tier"][tier] += 1
        self._save_index()

        return thread_id

    def complete(self, thread_id: str, outcome: str, files_changed: list[str] | None = None) -> None:
        if thread_id not in self.index["threads"]:
            msg = f"Thread {thread_id} not found"
            raise ValueError(msg)

        self.index["threads"][thread_id]["status"] = "COMPLETE"
        self.index["threads"][thread_id]["summary"] = outcome
        self.index["stats"]["total_completed"] += 1
        self._save_index()

        thread_file = THREADS_DIR / f"{thread_id}.md"
        if thread_file.exists():
            with open(thread_file) as f:
                content = f.read()

            handoff = {
                "thread_id": thread_id,
                "outcome": outcome,
                "files_changed": files_changed or [],
                "tests": {"passed": 0, "failed": 0},
                "next_action": "",
            }

            content = re.sub(
                r'"thread_id": "ATOMIC-XXX".*?"next_action": ""',
                json.dumps(handoff, indent=2)[1:-1],
                content,
                flags=re.DOTALL,
            )

            content = content.replace("[ ] COMPLETE", "[x] COMPLETE")

            with open(thread_file, "w") as f:
                f.write(content)


    def block(self, thread_id: str, reason: str) -> None:
        if thread_id not in self.index["threads"]:
            msg = f"Thread {thread_id} not found"
            raise ValueError(msg)

        self.index["threads"][thread_id]["status"] = "BLOCKED"
        self.index["threads"][thread_id]["summary"] = f"BLOCKED: {reason}"
        self._save_index()

    def list_threads(self, status: str | None = None) -> list[dict]:
        threads = list(self.index["threads"].values())
        if status:
            threads = [t for t in threads if t["status"] == status]
        return sorted(threads, key=lambda x: x["created"], reverse=True)

    def get_stats(self) -> dict:
        return self.index["stats"]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Atomic Thread Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    create_parser = subparsers.add_parser("create", help="Create new thread")
    create_parser.add_argument("--tier", choices=["FREE", "FLASH", "PRO"], default="FREE")
    create_parser.add_argument("--type", choices=["PROMPT", "BUGFIX", "OPTIMIZE", "GENERAL"], default="GENERAL")
    create_parser.add_argument("--parent", help="Parent thread ID")
    create_parser.add_argument("--mission", help="Brief mission statement")
    create_parser.add_argument("--situation", help="Problem description")

    complete_parser = subparsers.add_parser("complete", help="Complete thread")
    complete_parser.add_argument("thread_id", help="Thread ID")
    complete_parser.add_argument("--outcome", required=True, help="Outcome summary")
    complete_parser.add_argument("--files", nargs="*", help="Files changed")

    block_parser = subparsers.add_parser("block", help="Block thread")
    block_parser.add_argument("thread_id", help="Thread ID")
    block_parser.add_argument("--reason", required=True, help="Block reason")

    list_parser = subparsers.add_parser("list", help="List threads")
    list_parser.add_argument("--status", choices=["ACTIVE", "COMPLETE", "BLOCKED"])

    subparsers.add_parser("stats", help="Show statistics")

    args = parser.parse_args()
    manager = AtomicThreadManager()

    if args.command == "create":
        manager.create(
            tier=args.tier,
            insert_type=args.type,
            parent=args.parent,
            mission=args.mission or "",
            situation=args.situation or "",
        )
    elif args.command == "complete":
        manager.complete(args.thread_id, args.outcome, args.files)
    elif args.command == "block":
        manager.block(args.thread_id, args.reason)
    elif args.command == "list":
        threads = manager.list_threads(args.status)
        for _t in threads:
            pass
    elif args.command == "stats":
        manager.get_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
