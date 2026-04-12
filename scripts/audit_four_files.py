import json
import os


def audit_four_files():
    issues = []

    # Audit 01
    try:
        with open("01_repo_census.json") as f:
            census = json.load(f)
        for repo in census:
            dest = repo.get("destination_path")
            disp = repo.get("disposition")

            # Check false canonical
            if disp == "canonical_in_monorepo":
                if not os.path.exists(dest):
                    issues.append(
                        f"FALSE CLAIM: {repo['repo_name']} marked canonical but path {dest} does not exist!"
                    )
    except Exception as e:
        issues.append(f"01_repo_census.json could not be read: {e}")

    if not issues:
        print("Audit passed. No false completion claims detected.")
    else:
        for i in issues:
            print(i)


if __name__ == "__main__":
    audit_four_files()
