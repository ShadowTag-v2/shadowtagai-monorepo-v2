import os
import time

import requests

REPOS = {
    "ShadowTag-v2-fastapi-services": "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services",
    "Pipeline": "apps/ShadowTag-v2_stack/Pipeline",
    "cosmic-crab-payload": "apps/ShadowTag-v2_stack/cosmic-crab-payload",
    "nascent-apollo": "apps/ShadowTag-v2_stack/nascent-apollo",
}

TOKEN = None
PEM_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"
APP_ID = "3018200"
try:
    import jwt

    with open(PEM_PATH) as f:
        pk = f.read()
    payload = {"iat": int(time.time()), "exp": int(time.time()) + (10 * 60), "iss": APP_ID}
    enc = jwt.encode(payload, pk, algorithm="RS256")
    r = requests.get("https://api.github.com/app/installations", headers={"Authorization": f"Bearer {enc}"}, timeout=30)
    r.raise_for_status()
    insts = r.json()
    r2 = requests.post(
        f"https://api.github.com/app/installations/{insts[0]['id']}/access_tokens",
        headers={"Authorization": f"Bearer {enc}"},
        timeout=30,
    )
    r2.raise_for_status()
    TOKEN = r2.json()["token"]
except Exception:
    pass

headers = {"Accept": "application/vnd.github.v3+json"}
if TOKEN:
    headers["Authorization"] = f"token {TOKEN}"


def get_remote_tree(repo):
    orgs = ["ehanc69", "ShadowTag-v2"]
    branches = ["main", "master"]
    for org in orgs:
        for branch in branches:
            url = f"https://api.github.com/repos/{org}/{repo}/git/trees/{branch}?recursive=1"
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code == 200:
                return [item["path"] for item in res.json().get("tree", []) if item["type"] == "blob"]
    return None


report = "# Delta Audit of 4 Canonical Roots\n\n"
stale_strings = ["gemini-2.5-flash", "ShadowTag-v2", "AIzaSy", "sk-"]

for repo, dest in REPOS.items():
    remote_files = get_remote_tree(repo)

    if remote_files is None:
        report += f"## {repo}\n**Status:** blocked (Could not fetch remote tree from GitHub API)\n\n"
        continue

    local_dir = os.path.join(os.getcwd(), dest)
    if not os.path.exists(local_dir):
        report += f"## {repo}\n**Status:** drifted (Local destination {dest} missing)\n\n"
        continue

    local_files = []
    stale_hits = []

    for root, dirs, files in os.walk(local_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")
        for f in files:
            path = os.path.relpath(os.path.join(root, f), local_dir)
            local_files.append(path)
            # check stale
            if not f.endswith(".png") and not f.endswith(".jpg") and not f.endswith(".pyc"):
                full = os.path.join(root, f)
                try:
                    with open(full, errors="ignore") as file_obj:
                        content = file_obj.read()
                        for st in stale_strings:
                            if st in content:
                                stale_hits.append(f"{path} contains stale string: '{st}'")
                                break
                except Exception:
                    pass

    remote_set = set(remote_files)
    local_set = set(local_files)

    missing_in_local = frozenset(remote_set - local_set)
    extra_in_local = frozenset(local_set - remote_set)

    report += f"## {repo}\n"

    status = "drifted"
    if len(missing_in_local) == 0 and len(extra_in_local) == 0 and len(stale_hits) == 0:
        status = "fully folded"
    elif len(missing_in_local) < (len(remote_set) / 2):
        status = "partial copy (drifted)" if len(stale_hits) > 0 or len(extra_in_local) > 0 or len(missing_in_local) > 0 else "fully folded"

    report += f"**Status:** {status}\n\n"
    report += f"- **Missing Files (in GitHub but not locally):** {len(missing_in_local)}\n"
    if missing_in_local:
        for m in list(missing_in_local)[:5]:
            report += f"  - `{m}`\n"
        if len(missing_in_local) > 5:
            report += f"  - ... and {len(missing_in_local) - 5} more\n"

    report += f"- **Extra Files (local but not in GitHub):** {len(extra_in_local)}\n"
    if extra_in_local:
        for e in list(extra_in_local)[:5]:
            report += f"  - `{e}`\n"
        if len(extra_in_local) > 5:
            report += f"  - ... and {len(extra_in_local) - 5} more\n"

    report += f"- **Stale References Detected:** {len(stale_hits)}\n"
    if stale_hits:
        for s in stale_hits[:5]:
            report += f"  - `{s}`\n"
        if len(stale_hits) > 5:
            report += f"  - ... and {len(stale_hits) - 5} more\n"

    report += "\n"

os.makedirs("docs", exist_ok=True)
with open("docs/DELTA_AUDIT_REPORT.md", "w") as f:
    f.write(report)
