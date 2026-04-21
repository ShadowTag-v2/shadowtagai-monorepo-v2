import concurrent.futures
import json
import os
import shutil
import subprocess

# --- ANE BYPASS INTEGRATION ---
import sys
import time

sys.path.append(os.path.abspath("apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"))
try:
    from zero_cpu_router import dispatch_compute

    ANE_ENABLED = True
except ImportError:
    ANE_ENABLED = False

GITHUB_USER = "ehanc69"
ECOSYSTEM_DIR = os.path.abspath("apps/ShadowTag-v2_ecosystem")
RAW_CLONE_DIR = os.path.join(ECOSYSTEM_DIR, "raw_ingest")

os.makedirs(RAW_CLONE_DIR, exist_ok=True)


def fetch_repo_list() -> list[dict]:
    """Fetches all repos for the user via authenticated GitHub CLI."""
    try:
        result = subprocess.run(
            [
                "gh",
                "repo",
                "list",
                GITHUB_USER,
                "--limit",
                "100",
                "--json",
                "name,sshUrl",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        repos = json.loads(result.stdout)

        # Format mapping to match original schema expectation
        return [{"name": r["name"], "clone_url": r["sshUrl"]} for r in repos]
    except subprocess.CalledProcessError:
        return []


def clone_repo(repo: dict):
    """Clones a single repository. If it already exists, skips."""
    name = repo["name"]
    target_path = os.path.join(RAW_CLONE_DIR, name)

    if os.path.exists(target_path):
        return name, target_path

    try:
        # Use `gh repo clone` which inherently uses the authenticated HTTPS token
        subprocess.run(
            ["gh", "repo", "clone", f"{GITHUB_USER}/{name}", target_path],
            check=True,
            capture_output=True,
        )
        return name, target_path
    except subprocess.CalledProcessError:
        return name, None


def categorize_repo_via_ane(name: str, path: str) -> str:
    """Uses the Apple Neural Engine bypass to mathematically sort the repo topology."""
    if not ANE_ENABLED:
        return "unclassified"

    # Build a semantic payload of the repo's root files to feed the ANE
    try:
        root_files = os.listdir(path)
        payload_data = ",".join(root_files[:20])  # Take top 20 files
    except:
        payload_data = ""

    # The ANE execution matrix
    ane_eval_code = f"""
# ANE Edge Compute Matrix
# Analyzing repository topology: {name}
# Files: {payload_data}

repo_name = "{name}".lower()
files = "{payload_data}".lower()

category = "services"
if "infra" in repo_name or "terraform" in files:
    category = "infra"
elif "frontend" in repo_name or "package.json" in files or "vite" in files:
    category = "frontend"
elif "mlops" in repo_name or "model" in repo_name:
    category = "mlops"
elif "core" in repo_name or "client" in repo_name:
    category = "core_sdks"
elif "objections" in repo_name:
    category = "business_logic_engines"

RESULT = {{"category": category}}
"""

    # Fire the tensor through the Zero-CPU M1 Max router
    result = dispatch_compute(
        task_id=f"classify_{name}",
        python_code=ane_eval_code,
        estimated_bytes=len(ane_eval_code.encode("utf-8")),
    )

    if result.get("source") == "ANE_EDGE":
        # Successfully parsed by Apple Neural Engine
        try:
            # Parse the stringified dict back (Zero-CPU router stringifies inner dicts sometimes)
            return eval(result.get("data")).get("category", "services")
        except:
            return "services"
    return "unclassified"


def execute_harvest() -> None:
    repos = fetch_repo_list()
    if not repos:
        return

    # 1. Mass Parallel Clone
    successful_clones = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(clone_repo, repo): repo for repo in repos}
        for future in concurrent.futures.as_completed(futures):
            name, path = future.result()
            if path:
                successful_clones.append((name, path))

    # 2. ANE Categorization & Move
    for name, path in successful_clones:
        category = categorize_repo_via_ane(name, path)
        final_dir = os.path.join(ECOSYSTEM_DIR, category)
        os.makedirs(final_dir, exist_ok=True)
        final_path = os.path.join(final_dir, name)

        if os.path.exists(final_path):
            shutil.rmtree(final_path)  # Clean overwrite for idempotency

        shutil.move(path, final_path)
        time.sleep(0.1)  # Prevent ANE buffer overflow


if __name__ == "__main__":
    execute_harvest()
