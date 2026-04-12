import os
import subprocess
from pathlib import Path

# Directories to scan
scan_dirs = [
    os.path.expanduser("~/antigravity-repos"),
    os.path.expanduser("~/ShadowTag-v2-stack"),
    os.path.expanduser("~/.gemini/antigravity"),
]

table_header = "| Local Path | Git Remote | Status |\n|---|---|---|\n"
markdown_rows = []


def get_remote(git_dir):
    try:
        remote = subprocess.check_output(
            ["git", "-C", str(git_dir), "config", "--get", "remote.origin.url"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return remote
    except subprocess.CalledProcessError:
        return ""


print("Generating Dedup Table...")
for root_dir in scan_dirs:
    root_path = Path(root_dir)
    if not root_path.exists():
        continue

    for path in root_path.rglob(".git"):
        repo_dir = path.parent
        # Avoid traversing too deep into virtualenvs or node_modules
        if "node_modules" in str(repo_dir) or ".venv" in str(repo_dir):
            continue

        remote_url = get_remote(repo_dir)

        # Determine status
        status = "Unknown"
        ds_path = str(repo_dir)
        if (
            "Monorepo-Uphillsnowball" in ds_path
            and "external_sdks" not in ds_path
            and "incoming_repos" not in ds_path
        ):
            status = "**Canonical (Monorepo Root)**"
        elif "archive_legacy_" in ds_path or "archive" in ds_path:
            status = "Archive"
        elif remote_url and "ehanc69" in remote_url:
            status = "Standalone Source (ehanc69)"
        elif not remote_url:
            status = "Non-Git Copy / Local Duplicate"
        else:
            status = "Duplicate Git Clone"

        clean_path = ds_path.replace(os.path.expanduser("~"), "~")
        markdown_rows.append(
            f"| `{clean_path}` | `{remote_url if remote_url else 'NONE'}` | {status} |"
        )

# Also find raw non-git folders that match the target names
target_names = [
    "ShadowTag-v2-fastapi-services",
    "Pipeline",
    "cosmic-crab-payload",
    "nascent-apollo",
    "ShadowTag-v2",
]
for root_dir in scan_dirs:
    root_path = Path(root_dir)
    if not root_path.exists():
        continue
    for path in root_path.rglob("*"):
        if path.is_dir() and path.name in target_names and not (path / ".git").exists():
            if (
                "node_modules" in str(path)
                or ".venv" in str(path)
                or "apps/ShadowTag-v2_stack" in str(path)
            ):
                continue
            clean_path = str(path).replace(os.path.expanduser("~"), "~")
            markdown_rows.append(f"| `{clean_path}` | `NONE` | Non-Git Folder / Flat Copy |")

markdown_rows.sort()
report = table_header + "\n".join(markdown_rows)

out_file = "docs/DEDUP_MAPPING.md"
os.makedirs("docs", exist_ok=True)
with open(out_file, "w") as f:
    f.write(report)

print(f"Report written to {out_file}.")
print(report)
