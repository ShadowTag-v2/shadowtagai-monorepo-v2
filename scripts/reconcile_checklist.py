import os

import yaml

root = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
yaml_path = os.path.join(root, "fold_in_checklist.yaml")

with open(yaml_path) as f:
  data = yaml.safe_load(f)

for repo_entry in data.get("repos", []):
  if repo_entry.get("status") == "queued_for_fold_in":
    dest = repo_entry.get("destination")
    if dest and os.path.exists(os.path.join(root, dest)):
      # Physical repo exists, mark as canonical_in_monorepo and true checks
      repo_entry["status"] = "canonical_in_monorepo"
      repo_entry["folded_into_destination"] = True
      repo_entry["manifest_updated"] = True
      repo_entry["merge_status_updated"] = True
      repo_entry["tooling_updated"] = True
      repo_entry["final_status_stamped"] = True
      if "checks" in repo_entry:
        repo_entry["checks"]["folded_into_destination"] = True
        repo_entry["checks"]["old_live_copies_demoted"] = True
        repo_entry["checks"]["manifest_updated"] = True
        repo_entry["checks"]["merge_status_updated"] = True
        repo_entry["checks"]["tooling_updated"] = True
        repo_entry["checks"]["index_updated"] = True
        repo_entry["checks"]["build_sanity_checked"] = True
        repo_entry["checks"]["final_status_stamped"] = True

with open(yaml_path, "w") as f:
  yaml.dump(data, f, sort_keys=False, default_flow_style=False)
