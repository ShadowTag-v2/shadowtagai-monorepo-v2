# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os

import yaml


def check_stage_3():
    try:
        with open("monorepo_manifest.yaml") as f:
            manifest = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading monorepo_manifest.yaml: {e}")
        return

    print("--- Stage 3 Canonicalization & Repo-Drift Audit ---\n")

    drift = 0
    expected_paths = []

    for r in manifest.get("repos", []):
        if r.get("canonical_path"):
            expected_paths.append(r["canonical_path"])

    print("1. Auditing Canonical Paths...")
    for p in expected_paths:
        if not os.path.exists(p):
            print(f" [DRIFT] Manifest requires `{p}` but path is physically missing.")
            drift += 1

    print("2. Auditing for Floating/Undocumented Roots...")
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
                if d == ".DS_Store" or d == "__pycache__":
                    continue
                path = f"{domain}/{d}"
                # For example, apps/aiyou_stack. If no expected path starts with apps/aiyou_stack, and apps/aiyou_stack doesn't start with expected...
                is_valid = False
                for ep in expected_paths:
                    if ep == path or ep.startswith(path + "/") or path.startswith(ep + "/"):
                        is_valid = True
                        break
                if not is_valid and os.path.isdir(path):
                    print(f" [DRIFT] Undocumented floating folder found: `{path}`")
                    drift += 1

    print("3. Auditing Nested Git Roots...")
    # we can use find across domains
    search_dirs = " ".join([d for d in domains if os.path.exists(d)])
    nested_git = os.popen(f"find {search_dirs} -mindepth 2 -type d -name '.git' 2>/dev/null").read().strip()
    if nested_git:
        lines = nested_git.split("\n")
        print(f" [DRIFT] Found {len(lines)} nested `.git` folders in live trees.")
        for l in lines[:5]:
            print(f"   -> {l}")
        drift += len(lines)

    result = "\nSTAGE_3_PASS" if drift == 0 else f"\nSTAGE_3_FAIL (drift count: {drift})"
    print(result)
    if drift == 0:
        print("0 drift items found. Manifest truth perfectly aligns with physical workspace layout.")


if __name__ == "__main__":
    check_stage_3()
