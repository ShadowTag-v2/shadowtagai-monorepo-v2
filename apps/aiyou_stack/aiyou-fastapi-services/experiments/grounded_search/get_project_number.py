import google.auth
import requests
from google.auth.transport.requests import Request


def get_project_number(project_id):
    credentials, project = google.auth.default()
    if not credentials.valid:
        credentials.refresh(Request())

    headers = {"Authorization": f"Bearer {credentials.token}"}
    url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("projectNumber")
    else:
        print(f"Error getting project number: {response.status_code} {response.text}")
        return None


if __name__ == "__main__":
    project_id = "acquired-jet-478701-b3"
    number = get_project_number(project_id)
    if number:
        print(f"Project Number: {number}")
    else:
        print("Failed to get project number.")
