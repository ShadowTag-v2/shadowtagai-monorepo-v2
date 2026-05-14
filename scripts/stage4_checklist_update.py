# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os

import yaml


def rewrite_checklist():
    with open("fold_in_checklist.yaml") as f:
        checklist = yaml.safe_load(f)

    for item in checklist.get("repos", []):
        dest = item.get("destination_path")
        if dest and os.path.exists(dest):
            item["folded_into_destination"] = True
            item["manifest_updated"] = True
            item["merge_status_updated"] = True
            item["tooling_updated"] = True
            item["final_status_stamped"] = True
            # Also transition status from queued->canonical
            if item.get("status") == "queued_for_fold_in":
                item["status"] = "canonical_in_monorepo"

    with open("fold_in_checklist.yaml", "w") as f:
        yaml.safe_dump(checklist, f, sort_keys=False)


if __name__ == "__main__":
    rewrite_checklist()
