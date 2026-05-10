# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys

from github import Auth, GithubIntegration

APP_ID = "3018200"
PEM_PATH = os.path.expanduser(
  "~/.ssh/antigravity-shadowtag-manager.2026-03-05.private-key.pem"
)

try:
  with open(PEM_PATH) as f:
    private_key = f.read()
except Exception as e:
  print(f"Error reading PEM: {e}", file=sys.stderr)
  sys.exit(1)

# Authenticate as App Integration
app_auth = Auth.AppAuth(app_id=APP_ID, private_key=private_key)
integration = GithubIntegration(auth=app_auth)

inst_id = None
for inst in integration.get_installations():
  if inst.account.login == "ShadowTag-v2":
    inst_id = inst.id
    break

if not inst_id:
  print(
    "Error: Could not find matching installation ID for ShadowTag-v2",
    file=sys.stderr,
  )
  sys.exit(1)

# ONLY output the raw token to STDOUT so bash can capture it cleanly in $GITHUB_TOKEN
token = integration.get_access_token(
  inst_id,
  permissions={"contents": "write", "pull_requests": "write", "metadata": "read"},
).token
print(token, end="")
