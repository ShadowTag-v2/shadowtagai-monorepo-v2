import sys
import os
import json
import requests


def get_linear_token():
    token = os.environ.get("LINEAR_API_KEY")
    if not token:
        try:
            with open(".env") as f:
                for line in f:
                    if line.startswith("LINEAR_API_KEY="):
                        return line.strip().split("=", 1)[1].strip("\"'")
        except FileNotFoundError:
            pass
    return token


def linear_graphql(query, variables=None):
    token = get_linear_token()
    if not token:
        print("ERROR: LINEAR_API_KEY environment variable not found.")
        sys.exit(1)

    headers = {"Authorization": token, "Content-Type": "application/json"}

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    try:
        response = requests.post("https://api.linear.app/graphql", headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        if "errors" in data:
            print(f"LINEAR GRAPHQL ERRORS: {json.dumps(data['errors'], indent=2)}")
            sys.exit(1)

        return data["data"]
    except Exception as e:
        print(f"API Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 my_linear.py --action <action> [options]")
        sys.exit(1)

    action = sys.argv[1]

    if action == "--list_issues":
        # python3 my_linear.py --list_issues
        query = """
        query {
          issues(first: 10, filter: { state: { type: { neq: "completed" } } }) {
            nodes {
              id
              identifier
              title
              state { name }
            }
          }
        }
        """
        data = linear_graphql(query)
        issues = data.get("issues", {}).get("nodes", [])
        print(json.dumps(issues, indent=2))

    elif action == "--create_issue":
        # python3 my_linear.py --create_issue <team_id> <title>
        if len(sys.argv) < 4:
            print("Missing team_id or title")
            sys.exit(1)
        team_id = sys.argv[2]
        title = sys.argv[3]

        mutation = """
        mutation CreateIssue($title: String!, $teamId: String!) {
          issueCreate(input: { title: $title, teamId: $teamId }) {
            success
            issue {
              id
              identifier
              title
            }
          }
        }
        """
        variables = {"title": title, "teamId": team_id}
        data = linear_graphql(mutation, variables)
        success = data.get("issueCreate", {}).get("success", False)

        if success:
            issue = data["issueCreate"]["issue"]
            print(f"SUCCESS: Created issue {issue['identifier']} - {issue['title']}")
        else:
            print("ERROR: Failed to create issue.")

    else:
        print(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
