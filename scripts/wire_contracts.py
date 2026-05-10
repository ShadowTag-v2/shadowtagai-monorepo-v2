import json
from pathlib import Path

issues_file = Path(".beads/issues.jsonl")
lines = issues_file.read_text().splitlines()

orphan_ids = []
for line in lines:
  if not line.strip():
    continue
  data = json.loads(line)
  if "contract-orphan-" in data.get("id", ""):
    orphan_ids.append(data["id"].replace("contract-orphan-", ""))

for oid in orphan_ids:
  yaml_path = Path(f"tool_contracts/{oid}.yaml")
  if yaml_path.exists():
    content = f"""# tool_contracts/{oid}.yaml
tool_id: "{oid}"
description: "Governs the {oid} operations."
risk_level: "low"
preconditions: []
evidence_requirements:
  - type: "log"
    path: ".beads/evidence/{oid.replace(".", "_")}.jsonl"
reuse_queries: []
"""
    yaml_path.write_text(content)
    print(f"Wired {yaml_path}")
  else:
    print(f"File not found: {yaml_path}")
