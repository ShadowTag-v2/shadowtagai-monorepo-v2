import time

import jwt
import requests


def get_installation_token(app_id, key_path, target_login):
  with open(key_path) as f:
    private_key = f.read()

  payload = {
    "iat": int(time.time()),
    "exp": int(time.time()) + (10 * 60),
    "iss": app_id,
  }
  encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

  headers = {
    "Authorization": f"Bearer {encoded_jwt}",
    "Accept": "application/vnd.github.v3+json",
  }

  resp = requests.get(
    "https://api.github.com/app/installations", headers=headers, timeout=30
  )
  if resp.status_code != 200:
    return None

  installations = resp.json()
  inst_id = None
  for inst in installations:
    if inst["account"]["login"].lower() == target_login.lower():
      inst_id = inst["id"]
      break

  if not inst_id and installations:
    inst_id = installations[0]["id"]

  if not inst_id:
    return None

  url = f"https://api.github.com/app/installations/{inst_id}/access_tokens"
  res = requests.post(url, headers=headers, timeout=30)
  if res.status_code != 201:
    return None

  return res.json()["token"]


def delete_repo(token, owner, repo) -> None:
  headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
  }
  url = f"https://api.github.com/repos/{owner}/{repo}"
  res = requests.delete(url, headers=headers, timeout=30)
  if res.status_code in {204, 404}:
    pass
  else:
    pass


if __name__ == "__main__":
  APP_ID = "3018200"
  KEY_PATH = "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-13.private-key.pem"

  repos_to_delete = [
    "ShadowTag-v2-sops",
    "ShadowTag-v2-ml",
    "ShadowTag-v2-data",
    "ShadowTag-v2-risk",
    "ShadowTag-v2-security",
    "ShadowTag-v2-ci",
    "ShadowTag-v2-infra",
    "ShadowTag-v2-backend",
    "ShadowTag-v2-frontend",
    "ShadowTag-v2",
    "ShadowTag-v2-exec",
    "ShadowTag-v2-policy",
  ]

  token = get_installation_token(APP_ID, KEY_PATH, "ShadowTag-v2")
  if token:
    for repo in repos_to_delete:
      delete_repo(token, "ShadowTag-v2", repo)
  else:
    pass
