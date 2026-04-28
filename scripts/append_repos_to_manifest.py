# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json

with open("fetched_repos_client_id.json") as f:
    repos = json.load(f)

# filter out the monorepo itself — it IS the canonical root, not a component
repos = [r for r in repos if r != "Monorepo-Uphillsnowball"]
# the 4 ShadowTag-v2_stack repos are already declared as folded-in components
existing = {"ShadowTag-v2-fastapi-services", "cosmic-crab-payload", "Pipeline", "nascent-apollo"}
new_repos = [r for r in repos if r not in existing]


with open("monorepo_manifest.yaml") as f:
    lines = f.readlines()

out_lines = []
inserted = False

for line in lines:
    out_lines.append(line)
    if not inserted and line.strip() == "notes: Folded-in component. Not a root peer.":
        # append after the last known folded-in component
        out_lines.append("\n")
        for r in new_repos:
            block = f"""  - name: {r}
    status: folded-in
    path: apps/ShadowTag-v2_stack/{r}
    notes: Folded-in component. Not a root peer.

"""
            out_lines.append(block)
        inserted = True

with open("monorepo_manifest.yaml", "w") as f:
    f.writelines(out_lines)
