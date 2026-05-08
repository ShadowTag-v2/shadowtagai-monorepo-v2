import sys
import os
import json

sys.path.insert(0, os.path.abspath("packages/jules_orchestrator"))
from client import JulesClient

client = JulesClient()
try:
    sources = client.list_sources()
    print("Sources:", json.dumps(sources, indent=2))

    # find source for Uphillsnowball
    target_source = None
    for s in sources:
        if "Uphillsnowball" in s.get("name", "") or "Uphillsnowball" in s.get("displayName", ""):
            target_source = s["name"]
            break

    if not target_source and sources:
        target_source = sources[0]["name"]

    print(f"Selected source: {target_source}")
    if target_source:
        session = client.create_session(
            source_name=target_source, task_description="Execute post-launch 7-day marketing campaign (autonomous campaign via Jules)"
        )
        print("Session created:", json.dumps(session, indent=2))

except Exception as e:
    print("Error:", str(e))
