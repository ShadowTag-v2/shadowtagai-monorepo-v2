import argparse
import datetime
import json
import os

BEADS_FILE = ".beads/issues.jsonl"


def ensure_beads_dir():
    if not os.path.exists(".beads"):
        os.makedirs(".beads")


def load_issues():
    ensure_beads_dir()
    issues = []
    if os.path.exists(BEADS_FILE):
        with open(BEADS_FILE) as f:
            for line in f:
                if line.strip():
                    issues.append(json.loads(line))
    return issues


def save_issues(issues):
    ensure_beads_dir()
    with open(BEADS_FILE, "w") as f:
        for issue in issues:
            f.write(json.dumps(issue) + "\n")


def create_issue(title, description, labels):
    issues = load_issues()
    new_id = f"bd-{len(issues) + 1}"
    issue = {
        "id": new_id,
        "title": title,
        "description": description,
        "status": "open",
        "labels": labels.split(",") if labels else [],
        "created_at": datetime.datetime.now().isoformat(),
        "notes": [],
    }
    issues.append(issue)
    save_issues(issues)
    print(json.dumps(issue, indent=2))


def list_issues(status=None):
    issues = load_issues()
    for issue in issues:
        if status and issue["status"] != status:
            continue
        print(json.dumps(issue))


def update_issue(issue_id, status=None, note=None):
    issues = load_issues()
    updated = False
    for issue in issues:
        if issue["id"] == issue_id:
            if status:
                issue["status"] = status
            if note:
                issue["notes"].append(
                    {"timestamp": datetime.datetime.now().isoformat(), "text": note}
                )
            updated = True
            print(json.dumps(issue, indent=2))
            break
    if updated:
        save_issues(issues)
    else:
        print(f"Issue {issue_id} not found.")


def main():
    parser = argparse.ArgumentParser(description="Beads (bd) Issue Tracker")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("title")
    create_parser.add_argument("--desc", default="")
    create_parser.add_argument("--labels", default="")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--status")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("id")
    update_parser.add_argument("--status")
    update_parser.add_argument("--note")

    args = parser.parse_args()

    if args.command == "create":
        create_issue(args.title, args.desc, args.labels)
    elif args.command == "list":
        list_issues(args.status)
    elif args.command == "update":
        update_issue(args.id, args.status, args.note)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
