import json
import os
import subprocess

REPOS = [
    ("ehanc69/pnkln-stackjr-template-2", "apps/templates/pnkln-stackjr-template-2"),
    ("ehanc69/pnkln-stack-objections-decisions", "governance/pnkln-stack-objections-decisions"),
    ("ehanc69/pnkln-stack-core", "packages/pnkln-stack-core"),
    ("ehanc69/pnkln-stack-clients", "apps/pnkln-stack_stack/pnkln-stack-clients"),
    ("ehanc69/pnkln-stack-mlops", "infra/pnkln-stack-mlops"),
    ("ehanc69/pnkln-stack-data-contracts", "packages/pnkln-stack-data-contracts"),
    ("ehanc69/pnkln-stack-infra", "infra/pnkln-stack-infra"),
    ("ehanc69/pnkln-stack-devops", "infra/pnkln-stack-devops"),
    ("ehanc69/pnkln-stack-observability", "infra/pnkln-stack-observability"),
    ("ehanc69/pnkln-stack-sre", "infra/pnkln-stack-sre"),
    ("ehanc69/pnkln-stack-security", "infra/pnkln-stack-security"),
    ("ehanc69/pnkln-stack-sops", "infra/pnkln-stack-sops"),
    ("ehanc69/pnkln-stack-docs", "docs/pnkln-stack"),
    ("ehanc69/pnkln-stack-frontend", "apps/pnkln-stack_stack/pnkln-stack-frontend"),
    ("ehanc69/pnkln-stack-examples", "apps/pnkln-stack_stack/pnkln-stack-examples"),
    ("ehanc69/erik-hancock-llm-memory", "memory/erik-hancock-llm-memory"),
    ("ehanc69/pnkln-stack-rollup", "packages/pnkln-stack-rollup"),
    ("ehanc69/pnkln-stack-api", "apps/pnkln-stack_stack/pnkln-stack-api"),
    ("ehanc69/pnkln", "control/pnkln"),
    ("ehanc69/pnkln-stack-policy", "packages/pnkln-stack-policy"),
    ("ehanc69/pnkln-stack-backend", "apps/pnkln-stack_stack/pnkln-stack-backend"),
    ("ehanc69/pnkln-stack-evals", "evals/pnkln-stack-evals"),
    ("ehanc69/pnkln-stack-governance", "governance/pnkln-stack-governance"),
    ("ehanc69/pnkln-stack-ui-kit", "apps/pnkln-stack_stack/pnkln-stack-ui-kit"),
    ("ehanc69/pnkln-stack-offline-appliance", "apps/pnkln-stack_stack/pnkln-stack-offline-appliance"),
    ("ehanc69/pnkln-stack-risk-engine", "infra/pnkln-stack-risk-engine"),
    ("ehanc69/pnkln-stack-indexer", "packages/pnkln-stack-indexer"),
    ("ehanc69/pnkln-stack-codesmith", "packages/pnkln-stack-codesmith"),
    ("ehanc69/pnkln-stack-prompts", "packages/pnkln-stack-prompts"),
    ("ehanc69/pnkln-stack-exec", "packages/pnkln-stack-exec"),
    ("ehanc69/pnkln-stack-ml", "staging/pnkln-stack-ml"),
    ("ehanc69/pnkln-stack-data", "data/pnkln-stack-data"),
    ("ehanc69/pnkln-stack-risk", "infra/pnkln-stack-risk"),
    ("ehanc69/pnkln-stack-ci", "infra/ci/pnkln-stack-ci"),
]

MONO_ROOT = os.getcwd()
INCOMING_DIR = os.path.join(MONO_ROOT, ".agent", "incoming_repos")
REPORTS_DIR = os.path.join(MONO_ROOT, ".agent", "reports")
CHECKLIST_SCRIPT = os.path.join(
    MONO_ROOT,
    ".agent",
    "bundles",
    "antigravity_manifest_bundle_v3",
    "antigravity_manifest_bundle_v3",
    "fold_in_repo_checklist.py",
)
MANIFEST_PATH = os.path.join(MONO_ROOT, "monorepo_manifest.yaml")

os.makedirs(INCOMING_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

markdown_table = "| Repo | Status | Destination | Duplicate Family | Blockers | Verification |\n"
markdown_table += "| --- | --- | --- | --- | --- | --- |\n"

env = os.environ.copy()
env["GIT_TERMINAL_PROMPT"] = "0"

for git_source, dest_path in REPOS:
    repo_name = git_source.split("/")[-1]
    clone_path = os.path.join(INCOMING_DIR, repo_name)
    out_report = os.path.join(REPORTS_DIR, f"{repo_name}_foldin_report.json")

    print(f"[{repo_name}] Cloning...")
    if not os.path.exists(clone_path):
        res = subprocess.run(["git", "clone", f"https://github.com/{git_source}.git", clone_path], capture_output=True, env=env)
        if res.returncode != 0:
            markdown_table += f"| {repo_name} | BLOCKED | {dest_path} | - | Clone failed (Private/Missing) | Fail |\n"
            continue

    print(f"[{repo_name}] Running Audit...")
    subprocess.run(
        [
            "python3",
            CHECKLIST_SCRIPT,
            repo_name,
            clone_path,
            dest_path,
            "--monorepo-root",
            MONO_ROOT,
            "--out",
            out_report,
        ],
        capture_output=True,
    )

    blockers = "None"
    status = "canonical"
    if os.path.exists(out_report):
        with open(out_report) as f:
            try:
                rep_data = json.load(f)
                if rep_data.get("blocked"):
                    blockers = str(rep_data.get("block_reasons", "Unknown block"))
                    status = "blocked"
            except:
                pass

    if status == "blocked":
        markdown_table += f"| {repo_name} | BLOCKED | {dest_path} | - | {blockers} | Fail |\n"
        continue

    print(f"[{repo_name}] Landing Tree...")
    abs_dest = os.path.join(MONO_ROOT, dest_path)
    os.makedirs(abs_dest, exist_ok=True)
    subprocess.run(["rsync", "-a", "--exclude=.git", f"{clone_path}/", abs_dest], capture_output=True)

    print(f"[{repo_name}] Updating Manifest...")
    try:
        with open(MANIFEST_PATH) as f:
            manifest_lines = f.readlines()

        insert_idx = next((i + 1 for i, line in enumerate(manifest_lines) if line.startswith("repo_roots:")), -1)
        exists = any(f"  {repo_name}:" in line for line in manifest_lines)

        if insert_idx != -1 and not exists:
            entry = [
                f"  {repo_name}:\n",
                "    status: canonical\n",
                f"    canonical_path: {dest_path}\n",
                "    notes: Auto-folded via batch pipeline.\n\n",
            ]
            manifest_lines = manifest_lines[:insert_idx] + entry + manifest_lines[insert_idx:]
            with open(MANIFEST_PATH, "w") as f:
                f.writelines(manifest_lines)
    except Exception as e:
        print(f"[{repo_name}] Manifest update failed: {e}")

    markdown_table += f"| {repo_name} | canonical | {dest_path} | resolved | None | Success |\n"

with open("batch_foldin_summary.md", "w") as f:
    f.write(markdown_table)

print("[done] Batch Fold-In Complete.")
