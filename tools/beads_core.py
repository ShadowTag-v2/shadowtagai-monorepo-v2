# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import os
import datetime
import uuid

BEADS_FILE = ".beads/issues.jsonl"


class BeadsCore:
    def __init__(self):
        os.makedirs(os.path.dirname(BEADS_FILE), exist_ok=True)

    def _load_issues(self) -> list[dict]:
        if not os.path.exists(BEADS_FILE):
            return []
        with open(BEADS_FILE) as f:
            return [json.loads(line) for line in f if line.strip()]

    def _append_issue(self, issue: dict):
        with open(BEADS_FILE, "a") as f:
            f.write(json.dumps(issue) + "\n")

    def create_issue(self, title: str, description: str, type: str = "task") -> str:
        """Create a new tracked item."""
        issue_id = f"bd-{uuid.uuid4().hex[:6]}"
        issue = {
            "id": issue_id,
            "title": title,
            "description": description,
            "type": type,
            "status": "open",
            "created_at": datetime.datetime.now().isoformat(),
            "comments": [],
        }
        self._append_issue(issue)
        return f"✅ Created Issue {issue_id}: {title}"

    def update_status(self, issue_id: str, status: str, comment: str = None) -> str:
        """Move issue state (open -> in_progress -> closed)."""
        event = {
            "id": issue_id,
            "update_type": "status_change",
            "new_status": status,
            "comment": comment,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self._append_issue(event)
        return f"🔄 Updated {issue_id} to {status}"

    def get_ready_work(self) -> str:
        """The 'What should I do?' query."""
        issues = self._load_issues()
        state = {}
        for entry in issues:
            iid = entry.get("id")
            if "title" in entry:  # Creation event
                state[iid] = entry
            elif "update_type" in entry:  # Update event
                if iid in state:
                    state[iid]["status"] = entry.get("new_status", state[iid]["status"])

        ready = [i for i in state.values() if i["status"] == "open"]
        if not ready:
            return "No open issues found."

        return "\n".join([f"[{i['id']}] {i['title']} ({i['type']})" for i in ready])


if __name__ == "__main__":
    beads = BeadsCore()
    print(beads.get_ready_work())
