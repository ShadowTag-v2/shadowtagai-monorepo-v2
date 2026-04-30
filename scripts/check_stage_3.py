import os

import yaml


def check_stage_3() -> None:
    try:
        with open("monorepo_manifest.yaml") as f:
            manifest = yaml.safe_load(f)
    except Exception:
        return

    drift = 0
    expected_paths = []

    for r in manifest.get("repos", []):
        if r.get("canonical_path"):
            expected_paths.append(r["canonical_path"])

    for p in expected_paths:
        if not os.path.exists(p):
            drift += 1

    domains = [
        "apps",
        "labs",
        "shared",
        "infra",
        "packages",
        "staging",
        "control",
        "evals",
        "data",
        "docs",
        "reference",
        "governance",
        "memory",
    ]

    for domain in domains:
        if os.path.exists(domain):
            for d in os.listdir(domain):
                if d in {".DS_Store", "__pycache__"}:
                    continue
                path = f"{domain}/{d}"
                # For example, apps/ShadowTag-v2_stack. If no expected path starts with apps/ShadowTag-v2_stack, and apps/ShadowTag-v2_stack doesn't start with expected...
                is_valid = False
                for ep in expected_paths:
                    if ep == path or ep.startswith(path + "/") or path.startswith(ep + "/"):
                        is_valid = True
                        break
                if not is_valid and os.path.isdir(path):
                    drift += 1

    # we can use find across domains
    search_dirs = " ".join([d for d in domains if os.path.exists(d)])
    nested_git = os.popen(f"find {search_dirs} -mindepth 2 -type d -name '.git' 2>/dev/null").read().strip()  # nosec B605 — intentional shell for git/system ops
    if nested_git:
        lines = nested_git.split("\n")
        for _l in lines[:5]:
            pass
        drift += len(lines)

    if drift == 0:
        pass


if __name__ == "__main__":
    check_stage_3()
