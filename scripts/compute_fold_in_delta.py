import json
import sys

import yaml


def main() -> None:
  try:
    with open("repo_census.current.json") as f:
      census = json.load(f)

    with open("fold_in_checklist.yaml") as f:
      checklist = yaml.safe_load(f)

    repo_map = {r["repo"].replace("ehanc69/", "", 1): r for r in checklist["repos"]}
    if not repo_map:
      repo_map = {r["repo"]: r for r in checklist["repos"]}

    delta = []
    blockers = []

    for c in census:
      short_name = c["repo_name"]

      check_data = repo_map.get(f"ehanc69/{short_name}") or repo_map.get(short_name)

      if check_data:
        c["current_status"] = check_data.get("status", "unclassified")
        c["desired_status"] = check_data.get("status", "unclassified")
        c["destination_path"] = check_data.get("destination", "none")
        c["duplicate_family"] = check_data.get("duplicate_family", "none")

        # If it's already canonical, skip delta, otherwise add
        if c["desired_status"] not in ["canonical_in_monorepo", "reference_only"]:
          delta.append(c)
      else:
        c["current_status"] = "unclassified"
        c["blocker"] = "Missing from fold_in_checklist.yaml"
        blockers.append(c)
        delta.append(c)

    with open("repo_fold_in_delta.json", "w") as f:
      json.dump(delta, f, indent=2)

    with open("repo_census.current.json", "w") as f:
      json.dump(census, f, indent=2)

    with open("repo_merge_blockers.json", "w") as f:
      json.dump(blockers, f, indent=2)

  except Exception:
    sys.exit(1)


if __name__ == "__main__":
  main()
