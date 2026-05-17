# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import re
from pathlib import Path

# Invariants to Enforce
CANONICAL_MCP = "antigravity-mcp-config.json"
CANONICAL_PROJECT = "shadowtag-omega-v4"
CANONICAL_MODEL = "gemini-3.1-family"
LAB_PATH = "labs/uphillsnowball"
PROD_PATH = "apps/counselconduit"

drift_results = []
secret_pattern = re.compile(r"(AIzaSy[A-Za-z0-9_-]{33}|sk-[A-Za-z0-9]{48})")
stale_models = [
  "gemini-3.1-family",
  "gemini-3.1-family",
  "gemini-3.1-family",
  "gemini-3.1-family",
]
stale_projects = ["shadowtag-omega-v4"]

print("🔍 Initiating Stage 3 Canonicalization & Repo-Drift Audit...")


def audit_file(filepath):
  try:
    with open(filepath, encoding="utf-8", errors="ignore") as f:
      content = f.read()

    # 1. Secret Checking (Never inline in config)
    if (
      filepath.name.endswith(".json")
      or filepath.name.endswith(".yaml")
      or filepath.name.endswith(".py")
    ):
      secrets = secret_pattern.findall(content)
      if secrets:
        drift_results.append(f"[RULE 2 VIOLATION] Inline secret detected in {filepath}")

    # 2. Canonical Model
    for sm in stale_models:
      if sm in content:
        drift_results.append(
          f"[DRIFT DETECTED] Stale model '{sm}' found in {filepath} (Expected: {CANONICAL_MODEL})"
        )

    # 3. Canonical Project
    for sp in stale_projects:
      if sp in content:
        drift_results.append(
          f"[DRIFT DETECTED] Stale project '{sp}' found in {filepath} (Expected: {CANONICAL_PROJECT})"
        )
  except Exception:
    pass


p_root = Path(".")
print("-> Scanning for orphaned MCP configurations...")
# 1. MCP single source of truth
for mcp_file in p_root.rglob("*mcp*.json"):
  if "node_modules" in str(mcp_file) or ".venv" in str(mcp_file):
    continue
  if mcp_file.name != CANONICAL_MCP:
    drift_results.append(f"[RULE 1 VIOLATION] Orphaned MCP File Detected: {mcp_file}")

print("-> Deep traversing application code for secrets and model drift...")
# Traverse selected paths
target_dirs = [PROD_PATH, LAB_PATH, "scripts", "apps/src"]
for d in target_dirs:
  target = p_root / d
  if not target.exists():
    drift_results.append(
      f"[RULE 3 WARNING] Expected path {d} is missing or incomplete."
    )
    continue
  for f in target.rglob("*"):
    if (
      f.is_file()
      and "node_modules" not in str(f)
      and ".venv" not in str(f)
      and not f.name.startswith(".")
    ):
      audit_file(f)

print("\n==============================")
print("STAGE 3 AUDIT RESULTS")
print("==============================\n")
if not drift_results:
  print("✅ ZERO DRIFT. Workspace is strictly canonical.")
else:
  for res in drift_results:
    print(res)

with open("docs/STAGE_3_DRIFT_AUDIT.txt", "w") as out:
  out.write("\n".join(drift_results))
print("\nLog written to docs/STAGE_3_DRIFT_AUDIT.txt")
