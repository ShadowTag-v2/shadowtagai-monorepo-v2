import json
from pathlib import Path

issues_file = Path(".beads/issues.jsonl")
lines = issues_file.read_text().splitlines()

new_lines = []
for line in lines:
    if not line.strip():
        continue
    data = json.loads(line)
    if "contract-orphan-" in data.get("id", ""):
        data["status"] = "resolved"
        data["resolution"] = "Wired ToolGateway contract format."
    new_lines.append(json.dumps(data))

issues_file.write_text("\n".join(new_lines) + "\n")
print("Marked orphaned contracts as resolved.")
