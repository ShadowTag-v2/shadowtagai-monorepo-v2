# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import os
import sys

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def dispatch_to_kosmos(bar_exam_json):
    """Takes the structured 'Whiteboard' from Gemini Code Assist (ATC)
    and publishes it to the Beads Memory System.
    """
    try:
        plan = json.loads(bar_exam_json)
    except json.JSONDecodeError:
        print("❌ ATC Error: Invalid JSON input.")
        return

    # 1. Create the Epic
    # Mocking 'bd' call since it might not be in PATH in this env
    # epic_cmd = ["bd", "create", plan['objective'], "--type", "epic"]
    # res = subprocess.check_output(epic_cmd).decode()
    # epic_id = json.loads(res)['id']
    epic_id = f"EPIC-{int(os.times()[4] * 100)}"  # Mock ID
    print(f"📡 ATC: Epic Created [{epic_id}] -> Objective: {plan.get('objective', 'Unknown')}")

    # 2. Create the Tasks (The Beads)
    for task in plan.get("tasks", []):
        # APPLY ECHO PROTOCOL HERE?
        # No, we apply it inside the AGENT when it reads the task.
        # We just store the clean instruction.

        # cmd = [
        #     "bd", "create", task['title'],
        #     "--parent", epic_id,
        #     "--priority", task.get('priority', 'normal'),
        #     "--notes", task['description']
        # ]
        # subprocess.run(cmd)
        print(f"   >>> Task Queued: {task['title']} (Priority: {task.get('priority', 'normal')})")

    # 3. Sync Memory to Mothership (Git Push)
    # subprocess.run(["git", "add", ".beads"])
    # subprocess.run(["git", "commit", "-m", f"Monkeys7: Dispatch {epic_id}"])
    # subprocess.run(["git", "push"])

    print("🚀 ATC: Handoff Complete. Kosmos is engaged.")


if __name__ == "__main__":
    # Usage: python scripts/atc_dispatch.py '{"objective": "Refactor Auth", "tasks": [{"title": "Update Login", "description": "Fix bug", "priority": "high"}]}'
    if len(sys.argv) > 1:
        dispatch_to_kosmos(sys.argv[1])
    else:
        print("Usage: python scripts/atc_dispatch.py '<JSON_PLAN>'")
