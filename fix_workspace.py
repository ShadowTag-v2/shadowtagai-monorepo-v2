import json
import os

paths = [
  ".vscode/settings.json",
  "pnkln.code-workspace",
  "Monorepo-Uphillsnowball.code-workspace",
]

for p in paths:
  if os.path.exists(p):
    with open(p) as f:
      try:
        data = json.load(f)
      except:
        continue
    # Remove bad schemas
    if "json.schemas" in data:
      data["json.schemas"] = [
        s for s in data["json.schemas"] if "ty" not in str(s.get("url", ""))
      ]
    # Ensure ruff is default
    data["python.formatting.provider"] = "none"
    data["[python]"] = {
      "editor.defaultFormatter": "charliermarsh.ruff",
      "editor.formatOnSave": True,
      "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit",
      },
    }
    with open(p, "w") as f:
      json.dump(data, f, indent=4)
    print(f"Fixed {p}")

# Wipe vim state
os.system("rm -rf ~/.vscodevim.vim")
os.system("rm -rf .vscodevim.vim")

# Fix git ENOENT
os.system("git pack-refs --all --prune")
print("Diagnostics complete.")
