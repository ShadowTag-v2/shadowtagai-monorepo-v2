import urllib.request
import google.auth
from google.auth.transport.requests import Request

creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
creds.refresh(Request())
req = urllib.request.Request("https://jules.googleapis.com/v1alpha/sources", headers={
    "Authorization": f"Bearer {creds.token}",
    "x-goog-user-project": "shadowtag-omega-v4"
})
try:
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode())
except Exception as e:
    print(e)
    if hasattr(e, 'read'):
        print(e.read().decode())
