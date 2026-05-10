import json


def patch_drift() -> None:
  # Load 01
  with open("01_repo_census.json") as f:
    census = json.load(f)

  # Missing physical paths identified in Stage 3 audit
  missing_paths = [
    "reference/public-demos/antigravity-go",
    "reference/public-demos/codepmcs",
    "reference/public-demos/judge6",
    "reference/public-demos/kosmos",
    "reference/public-demos/shadowtag_v2",
  ]

  missing_repos = []

  # 1. Update 01_repo_census.json
  for repo in census:
    if repo["destination_path"] in missing_paths:
      repo["disposition"] = "blocked"
      repo["blocker"] = "Physical path missing in workspace"
      repo["evidence"] = "Stage 3 drift audit failed path existence check"
      missing_repos.append(repo)

  with open("01_repo_census.json", "w") as f:
    json.dump(census, f, indent=2)

  # 2. Update 02_merge_plan.md with blocked items
  with open("02_merge_plan.md", "a") as f:
    f.write("\n## BLOCKED ITEMS\n")
    for repo in missing_repos:
      f.write(f"### {repo['repo_name']}\n")
      f.write(f"- **Destination:** `{repo['destination_path']}`\n")
      f.write("- **Rationale:** Designated reference_only but not cloned/rsynced.\n")
      f.write(
        "- **Exact Next Action:** Clone repository via GitHub App into reference dest.\n"
      )
      f.write("- **Risk Note:** None. Purely missing data.\n\n")

  # 3. Update 04_canonical_state.md
  total = len(census)
  blocked = len(missing_repos)
  canon = total - blocked

  # Read and rewrite 04 to inject the block count and the duplicate roots finding
  with open("04_canonical_state.md") as f:
    state_lines = f.readlines()

  with open("04_canonical_state.md", "w") as f:
    for line in state_lines:
      if "- **total canonical:**" in line:
        f.write(f"- **total canonical:** {canon}\n")
      elif "- **total blocked:**" in line:
        f.write(f"- **total blocked:** {blocked}\n")
      elif "### Blocked Repos" in line:
        f.write("### Blocked Repos\n")
        f.writelines(
          f"- `{r['repo_name']}`: Physical path missing\n" for r in missing_repos
        )
      elif "- None." in line:
        continue  # we replaced it above
      elif "- **duplicate-live-root result:** NO DUPLICATES" in line:
        f.write(
          "- **duplicate-live-root result:** FAIL (legacy roots found like apps/ShadowTag-v2-fastapi-services vs apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services)\n",
        )
      elif "- **final verdict:** COMPLETE" in line:
        f.write("- **final verdict:** COMPLETE_WITH_BLOCKERS\n")
      else:
        f.write(line)


if __name__ == "__main__":
  patch_drift()
