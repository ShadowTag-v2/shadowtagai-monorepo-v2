import os
import sys

from github import Auth, GithubIntegration

APP_ID = "3018200"
PEM_PATH = os.path.expanduser("~/.ssh/antigravity-shadowtag-manager.2026-03-05.private-key.pem")

try:
    with open(PEM_PATH) as f:
        private_key = f.read()
except Exception as e:
    print(f"Error reading private key: {e}")
    sys.exit(1)

app_auth = Auth.AppAuth(app_id=APP_ID, private_key=private_key)
integration = GithubIntegration(auth=app_auth)

inst_id = None
try:
    installations = integration.get_installations()
    for inst in installations:
        print(f"Found installation for: {inst.account.login}")
        if inst.account.login == "ShadowTag-v2":
            inst_id = inst.id
            break
except Exception as e:
    print(f"Error fetching installations: {e}")

if not inst_id:
    print("Could not find installation ID for ShadowTag-v2")
    sys.exit(1)

try:
    token = integration.get_access_token(inst_id).token
    print(f"Successfully generated token. Length: {len(token)}")
except Exception as e:
    print(f"Error fetching token for installation {inst_id}: {e}")
    sys.exit(1)
