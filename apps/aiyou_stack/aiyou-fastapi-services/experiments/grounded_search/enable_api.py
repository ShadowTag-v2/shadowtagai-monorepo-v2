import google.auth
import requests
from google.auth.transport.requests import Request


def enable_api(project_id, service_name):
    credentials, project = google.auth.default()
    if not credentials.valid:
        credentials.refresh(Request())

    headers = {"Authorization": f"Bearer {credentials.token}", "Content-Type": "application/json"}
    # Service Usage API to enable service
    url = f"https://serviceusage.googleapis.com/v1/projects/{project_id}/services/{service_name}:enable"

    print(f"Enabling {service_name} for {project_id}...")
    response = requests.post(url, headers=headers)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Successfully enabled {service_name}")
        return True
    else:
        print(f"Error enabling service: {response.status_code} {response.text}")
        # If 403, it might be that Service Usage API itself is not enabled or permissions are missing.
        return False


if __name__ == "__main__":
    project_id = "acquired-jet-478701-b3"
    enable_api(project_id, "generativelanguage.googleapis.com")
