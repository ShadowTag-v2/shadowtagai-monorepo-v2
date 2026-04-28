# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json

POLICY_FILE = "iam_policy.json"
NEW_POLICY_FILE = "iam_policy_updated.json"
USER_EMAIL = "user:redacted@shadowtag-v4.local"
SA_EMAIL = "serviceAccount:redacted@shadowtag-v4.local"

USER_ROLES = [
    "roles/cloudbuild.builds.editor",
    "roles/storage.admin",
    "roles/artifactregistry.admin",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
]

SA_ROLES = [
    "roles/run.developer",
    "roles/artifactregistry.reader",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/managedkafka.client",
]


def update_binding(bindings, role, member):
    # Find existing binding
    binding = next((b for b in bindings if b["role"] == role and "condition" not in b), None)
    if binding:
        if member not in binding["members"]:
            binding["members"].append(member)
            print(f"Added {member} to existing {role}")
    else:
        bindings.append({"role": role, "members": [member]})
        print(f"Created new binding for {role} with {member}")


def update_policy():
    try:
        with open(POLICY_FILE) as f:
            policy = json.load(f)
    except FileNotFoundError:
        print(f"Error: {POLICY_FILE} not found.")
        return

    bindings = policy.get("bindings", [])

    for role in USER_ROLES:
        update_binding(bindings, role, USER_EMAIL)

    for role in SA_ROLES:
        update_binding(bindings, role, SA_EMAIL)

    policy["bindings"] = bindings

    with open(NEW_POLICY_FILE, "w") as f:
        json.dump(policy, f, indent=2)
    print(f"Successfully wrote updated policy to {NEW_POLICY_FILE}")


if __name__ == "__main__":
    update_policy()
